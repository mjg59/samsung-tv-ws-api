#!/home/homeassistant/dev/samsung-tv-ws-api/bin/python3

import sys
import os
import logging
import wakeonlan
import time
import subprocess

sys.path.append("../")

from samsungtvws import SamsungTVWS

"""
install in HomeAssistant like this

switch:
  - platform: command_line
    switches:
      tv_art_mode:
        friendly_name: Art Mode
        command_on: /home/homeassistant/dev/samsung-tv-ws-api/switch.py True
        command_off: /home/homeassistant/dev/samsung-tv-ws-api/switch.py False
        command_state: /home/homeassistant/dev/samsung-tv-ws-api/switch.py
        icon_template: >
         {% if value == 'on' %} mdi:image-frame
         {% else %} mdi:television
         {% endif %}
"""

# Increase debug level
logging.basicConfig(level=logging.INFO)

# Autosave token to file
token_file = os.path.dirname(os.path.realpath(__file__)) + "/tv-token.txt"
host = "samsung-frame"
port = 8002


def ping():
    # nmap -sn -PS samsung-frame
    return subprocess.run(["/usr/bin/ping", "-q", "-c1", host], capture_output=True).returncode == 0

is_on = ping()
print(f"{'on' if is_on else 'off'}")

# print(tv.rest_device_info())
if len(sys.argv) > 1:
    mode = (sys.argv[1]).lower() in ["on", "true"]
    print(f"Setting mode to {'on' if mode else 'off'}")
    if mode:
        if not is_on:
            print("Waking TV")
            wakeonlan.send_magic_packet("7c:0a:3f:15:f5:21")
        count = 0
        while not ping() and count < 15:
            count += 1
        tv = SamsungTVWS(host=host, port=port, token_file=token_file)
        tv.art().set_artmode(mode)
        if not tv.art().get_artmode():
            # If TV doesn't switch to art mode it's probably on
            tv.send_key("KEY_POWER")
            tv.art().set_artmode(mode)
        if tv.art().get_artmode():
            print("TV set to art mode")
        else:
            print("Failed to set art mode")
    else:
        if is_on:
            tv = SamsungTVWS(host=host, port=port, token_file=token_file)
            tv.hold_key("KEY_POWER", seconds=5)
            count = 0
            while ping() and count < 15:
                count += 1
                time.sleep(1)
            if count < 15:
                print("TV powered off")
            else:
                print("Failed to power off TV")
        else:
            print("Power is already off")
        sys.exit(0)
else:
    if is_on:
        tv = SamsungTVWS(host=host, port=port, token_file=token_file)
        print(tv.rest_device_info())
