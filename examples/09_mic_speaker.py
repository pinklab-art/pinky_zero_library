"""Mic / Speaker - 톤/삑 재생, 입력 레벨, 녹음→PC저장→로봇재생 왕복.

로봇 오디오(googlevoicehat 오버레이) 활성 필요.
"""
import time

import pinkylib
from pinkylib import Mic, Speaker

HOST = "192.168.7.1"        # 로봇 주소. 로봇 AP(pinky_zxxxx)에 붙었으면 이대로,
                            # 공유기를 거쳐 붙으면 로봇 IP 로 바꾼다

pinkylib.connect(HOST)
spk, mic = Speaker(), Mic()

print("삑 + 440Hz 톤")
spk.beep()
time.sleep(0.3)
spk.tone(440, 0.5, volume=0.3)

print("입력 레벨:", mic.level(0.3))        # 0.0~1.0 RMS

print("2초 녹음 → rec.wav 저장")
mic.record(2.0, "rec.wav")

print("녹음한 소리 로봇에서 재생")
spk.play("rec.wav")
print("완료")

pinkylib.disconnect()   # 로봇을 코딩모드에서 내보낸다.
                        # 안 부르면 이 프로그램이 살아있는 동안 로봇 화면이
                        # 코딩모드에 묶여 있고, 로봇 3번 버튼도 안 먹는다.
