# Standard Library Imports
import re
import struct
# Third Party Imports
from curses import wrapper
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
# Local Imports
from page import *

# ===== Packet Structure ===== #
#                              #
#   - c2t                      #
#       - (char) deviceID      #
#       - (flaot) dur          #
#       - (short) active       #
#                              #
#   - t2c                      #
#       - (char) deviceID      #
#       - (short) points       #
#                              #
# ============================ #

# ========== MQTT client authentication details ==========

client = mqtt.Client("Broker")
mqtt_user = "user"
mqtt_password = "pass"
client.username_pw_set(mqtt_user, mqtt_password)

# ========== Global variables ============================

broker_ip = ""
setting = {'difficulty':1, 'num_target':1, \
    'total_points':0, 'active':0, 'targets':[0]}

# ========== MQTT callback functions =====================

def on_connect(client, userdata, flags, rc):
    # Only subscribe to 'tar2cpu' if connection is authorized
    if rc == 0:
        client.subscribe('tar2cpu')
        print("Connected")

def on_message(client, userdata, msg):
    # Only receive packets from the broker when program is active
    if (setting['active'] == 1):
        id_str, points = struct.unpack('sh', msg.payload)
        target_id = int(id_str) - 1
        setting['targets'][target_id] = 0
        setting['total_points'] += points
        print(1)
        print("msg")
        print(setting)

client.on_connect = on_connect
client.on_message = on_message

# ========== Launch ======================================

def launch(stdscr):

    # Takes user to setup page
    broker_ip = setup(stdscr)
    
    authentication = {'user':mqtt_user,'pass':mqtt_password,\
        'broker_ip':broker_ip}

    # Check if given IP address is valid; 
    # if it is, connect to broker and start MQTT loop
    if (re.search(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', broker_ip) == None):
        invalid_broker(stdscr)
        return
    try:
        client.connect(broker_ip, 1883)
        client.loop_start()
    except:
        invalid_broker(stdscr)
        return

    # Takes user to main page
    current_row = 0
    while (True):
        
        # Let the user input which page s/he wants to visit
        current_row = main(stdscr, current_row)

        # Go to the corresponding page
        if current_row == 0: config(stdscr, setting)
        elif current_row == 1: practice(stdscr, setting, authentication)
        elif current_row == 2: blitz(stdscr, setting, authentication)
        elif current_row == 3: speed(stdscr, setting, authentication)
        else: break

        # Turn off all targets
        packet = struct.pack('sfh', b'A', 0, 0)
        publish.single('cpu2tar', packet, 2, False, broker_ip, \
            auth={'username':mqtt_user, 'password':mqtt_password})

        # Set all targets status back to 0 (turn them off)
        setting['targets'] = [0 for x in setting['targets']]

    # Kill MQTT loop
    client.loop_stop()
    
wrapper(launch)