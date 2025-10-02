import logging
import os
from _socket import SO_REUSEADDR, SOL_SOCKET
from contextlib import contextmanager
from socket import AF_UNIX, SOCK_STREAM, socket
from typing import Iterator

from mx_master_4 import FunctionID, MXMaster4

XDG_RUNTIME_DIR = os.getenv("XDG_RUNTIME_DIR")
HYPRLAND_INSTANCE_SIGNATURE = os.getenv("HYPRLAND_INSTANCE_SIGNATURE")


@contextmanager
def hyprland_socket():
    with socket(AF_UNIX, SOCK_STREAM) as s:
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.connect(f"{XDG_RUNTIME_DIR}/hypr/{HYPRLAND_INSTANCE_SIGNATURE}/.socket2.sock")

        yield s


def hyprland_listener() -> Iterator[tuple[str, list[str]]]:
    with hyprland_socket() as s:
        while True:
            response = s.recv(1024).decode(errors="replace")
            packages = response.rstrip("\n").split("\n")
            for pkg in packages:
                cmd, args_ = pkg.split(">>", 1)
                args = args_.split(",")
                yield cmd, args


def main():
    logging.basicConfig(level=logging.DEBUG)
    device = MXMaster4.find()
    if not device:
        logging.error("MX Master 4 not found!")
        exit(1)

    with device as dev:
        last_window = None
        for cmd, args in hyprland_listener():
            logging.debug("%s -> %s", cmd, ",".join(args))
            if cmd == "activewindowv2":
                if args == last_window:
                    continue

                dev.hidpp(FunctionID.Haptic, 2)
                last_window = args


if __name__ == "__main__":
    main()
