# Pinky Zero — 원격 제어 라이브러리 `pinkyzero`

제로 보드는 CPU가 약하고 무거운 모듈 import가 느리다. 그래서 **로봇에는 가벼운 상주 서버**만 두고,
**PC에서 `pinkyzero`으로 조종**한다. 무거운 비전(YOLO 등)은 PC가 맡는다.

```
[PC] pinkyzero  --WebSocket-->  [Zero] pinky_server  --시리얼-->  [Pico]
     Motor().set_rpm(30)            하드웨어 담당          모터/센서/LED
     비전/AI                        import 한 번만
```

- `pinkyzero/` : **PC에서** 쓰는 클라이언트 라이브러리(WebSocket). 이 저장소에 있는 건 이것뿐이다.
- 짝이 되는 `pinky_server` 는 **로봇에 미리 설치돼 부팅 때 자동 실행**된다(여기 없음).

> 센서·액추에이터 제어는 **웹소켓으로 통일**한다. 로봇 위에서 코딩할 때도
> `pinkyzero.connect("localhost")` 로 같은 서버에 붙는다.

## 설치

```bash
git clone https://github.com/pinklab-art/pinky_zero_library.git
cd pinky_zero_library
pip install -e .
```
`websocket-client`, `numpy`, `pillow`, `opencv-python` 이 같이 깔린다.

## 빠른 시작

**① 로봇** — 서버가 상주 중이라 할 일이 없다. 죽었으면 `sudo systemctl restart pinky-server`.

**② PC**
```python
import pinkyzero
pinkyzero.connect()                          # 기본 192.168.7.1 (로봇 AP에 붙었을 때)
                                            # 공유기를 거치면 connect("로봇IP")

pinkyzero.enable_all()                       # 센서는 부팅 시 전부 OFF → 측정 켜기

from pinkyzero import Battery, IR, Motor, LED, Camera
print(Battery().get_voltage())              # 배터리 전압
print(IR().read_floor())                    # 바닥 라인센서 5채널

m = Motor(); m.set_rpm(30, 30); m.stop()    # ⚠️ 바퀴 띄우고
LED().set_color(0, 128, 255)                # 파랑

cam = Camera(); cam.start(15)
frame = cam.read_array()                    # OpenCV BGR 배열

pinkyzero.disconnect()                       # 다 쓰면 꼭. 로봇이 자기 화면으로 돌아간다
```

> `disconnect()` 를 안 부르면 프로그램이 살아있는 동안 로봇 화면이 **코딩 모드에 묶여**
> 있고 로봇 3번 버튼도 먹지 않는다.

**③ 로봇 위에서 직접 코딩할 때** — 같은 라이브러리에 주소만 바꾼다.
```python
pinkyzero.connect("localhost")
```

## 센서 켜기

센서는 **부팅 시 전부 꺼져 있다**(절전·IR 간섭·IRQ 점유 때문). 읽기 전에 켠다.

| 함수 | 켜지는 것 |
|---|---|
| `pinkyzero.enable_imu()` | IMU(BNO055) |
| `pinkyzero.enable_touch()` | 터치(CST816) |
| `pinkyzero.enable_all()` | 위 셋 전부 |
| `pinkyzero.sensor_enabled()` | 현재 켜짐 상태 `{pico, imu, touch}` |

`Motor` 와 `LCD` 는 생성될 때 필요한 측정을 알아서 켠다.
꺼진 센서를 읽으면 조용히 `None` 이 나오는 게 아니라 **`pinkyzero.SensorOffError`** 가 뜨고,
무엇을 실행해야 하는지 메시지로 알려준다.

## 클래스

| 클래스 | 메서드 |
|---|---|
| `Battery` | `get_voltage()` `get_percentage()` |
| `IR` | `read_floor()`[5] `read_range()`[4] `read()` |
| `Motion` | `read()` → (dx, dy) |
| `Button` | `read()`[3] `is_pressed(i)` |
| `IMU` | `enable()` `is_enabled()` `read_euler()` `heading()` `read_gyro()` `read_accel()` `calibration_status()` `calibrate()` `read()` |
| `Motor` | `enable()` `set_rpm(l, r)` `stop()` `get_rpm()` `get_encoder()` `get_revolutions()` |
| `LED` | `set_color(r,g,b)` `blink()` `dimming()` `off()` |
| `Buzzer` | `play(freq, ms)` `beep(count=)` `note('C5' / '도' / 'do')` `melody()` `off()` |
| `Camera` | `start(fps)` `stop()` `read()` `read_array()` `snapshot()` `set_callback()` |
| `LCD` | `fill(r,g,b)` `clear()` `image(img)` `backlight()` `on()` `off()` |
| `LCD` 터치 | `enable()` `read_touch()` `touched()` `read_gesture()` `wait_touch()` `wait_gesture()` |
| `Mic` | `record(sec, path)` `record_bytes(sec)` `level()` `set_gain()` `get_gain()` |
| `Speaker` | `play(path)` `tone(freq, sec, vol)` `beep()` `stop()` `is_playing()` `set_volume()` `get_volume()` |

모든 클래스에 `close()` 가 있다. 모듈 함수는 `connect()` `disconnect()` `client()`
`enable_imu()` `enable_touch()` `enable_all()` `sensor_enabled()`.

## 예제

`examples/` 에 기능별 실행 스크립트가 있다(`00_quickstart.py` … `11_vision.py`).
메서드 하나가 셀 하나인 주피터 노트북 `examples/pinky_examples.ipynb` 도 있다.
자세한 목록은 [examples/README.md](examples/README.md) 참고.

```bash
cd examples
python3 00_quickstart.py
```

## 참고

- **IMU**: BNO055 는 Pico 가 아니라 **라즈베리파이 I2C**(`/dev/i2c-0`, 0x28)에 직결. 서버가 읽어
  status 로 보낸다. 지자기 미보정 시 `heading()` 이 0 에 고정되므로 `IMU().calibrate()` 로 먼저 보정한다.
- **LCD·터치**: ST7789 디스플레이(240×284)와 CST816 터치 모두 Pi 직결.
  **로봇 전원이 ON 이어야** Pi 가 SPI 를 잡는다(OFF 면 MCU 가 배터리 화면을 그린다).
- **오디오**: 마이크(ICS-43434)·스피커(MAX98357A)는 Pi 의 I2S. 서버가 잡고 중계한다.
- **부저**: 4kHz 공진 부품이라 그 주파수에서 가장 크게 들린다. 음량은 줄일 수만 있고 키울 수 없다.
