"""LED - NeoPixel 램프(3개). 고정 / 깜빡임 / 디밍(숨쉬기)."""
from ._client import client


class LED:
    def set_color(self, r, g, b, bright=127):
        """색 고정 (r,g,b,밝기 0~255)."""
        client().call("led.set_color", r=r, g=g, b=b, bright=bright)

    def blink(self, r, g, b, bright=127, on_ms=300, off_ms=300):
        """깜빡임."""
        client().call("led.blink", r=r, g=g, b=b, bright=bright, on_ms=on_ms, off_ms=off_ms)

    def dimming(self, r, g, b, min_bright=0, max_bright=255, cycle_ms=2000):
        """밝기 숨쉬기."""
        client().call("led.dimming", r=r, g=g, b=b,
                      min=min_bright, max=max_bright, cycle_ms=cycle_ms)

    def off(self):
        client().call("led.off")

    def close(self):
        try: self.off()
        except Exception: pass
