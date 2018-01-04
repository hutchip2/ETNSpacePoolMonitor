#!/usr/bin/env python

"""file docstring"""

import json
import time
import sys
import datetime
import curses
from curses import wrapper
import requests
from scitools.aplotter import plot

def initialize(screen):
    """function docstring"""
    height, width = screen.getmaxyx()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    screen.border('|', '|', '-', '-', '|', '|', '|', '|')
    title = 'pool.etn.spacepools.org'
    screen.addstr(2, (width/2)-len(title)/2, title)
    draw_borders(screen)
    screen.addstr(5, (int(width * 0.33)/2)-4, 'HASHRATE')
    screen.addstr(5, int(width * 0.33)+(int(width * 0.33)/2)-3, 'BALANCE')
    screen.addstr(5, int(width * 0.66)+(int(width * 0.33)/2)-2, 'PAID')
    screen.addstr(57, int(width / 2) - 5, 'STATISTICS')
    screen.addstr(59, int((width / 4) - 4), 'HASHRATE')
    screen.addstr(59, int((width / 2) + int(width/4)) - 4, 'PAYMENTS')
    github_url = 'https://github.com/hutchip2'
    screen.addstr(height-2, (width/2)-(len(github_url)/2), github_url)
    screen.refresh()
    while True:
        try:
            update_summary(screen)
        except ValueError:
            time.sleep(10)

def draw_borders(screen):
    """function docstring"""
    height, width = screen.getmaxyx()
    for i in range(4, 11):
        screen.addstr(i, int(width * 0.33), '|')
        screen.addstr(i, int(width * 0.66), '|')
    for i in range(1, width-1):
        screen.addstr(4, i, '=')
        screen.addstr(6, i, '-')
        screen.addstr(10, i, '=')
        screen.addstr(12, i, '-')
        screen.addstr(33, i, '=')
        screen.addstr(35, i, '-')
        screen.addstr(56, i, '=')
        screen.addstr(58, i, '-')
        screen.addstr(60, i, '-')
        screen.addstr(height-3, i, '-')
    screen.addstr(59, int(width / 2), '|')
    for i in range(61, height-2):
        screen.addstr(i, int(width / 2), '|')
    screen.border('|', '|', '-', '-', '|', '|', '|', '|')
    github_url = 'https://github.com/hutchip2'
    screen.addstr(height-2, (width/2)-(len(github_url)/2), github_url)

def clear_lines(screen):
    """function docstring"""
    screen.move(8, 1)
    screen.clrtoeol()
    screen.move(11, 1)
    screen.clrtoeol()
    screen.move(34, 1)
    screen.clrtoeol()
    screen.move(61, 1)
    screen.clrtobot()

def update_summary(screen):
    """function docstring"""
    raw = requests.get(POOL_URL)
    response = json.loads(raw.text)
    if raw.status_code == 200:
        clear_lines(screen)
        update_hashrate(screen, response)
        update_balance(screen, response)
        update_paid(screen, response)
        update_hashrate_graph(screen, response)
        update_payments_graph(screen, response)
        update_statistics(screen, response)
        draw_borders(screen)
        screen.move(screen.getmaxyx()[0]-1, screen.getmaxyx()[1]-1)
        screen.refresh()
    try:
        time.sleep(10)
    except KeyboardInterrupt:
        sys.exit(0)

def update_hashrate(screen, response):
    """function docstring"""
    hashrate = str(response['stats']['hashrate']) + '/sec'
    current = 'Current: %s' % hashrate
    width = screen.getmaxyx()[1]
    ypos = (int(width * 0.33) / 2)-(len('Current: ' + hashrate) / 2)
    screen.addstr(8, ypos, 'Current: ', curses.color_pair(1))
    screen.addstr(8, ypos + 9, hashrate, curses.color_pair(2))

def update_balance(screen, response):
    """function docstring"""
    balance = str(float(response['stats']['balance']) / 100) + ' ETN'
    pending = 'Pending: %s' % balance
    width = screen.getmaxyx()[1]
    screen.addstr(8, (int(width * 0.33) + (int(width * 0.33)/2))-(len(pending)/2), pending)

def update_paid(screen, response):
    """function docstring"""
    #payments = [x.encode('UTF8') for x in response['payments']]
    payments = [float(str(rate[1]).encode('UTF8')) for rate in response['charts']['payments']]
    timestamps = [float(str(rate[0]).encode('UTF8')) for rate in response['charts']['payments']]
    today = 'Today: %s' % str(get_intraday_paid(payments, timestamps)) + ' ETN'
    width = screen.getmaxyx()[1]
    screen.addstr(8, int(width * 0.66)+(int(width * 0.33)/2)-(len(today)/2), today)

def update_hashrate_graph(screen, response):
    """function docstring"""
    hashrates = [rate[1] for rate in response['charts']['hashrate']]
    timestamps = [rate[0] for rate in response['charts']['hashrate']]
    hashrates_start = datetime.datetime.fromtimestamp(timestamps[0]).strftime('%b %d @ %-I:%M %p')
    last_timestamp = timestamps[len(timestamps)-1]
    hashrates_stop = datetime.datetime.fromtimestamp(last_timestamp).strftime('%b %d @ %-I:%M %p')
    title = hashrates_start + ' - ' + hashrates_stop
    screen.addstr(11, 3, 'Hashrate (H/sec)')
    screen.addstr(11, screen.getmaxyx()[1] - len(title) - 2, title)
    graph = plot(timestamps, hashrates, output=str)
    lines = graph.split('\n')
    for i in range(1, len(lines)-1):
        screen.addstr(13 + i, (screen.getmaxyx()[1] - len(lines[0]))/2, lines[i])

def update_payments_graph(screen, response):
    """function docstring"""
    payments = [float(str(rate[1]).encode('UTF8')) for rate in response['charts']['payments']]
    timestamps = [float(str(rate[0]).encode('UTF8')) for rate in response['charts']['payments']]
    payments_start = datetime.datetime.fromtimestamp(timestamps[0])
    payments_start = payments_start.strftime('%b %d @ %-I:%M %p')
    payments_stop = datetime.datetime.fromtimestamp(timestamps[len(timestamps)-1])
    payments_stop = payments_stop.strftime('%b %d @ %-I:%M %p')
    title = payments_start + ' - ' + payments_stop
    screen.addstr(34, 3, 'Payments (ETN)')
    screen.addstr(34, screen.getmaxyx()[1] - len(title) - 2, title)
    graph = plot(timestamps, payments, output=str)
    lines = graph.split('\n')
    lines[1] = modify_minmax(lines[1])
    lines[len(lines)-2] = modify_minmax(lines[len(lines)-2])
    for i in range(1, len(lines)-1):
        screen.addstr(36 + i, (screen.getmaxyx()[1] - len(lines[0]))/2, lines[i])

def update_statistics(screen, response):
    """function docstring"""
    payments = [float(str(rate[1]).encode('UTF8')) for rate in response['charts']['payments']]
    timestamps = [float(str(rate[0]).encode('UTF8')) for rate in response['charts']['payments']]
    count = 0
    total_seconds = 0
    for i in range(0, len(timestamps)-1):
        if i % 2 == 0:
            start = datetime.datetime.fromtimestamp(timestamps[i])
            stop = datetime.datetime.fromtimestamp(timestamps[i+1])
            total_seconds += (stop - start).total_seconds()
            count += 1
    avg_payment_interval = time.strftime('%H:%M:%S', time.gmtime(total_seconds / count))
    avg_payment_interval = 'Average Payment Interval: ' + avg_payment_interval
    payments_total = 0
    for payment in payments:
        payments_total += float(payment)
    avg_payment = payments_total / len(payments)
    avg_payment = 'Average Payment: ' + str(round(avg_payment/100, 2)) + ' ETN'
    last_share = datetime.datetime.fromtimestamp(float(response['stats']['lastShare']))
    last_share = datetime.datetime.now() - last_share
    last_share = str(last_share.seconds // 60 % 60) + ' minute ago'
    last_share = '< 1 minute ago' if last_share == 0 else last_share
    total_paid = 'Total Paid: ' + str(round(float(response['stats']['paid'])/100, 2)) + ' ETN'
    hashes_submitted = str(round(float(response['stats']['hashes'])/1000000, 2)) + ' MH'
    screen.addstr(62, int(screen.getmaxyx()[1] / 2) + 3, avg_payment_interval)
    screen.addstr(64, int(screen.getmaxyx()[1] / 2) + 12, avg_payment)
    screen.addstr(66, int(screen.getmaxyx()[1] / 2) + 17, total_paid)
    screen.addstr(62, 5, 'Last Share Submitted: ' + last_share)
    screen.addstr(64, 3, 'Total Hashes Submitted: ' + hashes_submitted)

def modify_minmax(line):
    """function docstring"""
    if '+' in line:
        end = -1
        for i in range(line.find('+')+1, len(line)):
            if line[i].isdigit() is False:
                end = i
                break
        maximum = line[line.find('+')+1 : end]
        after = line.find(maximum) + len(maximum)
        maximum = round(float(maximum) / 100, 2)
        return line[:line.find('+')+1] + str(maximum) + line[after:]
    return line

def get_intraday_paid(payments, timestamps):
    """function docstring"""
    daily_total = 0
    for i in range(0, len(payments)):
        timestamp = datetime.datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d')
        if timestamp == datetime.datetime.today().strftime('%Y-%m-%d'):
            daily_total += float(payments[i])
    return daily_total / 100

POOL_URL = ''
if len(sys.argv) == 2:
    POOL_URL = 'https://api.etn.spacepools.org/v1/stats/address/' + sys.argv[1]
    wrapper(initialize)
else:
    sys.exit(1)
