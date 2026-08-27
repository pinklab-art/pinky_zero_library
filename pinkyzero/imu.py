"""IMU - BNO055 9축 (서버가 status에 실어보낸 값을 읽음).

실 IMU는 로봇의 Pi I2C(/dev/i2c-0 0x28)에 붙어있고, 서버가 주기적으로 읽어
status 스트림에 imu_* 필드로 넣어준다. 이 클래스는 그 캐시를 읽는다.
"""
from ._client import client


class IMU:
    def enable(self, on=True):
        """IMU 측정 on/off (서버는 부팅 시 OFF). read 전에 한 번 켜야 값이 온다."""
        client().call("imu.enable", on=bool(on))

    def is_enabled(self):
        """현재 IMU 측정이 켜져 있는지."""
        return bool(client().status().get("en_imu"))

    def read_euler(self):
        """(heading, roll, pitch) 도."""
        s = client().require("imu")
        return (s.get("imu_heading"), s.get("imu_roll"), s.get("imu_pitch"))

    def heading(self):
        """방위각 [도]."""
        return client().field("imu_heading", "imu")

    def read_gyro(self):
        """(x, y, z) 각속도 dps."""
        return client().field("imu_gyro", "imu")

    def read_accel(self):
        """(x, y, z) 가속도 m/s^2 (중력 제거된 선형 가속도)."""
        return client().field("imu_linacc", "imu")

    def calibration_status(self):
        """{sys,gyro,accel,mag} 각 0~3 (3=완료)."""
        return client().field("imu_calib", "imu")

    def calibrate(self, timeout=60, full=False):
        """IMU 캘리브레이션. BNO055는 '명령'이 아니라 로봇을 **움직여서** 보정한다.
        안내대로 움직이면 보정값이 0→3으로 오르고, 다 되면 완료.

        full=False: sys 가 3 되면 완료(기본).  full=True: gyro·accel·mag 모두 3.
        진행상황을 출력하고, 완료면 True / 시간초과면 False 반환.
        """
        import time
        self.enable(True)
        print("IMU calibration: gyro = hold still, "
              "accel = tilt through several orientations, "
              "mag = move in a figure eight")
        t0 = time.time()
        last = None
        while time.time() - t0 < timeout:
            c = self.calibration_status() or {}
            line = (f"sys {c.get('sys','?')}  gyro {c.get('gyro','?')}  "
                    f"accel {c.get('accel','?')}  mag {c.get('mag','?')}  (target 3)")
            if line != last:
                print(" ", line)
                last = line
            if full:
                done = all(c.get(k) == 3 for k in ("gyro", "accel", "mag"))
            else:
                done = c.get("sys") == 3
            if done:
                print("calibration done")
                return True
            time.sleep(0.5)
        print("calibration timed out:", last)
        return False

    def read(self):
        """요약 dict (heading/roll/pitch/gyro/linacc/calib)."""
        s = client().require("imu")
        return {"heading": s.get("imu_heading"), "roll": s.get("imu_roll"),
                "pitch": s.get("imu_pitch"), "gyro": s.get("imu_gyro"),
                "linacc": s.get("imu_linacc"), "calib": s.get("imu_calib")}

    def close(self):
        pass
