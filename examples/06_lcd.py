"""LCD - 색 채우기 + 이미지 표시 (로봇 전원 ON 필요).

이미지는 PC에서 RGB565로 변환해 서버로 보내면 서버가 화면에 그린다.
"""
import time

import pinkyzero
from pinkyzero import LCD

HOST = "192.168.7.1"        # 로봇 주소. 로봇 AP(pinky_zxxxx)에 붙었으면 이대로,
                            # 공유기를 거쳐 붙으면 로봇 IP 로 바꾼다

pinkyzero.connect(HOST)
lcd = LCD()
lcd.backlight(True)             # 이전 실행이 꺼뒀을 수 있으니 켜고 시작

print("남색 채우기")
lcd.fill(0, 0, 40)
time.sleep(1.0)

try:
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (lcd.WIDTH, lcd.HEIGHT), (18, 18, 18))
    d = ImageDraw.Draw(im)
    d.ellipse([70, 45, 214, 195], fill=(255, 200, 0))   # 노란 얼굴
    d.ellipse([110, 90, 130, 110], fill=(0, 0, 0))       # 눈
    d.ellipse([154, 90, 174, 110], fill=(0, 0, 0))
    d.arc([115, 120, 169, 165], 20, 160, fill=(0, 0, 0), width=4)  # 입
    lcd.image(im)
    print("이미지 표시 완료")
except ImportError:
    print("PIL 없음 → 이미지 예제 건너뜀 (pip install pillow)")

time.sleep(2)
lcd.off()                       # 화면 지우고 백라이트 끄고 종료
print("완료 (화면 꺼짐)")

pinkyzero.disconnect()   # 로봇을 코딩모드에서 내보낸다.
                        # 안 부르면 이 프로그램이 살아있는 동안 로봇 화면이
                        # 코딩모드에 묶여 있고, 로봇 3번 버튼도 안 먹는다.
