# pinkylib (PC 클라이언트) 예제

PC에서 WebSocket으로 로봇(Pinky Zero) 서버를 원격 제어하는 예제 모음.

## 준비
```bash
pip install -e ..          # 저장소 루트의 pinkylib 설치 (필요 시)
```
- 로봇에서 `pinky_server.py`가 떠 있어야 함 (`ws://<로봇IP>:8765`).
- **IMU·카메라는 부팅 시 OFF** → 읽기 전에 `pinkylib.enable_imu()` / `Camera().start()` 로 켠다.
  보드 그룹(배터리·IR·모션·버튼)은 로봇이 부팅부터 켜 두므로 켤 필요가 없다.
  (`Motor`/`LCD`는 생성 시 필요한 측정을 알아서 켬.)

## 실행
각 예제 맨 위의 `HOST` 를 로봇 주소로 고친 뒤 그냥 실행한다.

```python
HOST = "192.168.7.1"        # 로봇 AP(pinky_zxxxx)에 붙었으면 이대로
```
```bash
python3 00_quickstart.py
```

로봇 AP 에 직접 붙었으면 `192.168.7.1` 그대로 두면 되고, 공유기를 거쳐 붙었으면
그 망에서의 로봇 IP 로 바꾼다.

## 📓 메서드별로 보기: `pinky_examples.ipynb`
매뉴얼의 **메서드 하나가 셀 하나**인 주피터 노트북 (13그룹 / 65메서드).
맨 위 **연결 셀**을 한 번 실행한 뒤, 보고 싶은 메서드 셀만 골라 돌리면 된다.
```bash
pip install jupyter        # 필요 시
jupyter notebook pinky_examples.ipynb
```
연결 셀의 `HOST`는 기본값이 `192.168.7.1`이라 USB로 붙었으면 그대로 두면 된다.

> 이 노트북은 Confluence 매뉴얼에서 자동 생성한다(생성기는 저장소에 없음).
> 손으로 고치면 다음 생성 때 덮어써지니, 예제를 바꾸려면 매뉴얼 쪽을 먼저 고칠 것.

## 목록 (개별 스크립트)
| 파일 | 내용 | 주의 |
|---|---|---|
| `00_quickstart.py` | 연결 + 센서 켜고 배터리/방위 읽기 | |
| `01_sensors.py` | 배터리·바닥/거리IR·모션·버튼·엔코더 루프 | |
| `02_imu.py` | IMU 방위/자세/자이로 | |
| `03_motor.py` | 전진·회전 + 엔코더/회전수 | **바퀴 띄우고!** |
| `04_led.py` | LED 고정/깜빡임/디밍 | |
| `05_buzzer.py` | 부저 삑 + 멜로디 | |
| `06_lcd.py` | LCD 색채우기 + 이미지 | 로봇 전원 ON |
| `07_touch.py` | 터치 대기 → LED+부저 반응 | 로봇 전원 ON |
| `08_camera.py` | 스냅샷 저장 + 실시간 영상 창(`cv2.imshow`) | picamera2 필요 |
| `09_mic_speaker.py` | 녹음/재생/톤/레벨 | 오디오 오버레이 필요 |
| `10_gesture.py` | 터치 제스처(스와이프/탭) 인식 | 로봇 전원 ON |
| `11_vision.py` | `read_array()` → 필터 5종을 한 창에 나란히 (`s` 로 저장) | |

> ⚠️ `06/07`(LCD·터치)은 로봇 전원이 ON이어야 한다.
