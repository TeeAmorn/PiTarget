# PiTarget
The goal of this project is to design airsoft targets that are controlled centrally through a terminal-based program ran on the Raspberry Pi. The MQTT protocol is adopted to establish communication between the program and the targets. These targets are built using ESP32 micro-controllers, which communicate to the program via the MQTT broker hosted on the Raspberry Pi.

### Installation
#### Broker
This project uses Mosquitto to host the MQTT broker. To install the Mosquitto package, open terminal on the Raspberry Pi and type `sudo apt-get install mosquitto`. 

We will then configure our broker to prevent unauthorized clients from publishing or subscribing to the broker. Type `sudo nano /etc/mosquitto/mosquitto.conf` into terminal; this will open the broker configuration file via the GNU nano editor. Scroll to the very bottom; there you should find the line:
```
include_dir /etc/mosquitto/conf.d
```
Replace this line with the following:
```
allow_anonymous false
password_file /etc/mosquitto/pwfile
listener 1883
```
Setting `allow_anonymous` to `false` requires clients to provide a username in order to connect. The second line sets `/etc/mosquitto/pwfile` as the path to the password file, which will contain a list of authorized clients. Finally, the final line tells the broker to listen for messages on port `1883`. Close and save the file by pressing **control+X** and then **Y** when prompted.

To create the authorized client, type `sudo mosquitto_passwd -c /etc/mosquitto/pwfile username`, replacing `username` with the your username. You will then be prompted to enter the password you would like to use. Since we have just reconfigured our broker, it will have to be restarted in order for the new configuration to be implemented. Type `sudo killall mosquitto` to terminate the broker, and then `mosquitto -c mosquitto.conf -v` to start the broker again.
#### Terminal-Based Program
