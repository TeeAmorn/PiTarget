# PiTarget
The goal of this project is to design airsoft targets that are controlled centrally through a terminal-based program ran on the Raspberry Pi. The MQTT protocol is adopted to establish communication between the program and the targets. These targets are built using ESP32 micro-controllers, which communicate to the program via the MQTT broker hosted on the Raspberry Pi.
### A Note to the Reader
This is my first Rasberry Pi project. I am relatively inexperienced in the areas of IoT and programming. Thus, it is without doubt that you will find certain (or even many) parts of my scripts and explanation where codes are unoptimized and terms are misused. I am still learning and will appreciate any comments and advice. Thank you in advance!
## Installation
### Broker
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

To create the authorized client, type `sudo mosquitto_passwd -c /etc/mosquitto/pwfile user`, replacing `user` with the your username. (By default, the terminal-based program and targets use `user` and `pass` as the username and password, respectively). You will then be prompted to enter the password you would like to use. Since we have just reconfigured our broker, it will have to be restarted in order for the new configuration to be implemented. Type `sudo killall mosquitto` to terminate the broker, and then `mosquitto -c mosquitto.conf -v` to start the broker again.
### Terminal-Based Program
There are two different installation methods. The simpler method is to directly download the executable file **main.exe**. One limitation of this method is the default username `user` and password `pass` must be used to connect to the broker. If you wish to use your own username and password, download the `airsoft_target` folder. Note that this method will require the installation of one additional python package: the **paho-mqtt** package. To do so, go on terminal and type `pip install paho-mqtt`.

Inside the `airsoft_target` folder, open `main.py` and change `mqtt_user` and `mqtt_password` on lines **X** and **Y** to the username and password you wish to use. Save and close the file. The program can now be launched by running the script `main.py` (type `python main.py`). You can also use `pyinstaller` to create a single executable `main.exe`, which allows the program to be launched directly by opening the executable file. This however will not be covered here.
### Targets
Finally, there are the targets. To upload our sketches to the ESP32 micro-controllers, the Arduino IDE, along with the ESP32 platform, is needed (for installation, see: `https://github.com/espressif/arduino-esp32/blob/master/docs/arduino-ide/boards_manager.md`). Open the `airsoft_target.ino` sketch and configure lines 6 to 13 under `Identifier`.
```
const char* ssid = "wifi name";
const char* wifi_password = "wifi password";

const char* mqtt_server = "broker ip address";
const char* mqtt_user = "broker username";
const char* mqtt_pass = "broker password";
const char* clientID = "id";
char id = 'id';
```
To find the broker's IP address, type `ifconfig` into terminal on the Raspberry Pi. For a given network, the IP address should be on the second line after the word `inet`. The last two lines should be an ID (ranging from 1 to 9) unique to that target. In other words, you can have at most 9 targets. The ID should always start from 1, and increase by 1 for each additional target. **Note: Targets must NOT share the same ID**. 

To build the physical targets, you will need some kind of sensor to detect hits (such as a snap action limit switch, pressure sensor, etc.) and an LED to indicate that the target is active. The sensor must be connected to pin 3 of the micro-controller and LED to pin 4. There are many methods to power the ESP32; these methods will not be covered here.
## Usage
Whenever you launch the program, you will be prompted to enter the IP address of your broker. **Note: The program has to be able to connect to the mosquitto broker on the Raspberry Pi in order to proceed onto the main screen**.
![](Images/broker_ip.png)
This will then take you to the main menu. First, configure your program to match the number of targets you have and set the gamemode's difficulty to your desired level. As the difficulty increases, the interval in which new targets appear and the duration in which they appear for decrease.
![](Images/config_screen.png)
After configuring your program, return to the main screen and pick your desired gamemode. `Practice` mode merely spawns new targets indefinitely. In `Blitz` mode, you have to earn the most points over the span of 30 seconds. In `Speed` mode, you have to hit 10 targets in the least amount of time (thus earning you the highest points). 
![](Images/main_screen.png)
## In the Works
The current setup uses an external access point to connect between the broker and the clients. To make this setup more portable, I hope to setup an access point on the Raspberry Pi itself. In other words, to have it act like a wireless router.
