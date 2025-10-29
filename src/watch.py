import logging
import subprocess
import threading

from mx_master_4 import FunctionID, MXMaster4


def monitor_notifications(device):
    """Monitor D-Bus for notifications using dbus-monitor"""
    cmd = [
        "dbus-monitor",
        "--session",
        "interface='org.freedesktop.Notifications',member='Notify'",
    ]

    logging.info("Starting dbus-monitor...")
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
    )

    try:
        for line in process.stdout:
            line = line.strip()
            if line:
                logging.debug("D-Bus: %s", line)
                # When we see a Notify method call, trigger haptic
                if "member=Notify" in line or "method call" in line.lower():
                    try:
                        device.hidpp(FunctionID.Haptic, 0)
                        logging.info("✓ Haptic feedback triggered!")
                    except Exception as e:
                        logging.error("Failed to trigger haptic: %s", e)
                        if "No such device" in str(e):
                            logging.info("Trying to reconnect MX Master 4...")
                            new_device = MXMaster4.find()
                            if new_device:
                                try:
                                    device.__exit__(None, None, None)
                                except Exception:
                                    pass
                                device = new_device
                                device.__enter__()
                                logging.info("Reconnected to MX Master 4.")
                                try:
                                    device.hidpp(FunctionID.Haptic, 0)
                                    logging.info("✓ Haptic feedback triggered after reconnect!")
                                except Exception as e2:
                                    logging.error("Failed again after reconnect: %s", e2)
                            else:
                                logging.error("MX Master 4 not found on reconnect attempt.")
    except KeyboardInterrupt:
        process.terminate()
        raise


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    device = MXMaster4.find()
    if not device:
        logging.error("MX Master 4 not found!")
        exit(1)

    with device as dev:
        logging.info("MX Master 4 connected!")
        logging.info("Listening for notifications... Press Ctrl+C to stop.")
        logging.info("Test with: notify-send 'Test' 'Message'")
        logging.info("")

        try:
            monitor_notifications(dev)
        except KeyboardInterrupt:
            logging.info("\nStopping...")


if __name__ == "__main__":
    main()
