import time
from unittest import TestCase
from src.utils.mqttswitch import MQTTSwitch
import paho.mqtt.client as mqtt


class TestMQTTSwitch(TestCase):
    def _on_command(self):
        def on_command(client, userdata, flags, rc):
            print(f"State:{userdata}")
        return on_command

    def test_is_available(self):
        client = MQTTSwitch(
            "192.168.178.152",
            "home/linux/vncswitch1",
            "home/linux/vncswitch1/set",
            "home/linux/vncswitch1/available",
            self._on_command()
        )
        client.set_available(True)
        time.sleep(5)
        client.set_available(False)
        self.assertEqual(True, True)

    def test_set_state(self):
        client = MQTTSwitch(
            "192.168.178.152",
            "home/linux/vncswitch1",
            "home/linux/vncswitch1/set",
            "home/linux/vncswitch1/available",
            self._on_command()
        )
        client.set_available(True)
        client.set_state(True)
        time.sleep(3)
        client.set_state(False)
        time.sleep(3)
        client.set_available(False)

    def test_general(self):
        client = mqtt.Client()
        client.username_pw_set("mqtt", "mqtt")
        client.connect("192.168.178.152")
        client.publish("home/linux/vncswitch1/available", "OFFLINE")

