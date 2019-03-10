import logging
import ssl
from hashlib import sha1
from time import sleep

import paho.mqtt.client as mqtt

_LOG = logging.getLogger(__name__)

RECONNECT_DELAY_SECS = 5
LOG_LEVEL_MAP = {
    mqtt.MQTT_LOG_INFO: logging.INFO,
    mqtt.MQTT_LOG_NOTICE: logging.INFO,
    mqtt.MQTT_LOG_WARNING: logging.WARNING,
    mqtt.MQTT_LOG_ERR: logging.ERROR,
    mqtt.MQTT_LOG_DEBUG: logging.DEBUG,
}


class ConnectionFailed(Exception):
    pass


def do_nothing(*args, **kwargs):
    pass


def validate_config(config):
    # TODO: Implement
    pass


class MQTT(object):
    def __init__(self, config, on_connect=None, on_message=None, on_log=None):
        validate_config(config)
        self.config = config

        topic_prefix = config["topic_prefix"]
        protocol = mqtt.MQTTv311
        if config["protocol"] == "3.1":
            protocol = mqtt.MQTTv31

        # https://stackoverflow.com/questions/45774538/what-is-the-maximum-length-of-client-id-in-mqtt
        # TLDR: Soft limit of 23, but we needn't truncate it on our end.
        client_id = config["client_id"]
        if not client_id:
            client_id = "pi-mqtt-gpio-%s" % sha1(topic_prefix.encode("utf8")).hexdigest()

        self.client = mqtt.Client(
            client_id=client_id, clean_session=False, protocol=protocol
        )

        if config["user"] and config["password"]:
            self.client.username_pw_set(config["user"], config["password"])

        # Set last will and testament (LWT)
        self.status_topic = "%s/%s" % (topic_prefix, config["status_topic"])
        self.client.will_set(
            self.status_topic, payload=config["status_payload_dead"], qos=1, retain=True
        )
        _LOG.debug(
            "Last will set on %r as %r.", self.status_topic, config["status_payload_dead"]
        )

        # Set TLS options
        tls_enabled = config.get("tls", {}).get("enabled")
        if tls_enabled:
            self.set_tls_options(config["tls"])

        self.set_connection_callback(on_connect or do_nothing)
        self.set_message_callback(on_message or do_nothing)
        self.set_log_callback(on_log or do_nothing)

    def set_tls_options(self, tls_config):
        tls_kwargs = dict(
            ca_certs=tls_config.get("ca_certs"),
            certfile=tls_config.get("certfile"),
            keyfile=tls_config.get("keyfile"),
            ciphers=tls_config.get("ciphers"),
        )
        try:
            tls_kwargs["cert_reqs"] = getattr(ssl, tls_config["cert_reqs"])
        except KeyError:
            pass
        try:
            tls_kwargs["tls_version"] = getattr(ssl, tls_config["tls_version"])
        except KeyError:
            pass

        self.client.tls_set(**tls_kwargs)
        self.client.tls_insecure_set(tls_config["insecure"])

    def set_connection_callback(self, func):
        """
        Run the user's callback function on succesful connection, and handle errors.
        """

        def on_conn(client, userdata, flags, rc):
            fatal_exceptions = {
                1: "Incorrect protocol version used to connect to MQTT broker.",
                2: "Invalid client identifier used to connect to MQTT broker.",
                4: "Bad username or password used to connect to MQTT broker.",
                5: "Not authorised to connect to MQTT broker.",
            }

            if rc in fatal_exceptions:
                msg = fatal_exceptions[rc]
                _LOG.fatal(msg)
                raise ConnectionFailed(msg)

            if rc == 0:
                _LOG.info(
                    "Connected to the MQTT broker with protocol v%s.",
                    self.config["protocol"],
                )
                func(client, userdata, flags, rc)
                client.publish(
                    self.status_topic,
                    self.config["status_payload_running"],
                    qos=1,
                    retain=True,
                )
            elif rc == 3:
                _LOG.warning(
                    "MQTT broker unavailable. Retrying in %s secs...",
                    RECONNECT_DELAY_SECS,
                )
                sleep(RECONNECT_DELAY_SECS)
                client.reconnect()
            else:
                _LOG.warning("Received unknown 'rc' variable on connect: %r", rc)

        self.client.on_connect = on_conn

    def set_message_callback(self, func):
        def on_msg(client, userdata, msg):
            try:
                _LOG.info("Received message on topic %r: %r", msg.topic, msg.payload)
                func(client, userdata, msg)
            except Exception:
                _LOG.exception("Exception while handling received MQTT message:")

        self.client.on_message = on_msg

    def set_log_callback(self, func):
        def on_log(client, userdata, level, buf):
            _LOG.log(LOG_LEVEL_MAP[level], "MQTT client: %s" % buf)
            func(client, userdata, level, buf)

        self.client.on_log = on_log
