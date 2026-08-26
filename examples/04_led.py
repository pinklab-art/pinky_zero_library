"""LED - 고정색 / 깜빡임 / 숨쉬기(디밍) / 끄기."""
import time

import pinkyzero
from pinkyzero import LED

HOST = "192.168.7.1"        # 로봇 주소. 로봇 AP(pinky_zxxxx)에 붙었으면 이대로,
                            # 공유기를 거쳐 붙으면 로봇 IP 로 바꾼다

pinkyzero.connect(HOST)
led = LED()

print("고정색 (남색)")
led.set_color(0, 40, 60, bright=127)
time.sleep(1.2)

print("깜빡임 (빨강)")
led.blink(255, 0, 0, on_ms=200, off_ms=200)
time.sleep(2)

print("숨쉬기 (파랑)")
led.dimming(0, 0, 255, max_bright=200, cycle_ms=1500)
time.sleep(2.5)

led.off()
print("끄기")

pinkyzero.disconnect()   # 로봇을 코딩모드에서 내보낸다.
                        # 안 부르면 이 프로그램이 살아있는 동안 로봇 화면이
                        # 코딩모드에 묶여 있고, 로봇 3번 버튼도 안 먹는다.
