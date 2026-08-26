"""WebSocket 연결 싱글턴 - 모든 pinkyzero 클래스가 공유.

안정성:
  - 자동 재연결(백오프) + 하트비트(ping)로 끊김/반쪽연결 감지 → 재접속
  - 재접속 시 센서 스트림 자동 재구독
  - 끊긴 동안의 요청은 재연결을 3초까지 기다린 뒤 에러(무한 대기 없음).
    센서 읽기도 마찬가지 — 낡은 캐시를 현재값처럼 돌려주지 않는다.

사용:
    import pinkyzero
    pinkyzero.connect()          # 기본 192.168.7.1 (로봇 AP)
    from pinkyzero import Battery
    print(Battery().get_voltage())
"""
import itertools
import json
import os
import sys
import threading
import time

import websocket  # pip install websocket-client

# 로봇 AP(pinky_z####, 비밀번호 없음)에 붙었을 때의 주소.
# 공유기를 거쳐 붙으면 connect("주소") 로 로봇 IP 를 넘긴다.
DEFAULT_HOST = "192.168.7.1"

# --- 이진 프레임 규격 (server/README.md 와 같은 표) ---
# 머리 5바이트 = 종류(1) + 요청 id(uint32 LE, 0 이면 응답 안 받음)
# 큰 데이터를 base64 로 JSON 에 싣지 않기 위한 것이다 — base64 는 33% 를 더 보내고
# 양쪽에서 인코딩·디코딩 CPU 를 쓴다(LCD 한 장 136KB -> 182KB).
BIN_VERSION = 2
BIN_CAMERA, BIN_LCD, BIN_AUDIO, BIN_ECHO = 0x01, 0x02, 0x03, 0x04
BIN_HDR = 5


def bin_frame(tag, rid=0, body=b""):
    return bytes([tag]) + int(rid).to_bytes(4, "little") + bytes(body)


class SensorOffError(RuntimeError):
    """센서 측정이 꺼져 있는데 값을 읽으려 할 때 발생.

    부팅 시 꺼져 있는 것은 IMU · 카메라 · 모터다. 보드(배터리 · IR · 버튼)와 터치는
    로봇 화면(pinky-lcd-ui)이 접속하면서 켜므로 보통 이미 켜져 있다.
    안내 메시지대로 해당 센서를 먼저 켜면 된다.
    (조용히 None 을 돌려주면 왜 안 되는지 알기 어려워서, 대신 이 에러로 알려준다.)
    """


# 센서 그룹별 "이걸 먼저 켜세요" 안내
_OFF_HINT = {
    # 보드 그룹은 로봇이 부팅부터 켜둔다. 여기 걸리면 옛 서버이거나 시리얼이
    # 끊긴 것이라, 학생이 켤 수 있는 게 없다 — 로봇을 다시 켜라고 안내한다.
    "pico": "로봇을 껐다 켜 보세요 (배터리·바닥/거리 IR·모션·버튼·엔코더)",
    "imu": "IMU().enable()   또는  pinkyzero.enable_imu()",
    "touch": "LCD().enable()   또는  pinkyzero.enable_touch()",
    "camera": "Camera().start()   (카메라 스트림 시작)",
}


# 그룹별 주어(안내문 첫 단어). 없으면 "센서".
_OFF_SUBJECT = {"camera": "카메라"}


def _off_msg(group):
    subj = _OFF_SUBJECT.get(group, "센서")
    return (f"{subj}가 꺼져 있어 값을 읽을 수 없어요.\n"
            f"   먼저 이걸 실행하세요 →  {_OFF_HINT.get(group, group)}")


class _Client:
    def __init__(self):
        self.ws = None
        self.url = None
        self._ids = itertools.count(1)
        self._pending = {}
        self._send_lock = threading.Lock()
        self._status = {}
        self._status_ts = 0.0
        self._frame = None
        self._frame_ts = 0.0
        self._cam_cb = None
        self._stream_hz = 30
        self._want = False
        self._connected = threading.Event()
        self._kicked = None       # 서버가 내보낸 이유. 있으면 자동 재연결을 하지 않는다
        self._ever = False        # 한 번이라도 붙은 적 있는지(에러 문구 구분용)

    # --- 연결 ---
    def connect(self, host=DEFAULT_HOST, port=8765, timeout=5, stream_hz=30):
        """로봇에 접속. 붙었으면 True.

        시간 안에 못 붙어도 예외는 내지 않는다 — 주피터에서 셀을 죽이는 것보다
        경고를 보여주고 뒤에서 계속 다시 붙는 편이 낫다(로봇을 그제서야 켜는 일이 잦다).
        대신 조용히 넘어가지는 않는다. 예전엔 아무 말이 없어서, 다음 셀에서
        "서버 연결 끊김" 이 나올 때까지 못 붙은 줄을 몰랐다.
        """
        self.url = f"ws://{host}:{port}"
        self._stream_hz = stream_hz
        self._kicked = None       # 다시 붙는 것이므로 지난 강제종료 기록은 지운다
        self._want = True
        threading.Thread(target=self._supervisor, args=(timeout,), daemon=True).start()
        ok = self._connected.wait(timeout + 1)   # 최초 연결까지 대기
        if not ok:
            print(
                f"\u26a0 로봇에 접속하지 못했습니다 ({self.url}, {timeout + 1:.0f}초 기다림).\n"
                "   \u00b7 로봇 AP(pinky_z####)에 연결돼 있는지 확인하세요.\n"
                '   \u00b7 공유기를 거쳐 쓴다면 connect("로봇IP") 로 주소를 넘기세요.\n'
                "   \u00b7 로봇 전원이 켜져 있고 부팅이 끝났는지(표정 화면) 확인하세요.\n"
                "   뒤에서 계속 다시 시도합니다 — 로봇을 켜면 알아서 붙습니다.\n"
                "   pinkyzero.client().connected 로 지금 상태를 볼 수 있습니다.",
                file=sys.stderr)
        return ok

    @property
    def connected(self):
        return self._connected.is_set()

    def disconnect(self):
        self._want = False
        try:
            self.ws.close()
        except Exception:
            pass

    def _ensure(self):
        if not self._want:
            if self._kicked:
                raise RuntimeError(
                    f"로봇과의 연결이 끊겼습니다 ({self._kicked}). "
                    f"계속 쓰려면 pinkyzero.connect() 를 다시 호출하세요.")
            host = os.environ.get("PINKY_HOST")
            if host:
                self.connect(host)
            else:
                raise RuntimeError(
                    f"연결 안 됨. pinkyzero.connect() 를 먼저 호출하세요 "
                    f"(주소 생략 시 {DEFAULT_HOST}).")

    def _conn_error(self, tail="."):
        """연결 에러 문구. 한 번도 못 붙은 경우와 붙었다 끊긴 경우를 나눈다 —
        처음부터 못 붙었는데 "끊김" 이라고 하면 원인을 엉뚱한 데서 찾게 된다."""
        if self._ever:
            return ConnectionError("서버 연결 끊김(재연결 중)" + tail)
        return ConnectionError(
            f"로봇에 아직 접속하지 못했습니다 ({self.url}) — 뒤에서 다시 시도 중" + tail)

    # --- 감독 루프: 끊기면 자동 재연결 ---
    def _supervisor(self, timeout):
        backoff = 0.5
        while self._want:
            try:
                ws = websocket.create_connection(self.url, timeout=timeout,
                                                 max_size=None, enable_multithread=True)
                ws.settimeout(5)
                self.ws = ws
                self._ever = True
                self._connected.set()
                backoff = 0.5
                # 리더가 아직 안 돌아 응답을 못 받으므로 fire-and-forget 로 보낸다
                # (응답 대기하면 리더 시작 전까지 블랙아웃 → 첫 명령 타임아웃)
                # hello: 로봇이 "PC 가 코딩 중" 을 알고 LCD 를 코딩 모드로 넘긴다.
                # 재연결할 때마다 다시 알려야 하므로 여기서 보낸다.
                init = [("hello", {"role": "coding", "binv": BIN_VERSION})]
                if self._stream_hz:
                    init.append(("stream.on", {"hz": self._stream_hz}))
                for cmd, args in init:
                    try:
                        with self._send_lock:
                            ws.send(json.dumps({"id": next(self._ids),
                                                "cmd": cmd, "args": args}))
                    except Exception:
                        pass
                self._reader()                      # 끊길 때까지 블록
            except Exception:
                pass
            # --- 끊김 처리 ---
            self._connected.clear()
            try:
                self.ws.close()
            except Exception:
                pass
            self.ws = None
            for rid, (ev, box) in list(self._pending.items()):
                box.append({"ok": False, "error": "disconnected"}); ev.set()
            self._pending.clear()
            if not self._want:
                break
            time.sleep(backoff)
            backoff = min(5.0, backoff * 1.7)

    def _reader(self):
        while self._want:
            try:
                msg = self.ws.recv()
            except websocket.WebSocketTimeoutException:
                # 무트래픽 구간: ping으로 살아있는지 확인(끊겼으면 예외 → 재연결)
                self.ws.ping()
                continue
            if msg is None or msg == "":
                raise ConnectionError("closed")
            if isinstance(msg, (bytes, bytearray)):
                self._on_binary(bytes(msg))
                continue
            try:
                obj = json.loads(msg)
            except Exception:
                continue
            rid = obj.get("id")
            if rid in self._pending:
                ev, box = self._pending.pop(rid)
                box.append(obj); ev.set()
            elif obj.get("type") == "status":
                self._status = obj.get("data", {}); self._status_ts = time.time()
            elif obj.get("type") == "kicked":
                # 서버가 내보냈다. 소켓만 닫히면 감독 루프가 0.5초 뒤 되붙고
                # 로봇은 계속 코딩모드로 남는다(대시보드 ✕·LCD 나가기 버튼이 안 먹는 이유).
                # 그래서 재연결 의지(_want)까지 내려야 실제로 종료된다.
                self._kicked = obj.get("reason") or "로봇 쪽에서 종료 요청"
                self._want = False
                try:
                    self.ws.close()
                except Exception:
                    pass
                return

    def _on_binary(self, msg):
        """이진 프레임 수신. 머리 5바이트로 종류를 가른다.
        예전엔 이진이면 무조건 카메라였다 — 그래서 다른 용도를 쓸 수 없었다."""
        if len(msg) < BIN_HDR:
            return
        tag = msg[0]
        rid = int.from_bytes(msg[1:5], "little")
        body = msg[BIN_HDR:]
        if tag == BIN_CAMERA:
            self._frame = body
            self._frame_ts = time.time()
            if self._cam_cb:
                try:
                    self._cam_cb(body)
                except Exception:
                    pass
        elif tag == BIN_ECHO and rid in self._pending:
            # 회선 속도 측정. 내용은 버리고 길이만 쓴다.
            ev, box = self._pending.pop(rid)
            box.append({"ok": True, "result": len(body)}); ev.set()

    def send_binary(self, tag, body, timeout=10, wait=True):
        """이진 프레임 전송. 응답은 지금까지처럼 JSON 으로 온다(id 로 짝을 맞춘다).
        wait=False 면 id 0 으로 보내 서버가 응답을 안 만든다."""
        self._ensure()
        if not self._connected.wait(timeout):
            raise self._conn_error()
        rid = next(self._ids) if wait else 0
        ev = box = None
        if wait:
            ev = threading.Event(); box = []
            self._pending[rid] = (ev, box)
        try:
            with self._send_lock:
                self.ws.send_binary(bin_frame(tag, rid, body))
        except (websocket.WebSocketException, OSError) as e:
            self._pending.pop(rid, None)
            self._connected.clear()
            raise ConnectionError(str(e))
        if not wait:
            return None
        if not ev.wait(timeout):
            self._pending.pop(rid, None)
            raise TimeoutError(f"응답 없음: 이진 {tag}")
        r = box[0]
        if not r.get("ok"):
            raise RuntimeError(r.get("error", f"이진 {tag}"))
        return r.get("result")

    # --- 요청/응답 ---
    def _raw_call(self, cmd, timeout, **args):
        """연결돼 있다고 가정하고 즉시 전송(감독 루프 내부용)."""
        rid = next(self._ids)
        ev = threading.Event(); box = []
        self._pending[rid] = (ev, box)
        with self._send_lock:
            self.ws.send(json.dumps({"id": rid, "cmd": cmd, "args": args}))
        if not ev.wait(timeout):
            self._pending.pop(rid, None)
            raise TimeoutError(f"응답 없음: {cmd}")
        r = box[0]
        if not r.get("ok"):
            raise RuntimeError(r.get("error", cmd))
        return r.get("result")

    def call(self, cmd, timeout=3, **args):
        self._ensure()
        if not self._connected.wait(timeout):      # 재연결 중이면 잠깐 대기
            raise self._conn_error()
        try:
            return self._raw_call(cmd, timeout, **args)
        except (websocket.WebSocketException, OSError) as e:
            self._connected.clear()                # 전송 실패 → 감독 루프가 재연결
            raise ConnectionError(str(e))

    # --- 센서 캐시 ---
    def status(self, fresh=False, max_age=0.5):
        """센서 상태. 캐시가 낡았으면 서버에 다시 묻는다.

        끊겼으면 마지막 값을 주지 않고 에러를 낸다. 짧은 끊김은 call() 이 재연결을
        3초까지 기다려 흡수하므로, 여기까지 오는 건 그래도 못 붙은 경우뿐이다.
        그때 낡은 값을 현재값처럼 돌려주면 로봇이 꺼진 줄도 모르고 계속 돌게 된다.
        """
        self._ensure()
        if fresh or not self._status or (time.time() - self._status_ts) > max_age:
            try:
                return self.call("status.get")
            except Exception as e:
                age = time.time() - self._status_ts if self._status_ts else None
                raise self._conn_error(
                    (f" (마지막 값 {age:.1f}초 전)" if age else "")
                    + ".\n   pinkyzero.client().connected 으로 연결 상태 확인해보세요.") from e
        return self._status

    def require(self, group):
        """센서 그룹(pico/imu/touch)이 켜져 있으면 상태 dict 반환, 꺼져 있으면 친절한 에러.

        방금 켠 직후엔 스트림 캐시가 아직 옛 값(꺼짐)일 수 있어, 꺼진 것처럼 보이면
        서버에 한 번 더(fresh) 물어보고 그래도 꺼져 있을 때만 에러를 낸다(오탐 방지).
        """
        s = self.status()
        if not s.get("en_" + group):
            s = self.status(fresh=True)
            if not s.get("en_" + group):
                raise SensorOffError(_off_msg(group))
        return s

    def field(self, name, group):
        """require(group) 후 단일 필드 값 읽기."""
        return self.require(group).get(name)

    def latest_frame(self):
        return self._frame


_CLIENT = _Client()


def client():
    return _CLIENT


def connect(host=DEFAULT_HOST, port=8765, **kw):
    """로봇에 접속. host 를 생략하면 DEFAULT_HOST(로봇 AP 주소).

    못 붙으면 경고를 찍고 False 를 돌려준다(예외는 안 낸다).
    """
    return _CLIENT.connect(host, port, **kw)


def disconnect():
    """로봇 연결 끊기 — 로봇을 코딩모드에서 내보낸다.

    끊지 않고 노트북만 덮으면 로봇은 계속 코딩모드로 남아 LCD 를 안 되찾는다.
    주피터에서 다 쓰고 이걸 부르면 로봇이 자기 UI 로 돌아간다.
    다시 쓰려면 connect() 를 새로 부른다.
    """
    _CLIENT.disconnect()


# --- 센서 측정 켜기 ---
#
# 보드(Pico) 그룹 — 배터리·IR·모션·엔코더·버튼 — 은 켜고 끄는 함수가 없다.
# 로봇이 부팅부터 켜두고, 끌 방법도 두지 않는다. 껐을 때 아끼는 게 사실상 없는데
# (바닥 IR 발광부는 제어 핀 자체가 없어 계속 켜져 있다) 끄면 로봇의 물리 버튼이
# 죽어서 화면을 되찾을 수 없게 된다.
def enable_imu(on=True):
    """IMU(BNO055) 측정 on/off."""
    _CLIENT.call("imu.enable", on=bool(on))


def enable_touch(on=True):
    """터치(CST816) 측정 on/off."""
    _CLIENT.call("touch.enable", on=bool(on))


def enable_all(on=True):
    """IMU + 터치 한 번에. (보드 그룹은 로봇이 알아서 켜둔다)"""
    enable_imu(on); enable_touch(on)


def sensor_enabled():
    """현재 서버의 센서 측정 활성 상태 조회 → {'pico':bool, 'imu':bool, 'touch':bool}."""
    s = _CLIENT.status()
    return {"pico": bool(s.get("en_pico")),
            "imu": bool(s.get("en_imu")),
            "touch": bool(s.get("en_touch"))}
