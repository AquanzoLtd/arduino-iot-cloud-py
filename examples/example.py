# This file is part of the Python Arduino IoT Cloud.
# The MIT License (MIT)
# Copyright (c) 2022 Arduino SA
import time
import asyncio
import logging
from time import strftime
from arduino_iot_cloud import AIOTClient
from arduino_iot_cloud import Location
from arduino_iot_cloud import Schedule
from arduino_iot_cloud import ColoredLight
from random import randint
import argparse

KEY_PATH = "pkcs11:token=arduino"
CERT_PATH = "pkcs11:token=arduino"
CA_PATH = "ca-root.pem"
DEVICE_ID = b"25deeda1-3fda-4d06-9c3c-dd31be382cd2"


async def user_main(client):
    # Add your code here. Note to allow other tasks to run, this function
    # must yield execution periodically by calling asyncio.sleep(seconds).
    while True:
        # The composite cloud object's fields can be assigned to individually:
        client["clight"].hue = randint(0, 100)
        client["clight"].bri = randint(0, 100)
        await asyncio.sleep(1.0)


def on_switch_changed(client, value):
    # This is a write callback for the switch that toggles the LED variable. The LED
    # variable can be accessed via the client object passed in the first argument.
    client["led"] = value


def on_clight_changed(client, clight):
    logging.info(f"ColoredLight changed. Swi: {clight.swi} Bri: {clight.bri} Sat: {clight.sat} Hue: {clight.hue}")


async def main():
    # Create a client to connect to the Arduino IoT cloud. To use a secure element, set the token "pin"
    # and URI in "keyfile" and "certfile, and CA certificate (if used), in ssl_params. Alternatively,
    # a username and a password can be used for authentication, for example:
    #   client = AIOTClient(device_id, username="username", password="password")
    client = AIOTClient(
        device_id=DEVICE_ID,
        ssl_params={"pin": "1234", "keyfile": KEY_PATH, "certfile": CERT_PATH, "ca_certs": CA_PATH},
    )

    # Register cloud objects. Note these objects must be created first in the dashboard.
    # This cloud object is initialized with its last known value from the cloud. When this object is updated
    # from the dashboard, the on_switch_changed function is called with the client object and the new value.
    client.register("sw1", value=None, on_write=on_switch_changed, interval=0.250)

    # This cloud object is updated manually in the switch's on_write_change callback.
    client.register("led", value=None)

    # This is a periodic cloud object that gets updated at fixed intervals (in this case 1 seconed) with the
    # value returned from its on_read function (a formatted string of the current time). Note this object's
    # initial value is None, it will be initialized by calling the on_read function.
    client.register("clk", value=None, on_read=lambda x: strftime("%H:%M:%S", time.localtime()), interval=1.0)

    # This is an example of a composite cloud object (a cloud object with multiple variables). In this case
    # a colored light with switch, hue, saturation and brightness attributes. Once initialized, the object's
    # attributes can be accessed using dot notation. For example: client["clight"].swi = False.
    client.register(ColoredLight("clight", swi=True, on_write=on_clight_changed))

    # This is another example of a composite cloud object, a map location with lat and long attributes.
    client.register(Location("treasureisland", lat=31.264694, lon=29.979987))

    # This object allows scheduling recurring events from the cloud UI. On activation of the event, if the
    # on_active callback is provided, it gets called with the client object and the schedule object value.
    # Note: The activation status of the object can also be polled using client["schedule"].active.
    client.register(Schedule("schedule", on_active=lambda client, value: logging.info(f"Schedule activated {value}!")))

    # Start the Arduino IoT cloud client. Note a co-routine can be passed to client.run(coro), in this case it will
    # scheduled to run along with the other cloud objects.
    await client.run(user_main)


if __name__ == "__main__":
    # Parse command line args.
    parser = argparse.ArgumentParser(description="arduino_iot_cloud.py")
    parser.add_argument("-d", "--debug", action="store_true",  help="Enable debugging messages")
    args = parser.parse_args()

    # Assume the host has an active Internet connection.

    # Configure the logger.
    # All message equal or higher to the logger level are printed.
    # To see more debugging messages, pass --debug on the command line.
    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(asctime)s.%(msecs)03d %(message)s",
        level=logging.DEBUG if args.debug else logging.INFO,
    )
    asyncio.run(main())
