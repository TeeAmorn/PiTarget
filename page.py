# Standard Library Imports
import random
import struct
import time
# Third Party Imports
import curses
import paho.mqtt.publish as publish
# Local Imports
from helper import *

# ========== Setup Page ==================================

def setup(stdscr) -> str:

    # Clear window
    stdscr.clear()

    # Create a black-on-white color scheme
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Turn off blinking cursor
    curses.curs_set(0)

    # Prompt user to type in the broker's IP address
    height, width = stdscr.getmaxyx()
    text = 'Enter broker\'s IP address'
    curses.echo()
    col = width // 2 - len(text)//2
    row = height // 2
    stdscr.addstr(row, col, text)
    col = width // 2 - 7
    row = height // 2 + 1
    broker_ip = stdscr.getstr(row, col, 15)
    curses.noecho()

    # Load to connecting screen
    stdscr.clear()
    text = 'Connecting...'
    col = width // 2 - len(text)//2
    row = height // 2
    stdscr.addstr(row, col, text)
    stdscr.refresh()

    # return the IP address of the broker
    return broker_ip.decode("utf-8")

# ========== Invalid Broker ==============================

def invalid_broker(stdscr):
    
    # Clear window
    stdscr.clear()

    # Notify user that IP is incorrect
    height, width = stdscr.getmaxyx()
    text = 'Connection Failed - Invalid IP address'
    col = width // 2 - len(text)//2
    row = height // 2
    stdscr.addstr(row, col, text)
    text = 'Exit'
    col = width // 2 - len(text)//2
    row = height // 2 + 1
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(row, col, text)
    stdscr.attroff(curses.color_pair(1))
    stdscr.refresh()

    # Prompt user to exit the program
    while(1):
        key = stdscr.getch()
        if (key == curses.KEY_ENTER) or key in [10, 13]:
            return

# ========== Main ========================================

def main(stdscr, current_row):

    # Define the items to display on the main screen
    menu = ['Config', 'Practice', 'Blitz', 'Speed', 'Exit']

    # Print the menu
    print_menu(stdscr, menu, current_row)
    while (True):
        key = stdscr.getch()
        if (key == curses.KEY_LEFT or key == curses.KEY_UP) and \
            (current_row > 0):
            current_row -= 1
        elif (key == curses.KEY_RIGHT or key == curses.KEY_DOWN) and \
            (current_row < len(menu)-1):
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            return current_row
        print_menu(stdscr, menu, current_row)
    return

# ========== Config ======================================

def config(stdscr, setting):

    # Initialize currently selected row
    current_row = 0

    # Define the items to display on the config screen
    config = ['Difficulty', 'Number of Targets', 'Back']

    # Print the configuration page
    print_config(stdscr, config, setting, current_row)
    while (True):
        key = stdscr.getch()
        if (key == curses.KEY_UP) and (current_row > 0):
            current_row -= 1
        elif (key == curses.KEY_DOWN) and (current_row < len(config)-1):
            current_row += 1
        elif (key == curses.KEY_RIGHT):
            if (current_row == 0) and (setting['difficulty'] < 9):
                setting['difficulty'] += 1
            if (current_row == 1) and (setting['num_target'] < 9):
                setting['num_target'] += 1
                setting['targets'].append(0)
        elif (key == curses.KEY_LEFT): 
            if (current_row == 0) and (setting['difficulty'] > 1):
                setting['difficulty'] -= 1
            if (current_row == 1) and (setting['num_target'] > 1):
                setting['num_target'] -= 1
                setting['targets'].pop()
        elif (key == curses.KEY_ENTER or key in [10, 13]) and \
            (current_row == 2):
            return
        print_config(stdscr, config, setting, current_row)

# ========== Practice ====================================

def practice(stdscr, setting, authentication):
    
    # Set active to 1 to allow packets to be received
    setting['active'] = 1

    # Parameters for the practice mode
    max_interval = 3
    min_interval = 0.7
    max_duration = 5
    min_duration = 1.5
    level = setting['difficulty'] - 1
    interval = (8 - level) / 8 * (max_interval - min_interval) + min_interval
    duration = ((8 - level) / 8 * (max_duration - min_duration) + min_duration) * 1000

    # Start timer
    start = time.time()

    # Start loop
    while (True):
        
        # Compute time elapsed
        elapsed = (time.time() - start)

        # Generate targets and then publish every 'interval' seconds
        if not (isFull(setting['targets'])):
            target_id = random.randint(0, setting['num_target'] - 1)
            while (setting['targets'][target_id] == 1):
                target_id = random.randint(0, setting['num_target'] - 1)
            if (elapsed > interval):
                start = time.time()
                setting['targets'][target_id] = 1
                packet = struct.pack('sfh', str(target_id+1).encode(), duration, 1)
                publish.single('cpu2tar', packet, 0, False, \
                    authentication['broker_ip'], \
                    auth={'username':authentication['user'], \
                        'password':authentication['pass']})

        # Print practice page
        print_practice(stdscr, setting)
        stdscr.nodelay(True)
        key = stdscr.getch()
        if (key == curses.KEY_ENTER) or (key in [10, 13]): 
            setting['active'] = 0
            setting['total_points'] = 0
            stdscr.nodelay(False)
            return
        print_practice(stdscr, setting)

# ========== Blitz =======================================

def blitz(stdscr, setting, authentication):
    
    # Set active to 1 to allow packets to be received
    setting['active'] = 1

    # Parameters for the blitz mode
    time_limit = 30
    max_interval = 3
    min_interval = 0.7
    max_duration = 5
    min_duration = 1.5
    level = setting['difficulty'] - 1
    interval = (8 - level) / 8 * (max_interval - min_interval) + min_interval
    duration = ((8 - level) / 8 * (max_duration - min_duration) + min_duration) * 1000

    # Start timer
    start = time.time()
    begin = start

    # Start loop
    while (True):

        elapsed = time.time() - start
        curr_time = time.time() - begin

        # Generate targets and then publish every 'interval' seconds
        if (not isFull(setting['targets'])) and (curr_time < time_limit):
            target_id = random.randint(0, setting['num_target'] - 1)
            while (setting['targets'][target_id] == 1):
                target_id = random.randint(0, setting['num_target'] - 1)
            if (elapsed > interval):
                start = time.time()
                setting['targets'][target_id] = 1
                packet = struct.pack('sfh', str(target_id+1).encode(), duration, 1)
                publish.single('cpu2tar', packet, 0, False, \
                    authentication['broker_ip'], \
                    auth={'username':authentication['user'], \
                        'password':authentication['pass']})
    
        # Print practice page
        print_practice(stdscr, setting)
        stdscr.nodelay(True)
        key = stdscr.getch()
        if (key == curses.KEY_ENTER) or (key in [10, 13]): 
            setting['active'] = 0
            setting['total_points'] = 0
            stdscr.nodelay(False)
            return
        print_practice(stdscr, setting)

# ========== Speed =======================================

def speed(stdscr, setting, authentication):
    
    # Set active to 1 to allow packets to be received
    setting['active'] = 1

    # Parameters for the blitz mode
    targets_to_hit = 10
    max_interval = 3
    min_interval = 0.7
    max_duration = 5
    min_duration = 1.5
    level = setting['difficulty'] - 1
    interval = (8 - level) / 8 * (max_interval - min_interval) + min_interval
    duration = ((8 - level) / 8 * (max_duration - min_duration) + min_duration) * 1000

    # Start timer
    start = time.time()

    # Start loop
    while (True):

        elapsed = time.time() - start

        # Generate targets and then publish every 'interval' seconds
        if (not isFull(setting['targets'])) and (targets_to_hit > 0):
            target_id = random.randint(0, setting['num_target'] - 1)
            while (setting['targets'][target_id] == 1):
                target_id = random.randint(0, setting['num_target'] - 1)
            if (elapsed > interval):
                start = time.time()
                setting['targets'][target_id] = 1
                packet = struct.pack('sfh', str(target_id+1).encode(), duration, 1)
                publish.single('cpu2tar', packet, 0, False, \
                    authentication['broker_ip'], \
                    auth={'username':authentication['user'], \
                        'password':authentication['pass']})
                targets_to_hit -= 1
    
        # Print practice page
        print_practice(stdscr, setting)
        stdscr.nodelay(True)
        key = stdscr.getch()
        if (key == curses.KEY_ENTER) or (key in [10, 13]): 
            setting['active'] = 0
            setting['total_points'] = 0
            stdscr.nodelay(False)
            return
        print_practice(stdscr, setting)