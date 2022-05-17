import signal
import subprocess
import threading
import time

from src.utils.mqttswitch import MQTTSwitch


class VNCSwitch1:
    def __init__(self):
        self.interrupt = False
        self.host = "192.168.178.152"
        self.state_topic = "home/linux/vncswitch1"
        self.command_topic = "home/linux/vncswitch1/set"
        self.availability_topic = "home/linux/vncswitch1/available"

        signal.signal(signal.SIGTERM, self.__stop__)
        signal.signal(signal.SIGINT, self.__stop__)

        # service information
        self.service_name = "vncserver@:1"

        self.switch = MQTTSwitch(
            self.host,
            self.state_topic,
            self.command_topic,
            self.availability_topic,
            self._on_command()
        )
        self.set_switch_sate()

    def __stop__(self):
        self.switch.set_available(False)
        self.interrupt = True
        self.switch.interrupt_loop()

    def set_switch_sate(self):
        if self.is_vnc_service_running():
            self.switch.set_state(True)
        else:
            self.switch.set_state(False)

        self.switch.set_available(True)

    def _on_command(self):
        def on_command(client, userdata, message):
            message = str(message.payload.decode("utf--8"))
            if message == "ON":
                if self.is_vnc_service_running():
                    return
                self.start_vnc_service()
                self.switch.set_state(True)
            elif message == "OFF":
                if not self.is_vnc_service_running():
                    return
                self.stop_vnc_service()
                self.switch.set_state(False)

        return on_command

    def is_vnc_service_running(self) -> bool:
        command = f"systemctl status {self.service_name}"
        status = subprocess.call([command], shell=True, stdout=subprocess.DEVNULL)
        return status == 0

    def start_vnc_service(self) -> None:
        command = f"systemctl start {self.service_name}"
        subprocess.call([command], shell=True, stdout=subprocess.DEVNULL)

    def stop_vnc_service(self) -> None:
        command = f"systemctl stop {self.service_name}"
        subprocess.call([command], shell=True, stdout=subprocess.DEVNULL)

    def loop_forever(self):
        self.switch.loop_forever()


def start_listining_thread(vncswitch: VNCSwitch1):
    vncswitch.loop_forever()


def start_status_thread(vncswitch: VNCSwitch1):
    while True:
        if vncswitch.interrupt:
            return

        vncswitch.set_switch_sate()
        time.sleep(1)


if __name__ == "__main__":
    vncswitch = VNCSwitch1()
    try:
        lthread = threading.Thread(target=start_listining_thread, args=(vncswitch,))
        sthread = threading.Thread(target=start_status_thread, args=(vncswitch,))
        lthread.start()
        sthread.start()
        lthread.join()
        sthread.join()
    finally:
        vncswitch.__stop__()

