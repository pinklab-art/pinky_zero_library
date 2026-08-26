"""Buzzer - 알림음과 멜로디."""
import time

from ._client import client

BEEP_FREQ = 4000        # 부저가 가장 크게 울리는 주파수

# 음이름 -> 주파수(Hz). "R" = 쉼표
_NOTES = {
    "C4": 262, "C#4": 277, "D4": 294, "D#4": 311, "E4": 330, "F4": 349,
    "F#4": 370, "G4": 392, "G#4": 415, "A4": 440, "A#4": 466, "B4": 494,
    "C5": 523, "C#5": 554, "D5": 587, "D#5": 622, "E5": 659, "F5": 698,
    "F#5": 740, "G5": 784, "G#5": 831, "A5": 880, "A#5": 932, "B5": 988,
    "C6": 1047, "C#6": 1109, "D6": 1175, "D#6": 1245, "E6": 1319, "F6": 1397,
    "F#6": 1480, "G6": 1568, "G#6": 1661, "A6": 1760, "A#6": 1865, "B6": 1976,
    "C7": 2093, "C#7": 2217, "D7": 2349, "D#7": 2489, "E7": 2637, "F7": 2794,
    "F#7": 2960, "G7": 3136, "G#7": 3322, "A7": 3520, "A#7": 3729, "B7": 3951,
    "C8": 4186,
    "R": 0, "REST": 0,
}

# 한글 계이름
_KO = {"도": "C5", "레": "D5", "미": "E5", "파": "F5",
       "솔": "G5", "라": "A5", "시": "B5", "쉼": "R"}


def note_freq(name):
    """음이름/계이름 -> 주파수(Hz). 모르는 이름이면 None."""
    key = str(name).strip()
    if key.upper() in _NOTES:
        return _NOTES[key.upper()]
    return _NOTES.get(_KO.get(key, ""), None)


class Buzzer:
    def play(self, freq_hz=BEEP_FREQ, ms=150):
        """freq_hz [Hz] 로 ms [밀리초] 울림."""
        client().call("buzzer", freq=int(freq_hz), ms=int(ms))

    def beep(self, ms=120, count=1, gap_ms=100):
        """알림음을 count 번."""
        for i in range(int(count)):
            self.play(BEEP_FREQ, ms)
            if i < int(count) - 1:
                time.sleep((ms + gap_ms) / 1000.0)

    def note(self, name, ms=200):
        """음이름으로 재생. 'C5' / 'A#4' / '도' / 'R'(쉼표)."""
        f = note_freq(name)
        if f is None:
            raise ValueError(f"모르는 음이름: {name!r} (예: 'C5', 'A#4', '도', 'R')")
        self.play(f, ms)

    def melody(self, notes, ms=200, gap_ms=20):
        """여러 음을 순서대로 연주. 끝날 때까지 기다린다.

        notes:  "도 레 미"  /  ["C5", "D5"]  /  [("C5", 400), ("E5", 200)]
        """
        if isinstance(notes, str):
            notes = notes.split()
        for item in notes:
            if isinstance(item, (tuple, list)):
                name, dur = item[0], int(item[1])
            else:
                name, dur = item, int(ms)
            self.note(name, dur)
            time.sleep((dur + gap_ms) / 1000.0)

    def off(self):
        """소리 끄기."""
        self.play(0, 0)

    def close(self):
        pass
