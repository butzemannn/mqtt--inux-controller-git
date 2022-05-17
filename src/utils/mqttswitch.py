from typing import Callable, Any
import paho.mqtt.client as mqtt

from src.utils.mqttclient import MQTTClient


class MQTTSwitch:
    """
    Provides the interface for a Home Assistant MQTT-Switch
    """
    def __init__(
            self,
            host: str,
            state_topic: str,
            command_topic: str,
            availability_topic: str,
            on_command: Callable[[mqtt.Client, Any, Any], None]
    ):
        """
        Initialise the required parameters.

        :param host: The MQTT broker to which to connect to. Most likely a Home Assistant ip.
        :param state_topic: The state topic path to publish the current switch state to.
        :param command_topic: The command topic path where the Home assistant switch change can be received.
        :param availability_topic: The availability topic path where to publish the switch's availability
        :param on_command: Method that is executed when the on-command from home assistant is received
        """
        self.host = host
        self.state_topic = state_topic
        self.command_topic = command_topic
        self.availability_topic = availability_topic
        self.on_command = on_command

        # Set available for Home Assistant
        self._setup_clients()
        self.set_available(True)

    def __delete__(self, instance):
        self.set_available(False)

    def _setup_clients(self) -> None:
        """
        Setup the necessary topics for home assistant interaction. The state topic communicates the current switch
        state, command topic receives the switch state changes from home assistant and the availability topic
        sets the current switches availability within Home Assistant.
        :return:
        """
        self.state_client = MQTTClient(
            self.host,
            self.state_topic,
            False,
            username="mqtt",
            password="mqtt"
        )
        self.command_client = MQTTClient(
            self.host,
            self.command_topic,
            True,
            self.on_command,
            username="mqtt",
            password="mqtt"
        )
        self.availability_client = MQTTClient(
            self.host,
            self.availability_topic,
            False,
            username="mqtt",
            password="mqtt"
        )

    def set_available(self, state: bool) -> None:
        """
        Sets the switches availability according to the given state parameter.
        True means available, False equals not available

        :param state: The switches availability. True is available, False is not available
        :return: None
        """
        msg = "ONLINE" if state else "OFFLINE"
        self.availability_client.publish(msg)

    def set_state(self, state: bool) -> None:
        """
        Sets the current switch state in Home Assistant. True is enabling the switch, while False disables it.

        :param state: The state of the switch. True is on, False equals off
        :return: None
        """
        msg = "ON" if state else "OFF"
        self.state_client.publish(msg)

    def loop_forever(self):
        self.command_client.loop_forever()

    def interrupt_loop(self):
        self.command_client.interrupt_loop()
