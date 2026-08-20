"""IR - 바닥 라인센서(5채널) + 거리센서(4채널)."""
from ._client import client


class IR:
    def read_floor(self):
        """바닥 라인센서 5채널 [ch0..ch4]."""
        return client().field("floor_ir", "pico")

    def read_range(self):
        """거리(장애물) IR 4채널 [ch0..ch3]."""
        return client().field("range_ir", "pico")

    def read(self):
        """(floor 5채널, range 4채널) 튜플."""
        st = client().require("pico")
        return st.get("floor_ir"), st.get("range_ir")

    def close(self):
        pass
