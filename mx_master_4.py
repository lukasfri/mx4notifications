import logging
from enum import IntEnum
from struct import pack, unpack

import hid

LOGITECH_VID = 0x046D


class ReportID(IntEnum):
    Short = 0x10  # 7 bytes
    Long = 0x11  # 20 bytes


class FunctionID(IntEnum):
    IRoot = 0x0000
    IFeatureSet = 0x0001
    IFeatureInfo = 0x0002

    Haptic = 0x0B4E


class MXMaster4:
    device: hid.Device | None = None

    def __init__(self, path: str, device_idx: int):
        self.path = path
        self.device_idx = device_idx

    @classmethod
    def find(cls):
        devices = hid.enumerate(LOGITECH_VID)

        for device in devices:
            if device["usage_page"] == 65280:
                path = device["path"].decode("utf-8")
                logging.debug(f"Found: %s", device["product_string"])
                logging.debug(f"\tPath: %s", path)
                logging.debug(
                    f"\tVID:PID: %.04X:%.04X",
                    device["vendor_id"],
                    device["product_id"],
                )
                logging.debug(f"\tInterface: %s", device.get("interface_number"))
                return cls(path, device["interface_number"])

        return None

    def __enter__(self):
        self.device = hid.Device(path=self.path.encode())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.device.close()

    def write(self, data: bytes):
        if not self.device:
            raise Exception("Device not open")
        self.device.write(data)

    def hidpp(
        self,
        feature_idx: FunctionID,
        *args: int,
    ) -> tuple[int, bytes]:

        if len(args) > 16:
            raise Exception("Too many arguments")

        data = bytes(args)
        if len(data) < 3:
            data += bytes([0]) * (3 - len(data))

        report_id = ReportID.Short if len(data) == 3 else ReportID.Long
        logging.debug(
            f"Sending: {report_id:02X} {self.device_idx:02X} {feature_idx:04X} {data.hex()}"
        )
        packet = pack(b">BBH3s", report_id, self.device_idx, feature_idx, data)
        self.write(packet)
        return self.read()

    def read(self) -> tuple[int, bytes]:
        response: bytes
        r_f_idx: int

        response = self.device.read(20)

        # print(f"Response: {' '.join(f'{b:02X}' for b in response)}")
        (r_report_id, r_device_idx, r_f_idx) = unpack(b">BBH", response[:4])
        if r_device_idx != self.device_idx:
            return self.read()

        if r_report_id == ReportID.Short:
            data = response[4:]
            if len(data) != 7 - 4:
                raise Exception("Wrong short report length")
        elif r_report_id == ReportID.Long:
            data = response[4:]
            if len(data) != 20 - 4:
                raise Exception("Wrong long report length")
        else:
            raise Exception("Unknown report ID")

        return r_f_idx, response[4:]


def demo():
    from time import sleep

    logging.basicConfig(level=logging.DEBUG)

    mx_master_4 = MXMaster4.find()

    if not mx_master_4:
        logging.error("MX Master 4 not found!")
        exit(1)

    with mx_master_4 as dev:
        for i in range(15):
            logging.info("Haptic %d", i)
            dev.hidpp(
                FunctionID.Haptic,
                i,
            )
            sleep(3)


if __name__ == "__main__":
    demo()
