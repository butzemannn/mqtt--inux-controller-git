from typing import Callable, Any

import paho.mqtt.client as mqtt


class MQTTClient:
    def __init__(
            self,
            host: str,
            topic: str,
            is_receiver: bool,
            on_message: Callable[[mqtt.Client, Any, Any], None] = None,
            username: str = None,
            password: str = None
    ):
        """
        Set the initial MQTTClient parameters and setup the MQTT client itself

        :param host: The MQTT host to which the client should connect
        :param topic: The topic where to publish to or receive from
        :param is_receiver: Boolean value if the client is used as receiver or as publisher
        :param on_message: If is_receiver is True, this field is required. It defines the method which will
            be executed when a message is received from host on the defined topic.
        """
        if is_receiver and on_message is None:
            raise ValueError("When working as receiver, the on_message parameter is required!")

        self.interrupt = False
        self.host = host
        self.topic = topic
        self.is_receiver = is_receiver
        if is_receiver:
            self.on_message = on_message

        self.username = username
        self.password = password

        self.client = self._setup_client()

    def _setup_client(self) -> mqtt.Client:
        """
        Setup the MQTT client by setting necessary functions

        :return: Returns the client that is set up
        """
        client = mqtt.Client()
        client.on_connect = self._on_connect()
        if self.is_receiver:
            client.on_message = self.on_message

        client.username_pw_set(self.username, self.password)
        client.connect(self.host, 1883, 60)
        return client

    def _on_connect(self) -> Callable[[mqtt.Client, Any, Any, Any], None]:
        def on_connect(client, userdata, flags, rc):
            client.subscribe(self.topic)

        return on_connect

    def publish(self, msg: str) -> None:
        """
        Publish the given message to the client topic

        :param msg: The message that should be published
        :return: None
        """
        self.client.publish(self.topic, msg)

    def loop_forever(self):
        self.client.loop_forever()
        if self.interrupt:
            return

    def interrupt_loop(self):
        self.interrupt = True

