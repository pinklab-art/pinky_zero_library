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
        """카메라 스트림 구독 시작."""
        client().call("camera.start", fps=fps or self.fps)
        self._started = True

    def stop(self):
        self._started = False
        client().call("camera.stop")

    def read(self, timeout=2.0):
        """최신 JPEG 바이트. 아직 프레임이 없으면 None."""
        if not self._started and client().latest_frame() is None:
            raise SensorOffError(_off_msg("camera"))
        t = time.time()
        while time.time() - t < timeout:
            f = client().latest_frame()
            if f is not None:
                return f
            time.sleep(0.01)
        return client().latest_frame()

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
