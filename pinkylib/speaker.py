"""Speaker - 로봇 I2S 앰프(MAX98357A) 원격 재생.

앰프는 로봇 Pi(ALSA)에 붙어있어 WAV/톤을 서버로 보내 재생한다.
백업 온보드판(local_backup_pinkylib)과 같은 API.
"""

from ._client import BIN_AUDIO, client


class Speaker:
    def play(self, path):
        """PC의 WAV 파일을 로봇에서 재생(블로킹). 볼륨은 set_volume 값을 쓴다."""
        with open(path, "rb") as f:
            data = f.read()
        # 이진으로 보낸다 — WAV 는 몇 MB 가 되기도 해서 base64 의 33% 가 그대로 지연이다
        client().send_binary(BIN_AUDIO, data, timeout=60)

    def tone(self, freq=440, seconds=1.0, volume=None):
        """사인 톤 재생 (freq Hz, volume 0~100). 생략하면 set_volume 값."""
        kw = {} if volume is None else {"volume": float(volume)}
        client().call("speaker.tone", timeout=float(seconds) + 8,
                      freq=float(freq), seconds=float(seconds), **kw)

    def beep(self, freq=880, seconds=0.15, volume=None):
        """짧은 삑 소리 (volume 0~100). 생략하면 set_volume 값."""
        kw = {} if volume is None else {"volume": float(volume)}
        client().call("speaker.beep", timeout=float(seconds) + 8,
                      freq=float(freq), seconds=float(seconds), **kw)

    def stop(self):
        """재생 중인 소리를 끊는다. 끊은 게 있으면 True.

        play/tone/beep 은 끝날 때까지 기다리므로, 멈추려면 다른 곳에서 불러야 한다
        (예: 대시보드의 정지 버튼, 또는 별도 스레드).
        """
        return client().call("speaker.stop")

    def is_playing(self):
        """지금 소리가 나고 있는가."""
        return client().call("speaker.is_playing")

    def set_volume(self, volume):
        """스피커 볼륨 설정 (0~100). play/tone/beep 에 모두 적용된다.

        googlevoicehat 은 믹서 컨트롤이 없어 서버가 샘플에 직접 곱한다. 기본 30.
        """
        return client().call("speaker.set_volume", volume=float(volume))

    def get_volume(self):
        """현재 스피커 볼륨 (0~100)."""
        return client().call("speaker.get_volume")

    def close(self):
        # 프로그램이 끝날 때 소리가 남아 계속 나는 걸 막는다.
        # 이미 연결이 끊겼으면 멈출 것도 없으니 조용히 넘어간다.
        try:
            self.stop()
        except Exception:
            pass
