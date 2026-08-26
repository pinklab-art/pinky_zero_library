"""LCD - 로봇 화면(ST7789) 원격 표시 + 터치(CST816) 읽기.

터치 패널은 물리적으로 LCD의 일부라 한 클래스로 묶었다.
  - 화면 표시: 서버가 Pi SPI0 로 직접 그린다(로봇 전원 ON 이어야 MCU가 SPI 양보).
  - 터치: 서버 status 스트림의 touch_* 필드를 읽는다. enable(True) 로 측정을 켜야 값이 옴.

    from pinkyzero import LCD
    lcd = LCD()
    lcd.fill(0, 0, 40)                 # 남색으로 채우기
    lcd.image("face.png")             # 파일/PIL/ndarray 를 화면에
    lcd.enable(True)                  # 터치 측정 ON
    print(lcd.wait_touch())           # 터치 대기 → {touch,x,y,gesture}
"""

from ._client import BIN_LCD, client

WIDTH, HEIGHT = 284, 240


class LCD:
    WIDTH = WIDTH
    HEIGHT = HEIGHT

    # ---------------- 터치 ----------------
    def enable(self, on=True):
        """터치 측정 on/off (서버 touch.enable). on 이어야 read_touch 값이 들어온다."""
        client().call("touch.enable", on=bool(on))

    def is_touch_enabled(self):
        """현재 터치 측정이 켜져 있는지."""
        return bool(client().status().get("en_touch"))

    def read_touch(self):
        """현재 터치 상태 dict {touch,x,y,gesture}. (측정이 꺼져 있으면 안내 에러)"""
        s = client().require("touch")
        return {"touch": s.get("touch"), "x": s.get("touch_x"),
                "y": s.get("touch_y"), "gesture": s.get("touch_gesture")}

    def touched(self):
        """지금 눌려있나 (bool)."""
        return bool(client().require("touch").get("touch"))

    def read_gesture(self):
        """현재 제스처 문자열(none/up/down/left/right/click/long/double)."""
        return client().require("touch").get("touch_gesture")

    def wait_gesture(self, timeout=10.0, poll=0.02):
        """다음 제스처(up/down/left/right/click/long/double)가 올 때까지 대기 → 반환.
        (측정 자동 ON. 서버가 순간 제스처를 래치해줘서 놓칠 확률이 낮다.)"""
        import time
        self.enable(True)
        last = "none"
        t0 = time.time()
        while time.time() - t0 < timeout:
            g = client().status().get("touch_gesture")   # 스트림 캐시(래치됨)
            if g and g != "none" and g != last:
                return g
            last = g
            time.sleep(poll)
        return None

    def wait_touch(self, timeout=10.0, poll=0.03):
        """터치가 눌릴 때까지 대기 → 그 상태(dict) 반환, 없으면 None. (측정 자동 ON)"""
        import time
        self.enable(True)
        t0 = time.time()
        while time.time() - t0 < timeout:
            s = client().status(fresh=True)
            if s.get("touch"):
                return {"touch": True, "x": s.get("touch_x"),
                        "y": s.get("touch_y"), "gesture": s.get("touch_gesture")}
            time.sleep(poll)
        return None

    # ---------------- 화면 ----------------
    def backlight(self, on=True):
        """백라이트 ON/OFF."""
        client().call("lcd.backlight", on=bool(on))

    def fill(self, r=0, g=0, b=0):
        """화면 전체를 (r,g,b)로 채움."""
        client().call("lcd.fill", r=int(r), g=int(g), b=int(b))

    def clear(self):
        """검게 지움."""
        self.fill(0, 0, 0)

    def off(self):
        """화면 지우고 백라이트 끄기 (종료 시 정리용).

        백라이트는 아무도 자동으로 되켜지 않는다. off() 뒤에는 화면이 계속
        캄캄하고, 로봇 3번 버튼으로 UI 를 되찾아도 그린 그림이 안 보인다.
        다시 켜려면 on() 을 부른다.
        """
        try:
            self.clear()
        except Exception:
            pass
        self.backlight(False)

    def on(self):
        """백라이트 켜기 (off() 를 되돌린다).

        내용은 마지막에 그린 것 그대로다 — off() 가 검게 지웠으니 화면은 검다.
        로봇 UI 로 돌아가려면 로봇 3번 버튼을 길게 누른다.
        """
        self.backlight(True)

    def image(self, img, x=0, y=0, w=None, h=None, is_bgr=False):
        """이미지를 화면(또는 (x,y) 영역)에 표시. img: 파일경로/PIL/ndarray(HxWx3).
        PC에서 RGB565 빅엔디안으로 변환 후 서버로 보내 블릿한다."""
        data, W, H = self._to_565be(img, w, h, is_bgr)
        if x + W > WIDTH or y + H > HEIGHT:
            raise ValueError(f"이미지({W}x{H})가 화면 범위를 벗어남 (at {x},{y})")
        # 이진으로 보낸다. base64 로 JSON 에 실으면 33% 를 더 보내고(136KB -> 182KB)
        # 양쪽에서 인코딩·디코딩 CPU 까지 쓴다 — 그림 전송이 화면 갱신 속도의 상한이다.
        head = b"".join(int(v).to_bytes(2, "little") for v in (x, y, W, H))
        client().send_binary(BIN_LCD, head + data, timeout=10)

    def _to_565be(self, img, w, h, is_bgr):
        import numpy as np
        tw = w or WIDTH
        th = h or HEIGHT
        arr = None
        try:
            from PIL import Image
            if isinstance(img, str):
                img = Image.open(img)
            if isinstance(img, Image.Image):
                img = img.convert("RGB")
                if img.size != (tw, th):
                    img = img.resize((tw, th))
                arr = np.asarray(img, dtype=np.uint16)
        except ImportError:
            if isinstance(img, str):
                raise RuntimeError("이미지 파일 로드에 pillow 필요")
        if arr is None:
            a = np.asarray(img)
            if is_bgr:
                a = a[:, :, ::-1]
            if a.shape[1] != tw or a.shape[0] != th:
                try:
                    import cv2
                    a = cv2.resize(a, (tw, th))
                except ImportError:
                    raise RuntimeError("ndarray 리사이즈에 opencv 필요(또는 미리 크기 맞추기)")
            arr = a[:, :, :3].astype(np.uint16)
        r = (arr[:, :, 0] >> 3) << 11
        g = (arr[:, :, 1] >> 2) << 5
        b = arr[:, :, 2] >> 3
        v = (r | g | b).astype(">u2")
        return v.tobytes(), arr.shape[1], arr.shape[0]

    def close(self):
        try:
            client().call("lcd.close")
        except Exception:
            pass
