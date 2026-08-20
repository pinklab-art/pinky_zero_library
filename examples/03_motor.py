"""Motor - 전진/제자리회전 + 엔코더/회전수/실측RPM.

⚠️ 실제 바퀴가 돕니다. 반드시 바퀴를 띄우고 테스트하세요.
엔코더는 Motor 클래스에 포함됨 (get_encoder / get_revolutions).
"""
import time

import pinkylib
from pinkylib import Motor

HOST = "192.168.7.1"        # 로봇 주소. 로봇 AP(pinky_zxxxx)에 붙었으면 이대로,
                            # 공유기를 거쳐 붙으면 로봇 IP 로 바꾼다

pinkylib.connect(HOST)
m = Motor()                     # 보드·모터 활성화는 Motor 가 알아서 한다
try:
    print("전진 (30 RPM, 1.5s)")
    m.set_rpm(30, 30)
    time.sleep(1.5)

    print("제자리 회전 (1.0s)")
    m.set_rpm(-30, 30)
    time.sleep(1.0)

    m.stop()
    print("엔코더:", m.get_encoder())
    print("회전수:", m.get_revolutions())
    print("실측 RPM:", m.get_rpm())
finally:
    m.close()                   # 정지 + disable (안전)
    print("정지")

pinkylib.disconnect()   # 로봇을 코딩모드에서 내보낸다.
                        # 안 부르면 이 프로그램이 살아있는 동안 로봇 화면이
                        # 코딩모드에 묶여 있고, 로봇 3번 버튼도 안 먹는다.
