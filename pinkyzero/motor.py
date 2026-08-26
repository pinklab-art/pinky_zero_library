"""Motor - 좌/우 바퀴 구동(목표 RPM) + 피드백.

안정성: set_rpm으로 0이 아닌 속도를 주면 keepalive 스레드가 그 명령을
주기적으로 재전송한다. 이렇게 하면 서버 워치독(명령 끊기면 자동정지)에
정상 주행이 걸리지 않고, WiFi가 끊기면 재전송이 실패 → 워치독이 안전하게 정지.

주의: 실제 바퀴가 돕니다. 테스트는 바퀴를 띄우고 하세요.
"""
import threading
import time

from ._client import client


class Motor:
    KEEPALIVE = 0.2       # 초. 서버 watchdog(0.7)보다 짧게.
    CPR = 28 * 120        # 엔코더 카운트/회전 (기어비 포함)

    def __init__(self, auto_enable=True):
        client().call("comm.start", on=True)
        self._last = (0, 0)
        self._ka_run = False
        self._ka = None
        if auto_enable:
            self.enable(True)

    def enable(self, on=True):
        client().call("motor.enable", on=bool(on))

    def set_rpm(self, left, right):
        """좌/우 목표 RPM (int16)."""
        left, right = int(left), int(right)
        self._last = (left, right)
        client().call("motor.set_rpm", l=left, r=right)
        if left or right:
            self._start_keepalive()
        else:
            self._stop_keepalive()

    def stop(self):
        self._last = (0, 0)
        self._stop_keepalive()
        client().call("motor.stop")

    # --- keepalive ---
    def _start_keepalive(self):
        if self._ka_run:
            return
        self._ka_run = True
        self._ka = threading.Thread(target=self._keepalive, daemon=True)
        self._ka.start()

    def _stop_keepalive(self):
        self._ka_run = False

    def _keepalive(self):
        while self._ka_run:
            time.sleep(self.KEEPALIVE)
            l, r = self._last
            if not (l or r):
                break
            try:
                client().call("motor.set_rpm", l=l, r=r, timeout=1)
            except Exception:
                pass   # 끊기면 재전송 실패 → 서버 워치독이 정지시킴

    # --- 피드백 (캐시) ---
    def get_rpm(self):
        st = client().status()
        return st.get("rpm_L"), st.get("rpm_R")

    def get_encoder(self):
        """(enc_L, enc_R) 누적 카운트."""
        st = client().status()
        return st.get("enc_L"), st.get("enc_R")

    def get_revolutions(self):
        """(회전수_L, 회전수_R) — 엔코더 카운트 / CPR."""
        l, r = self.get_encoder()
        return (l / self.CPR if l is not None else None,
                r / self.CPR if r is not None else None)

    def close(self):
        try:
            self.stop(); self.enable(False)
        except Exception:
            pass
