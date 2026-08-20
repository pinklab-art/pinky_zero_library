"""Mic - 로봇 I2S 마이크(ICS-43434) 원격 녹음.

마이크는 로봇 Pi(ALSA)에 붙어있어 서버가 arecord로 캡처한 WAV를 보내준다.
백업 온보드판(local_backup_pinkylib)과 같은 API.
"""
import base64

from ._client import client


class Mic:
    def record(self, seconds, path):
        """seconds초 녹음 → 로컬(PC) path 에 WAV 저장, 경로 반환."""
        data = self.record_bytes(seconds)
        with open(path, "wb") as f:
            f.write(data)
        return path

    def record_bytes(self, seconds):
        """녹음 결과 WAV 바이트 반환."""
        r = client().call("mic.record", timeout=float(seconds) + 8, seconds=float(seconds))
        return base64.b64decode(r["wav"])

    def level(self, seconds=0.3):
        """짧게 녹음해 입력 레벨(0.0~1.0 RMS) 반환 - VU/소리 트리거용."""
        return client().call("mic.level", timeout=float(seconds) + 5, seconds=float(seconds))

    def set_gain(self, gain):
        """마이크 게인 설정 (0~100, 값이 곧 배율). 녹음이 작으면 올린다.

        ICS-43434 는 하드웨어 게인이 없어(믹서 컨트롤 자체가 없음) 서버가
        샘플에 직접 곱한다. 기본 25.
        """
        return client().call("mic.set_gain", gain=float(gain))

    def get_gain(self):
        """현재 마이크 게인 (0~100)."""
        return client().call("mic.get_gain")

    def close(self):
        pass
