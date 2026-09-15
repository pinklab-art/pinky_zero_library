"""Camera - 로봇 카메라 영상 받기.

read() = JPEG 바이트,  read_array() = OpenCV BGR ndarray (cv2 필요)
"""
import time
from ._client import client, SensorOffError, _off_msg


class Camera:
    def __init__(self, fps=15):
        self.fps = fps
        self._started = False

    def start(self, fps=None):
        """카메라 스트림 구독 시작. 끊겼다 다시 붙어도 자동으로 다시 신청한다."""
        self._fps_now = fps or self.fps
        client().call("camera.start", fps=self._fps_now)
        self._started = True
        client()._cam_fps = self._fps_now

    def stop(self):
        self._started = False
        client()._cam_fps = None      # 먼저 지운다 — 끄는 도중 재연결돼도 다시 켜지지 않게
        client()._frame = None        # 끈 뒤 read() 는 마지막 그림 대신 '카메라 꺼짐' 에러
        client().call("camera.stop")

    def read(self, timeout=2.0):
        """최신 JPEG 바이트. timeout 안에 새 프레임이 안 오면 None.

        오래된 프레임은 돌려주지 않는다. 끊겼다 다시 붙거나 영상이 멈추면 마지막으로
        받은 그림이 그대로 남는데, 예전엔 그걸 계속 돌려줘서 에러도 None 도 없이
        화면이 멈춘 것처럼 보였다(2026-09-15 실측). 그 그림으로 계속 계산하게 된다.
        """
        if not self._started and client().latest_frame() is None:
            raise SensorOffError(_off_msg("camera"))
        max_age = self._max_age()
        t = time.time()
        while True:
            f = client().latest_frame()
            if f is not None and time.time() - client()._frame_ts <= max_age:
                return f
            if time.time() - t >= timeout:
                return None
            time.sleep(0.01)

    def _max_age(self):
        """이보다 오래된 프레임은 낡은 것으로 본다. 받는 간격의 3배, 최소 1초."""
        fps = getattr(self, "_fps_now", None) or self.fps
        return max(1.0, 3.0 / fps)

    def read_array(self, timeout=2.0):
        """최신 프레임을 OpenCV BGR ndarray로 (cv2 필요)."""
        import numpy as np
        import cv2
        jpg = self.read(timeout)
        if jpg is None:
            return None
        return cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_COLOR)

    def snapshot(self):
        """사진 한 장 찍기(스트림 구독 없이)."""
        client().call("camera.snapshot")
        self._started = True
        return self.read()

    def set_callback(self, fn):
        """프레임마다 fn(jpeg_bytes) 호출."""
        client()._cam_cb = fn

    def close(self):
        try: self.stop()
        except Exception: pass
