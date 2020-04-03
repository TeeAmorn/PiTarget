import curses

# ========== Print Menu ==================================

def print_menu(stdscr, menu, current_row):
    
    # Clear window
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Print menu
    for idx, text in enumerate(menu):
        col = width // 2 - 3
        row = height // 2 - len(menu) // 2 + idx
        if idx == current_row:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(row, col, text)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(row, col, text)

    # Update page with new changes
    stdscr.refresh()

# ========== Print Config ================================

def print_config(stdscr, config, setting, current_row):
    
    # Clear window
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Print config
    for idx, text in enumerate(config):
        col = width // 2 - 15
        row = height // 2 - len(config) // 2 + idx
        if idx == current_row:
            if idx == len(config)-1:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(row, col, text)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(row, col, text)
                stdscr.attroff(curses.color_pair(1))
                if idx == 0: 
                    draw_slider(stdscr, row, col+24, setting['difficulty'], 1)
                if idx == 1: 
                    draw_slider(stdscr, row, col+24, setting['num_target'], 1)
        else:
            if idx == len(config)-1:
                stdscr.addstr(row, col, text)
            else:
                stdscr.addstr(row, col, text)
                if idx == 0: 
                    draw_slider(stdscr, row, col+24, setting['difficulty'], 0)
                if idx == 1: 
                    draw_slider(stdscr, row, col+24, setting['num_target'], 0)

    # Update page with new changes
    stdscr.refresh()

# ========== Print Slider ================================

def draw_slider(stdscr, row, col, val, selected):

    # Print slider
    if selected == 0:
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(row, col, ' < ')
        stdscr.attroff(curses.color_pair(1))
        stdscr.addstr(row, col+4, str(val))
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(row, col+6, ' > ')
        stdscr.attroff(curses.color_pair(1))
    else:
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(row, col, ' < ')
        stdscr.addstr(row, col+4, str(val))
        stdscr.addstr(row, col+6, ' > ')
        stdscr.attroff(curses.color_pair(1))

# ========== isFull Method ===============================

# Used to check whether all the targets in the list 'targets'
# have been turned on or not
def isFull(targets):
    lst = [x for x in targets if x==0]
    if not lst: return True
    else: return False

# ========== Print Pracatice =============================

def print_practice(stdscr, setting):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    col = width // 2
    row = height // 2
    stdscr.addstr(row, col-7, 'Score: ')
    score = str(setting['total_points'])
    stdscr.addstr(row, col+1, score)
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(row+1, col-2, 'Back')
    stdscr.attroff(curses.color_pair(1))
    stdscr.refresh()
