"""Touch - LCD 터치를 기다렸다가 LED+부저로 반응 (터치는 LCD 클래스에 포함).

로봇 전원 ON 필요. 터치 좌표/제스처도 함께 출력.
"""
import time

import pinkylib
from pinkylib import LCD, LED, Buzzer

HOST = "192.168.7.1"        # 로봇 주소. 로봇 AP(pinky_zxxxx)에 붙었으면 이대로,
                            # 공유기를 거쳐 붙으면 로봇 IP 로 바꾼다

pinkylib.connect(HOST)
lcd, led, bz = LCD(), LED(), Buzzer()
lcd.enable(True)                # 터치 측정 ON (touch.enable)

print("화면을 만지세요. Ctrl+C 로 종료")
try:
    while True:
        t = lcd.wait_touch(timeout=30)      # 눌릴 때까지 대기
        if t is None:
            continue
        print("터치!", t)                    # {touch, x, y, gesture}
        led.set_color(0, 80, 0)
        bz.beep(80)
        time.sleep(0.3)
        led.off()
except KeyboardInterrupt:
    print("\n종료")
    led.off()

pinkylib.disconnect()   # 로봇을 코딩모드에서 내보낸다.
                        # 안 부르면 이 프로그램이 살아있는 동안 로봇 화면이
                        # 코딩모드에 묶여 있고, 로봇 3번 버튼도 안 먹는다.
