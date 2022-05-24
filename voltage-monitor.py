#!/usr/bin/env python3

import lzma
import time
import os

def find_sensors():
    root = "/sys/devices/pci0000:00/0000:00:1f.3/i2c-0/0-002d/hwmon/hwmon3"
    devs = [1, 2, 3, 4, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 20]
    
    return { x: f'{root}/in{x}_input' for x in devs }

def read_sensors(sensors):
    row = [f'{time.time():.1f}']
    for dev, path in sensors.items():
        try:
            value = open(path, 'r').read().strip()
        except IOError:
            value = ''

        row.append(value)

    return ','.join(row) + '\n'

log_root = '/opt/voltage-monitor/logs'
def get_log_name():
    return log_root + '/' + time.strftime('%Y%m%d-%H') + '.csv.xz'

os.makedirs(log_root, exist_ok=True)

sensors = find_sensors()

log_name = log_fp = None

while True:
    ts = time.time()
    new_log_name = get_log_name()
    if new_log_name != log_name:
        log_name = new_log_name
        if log_fp is not None:
            log_fp.close()

        nonce = 0
        while True:
            real_log_name = f'{log_name}.{nonce}' if nonce else log_name
            if os.path.exists(real_log_name):
                nonce += 1
            else:
                break
        log_fp = lzma.open(real_log_name, 'wt')
    log_fp.write(read_sensors(sensors))
    time.sleep(1 - (time.time() - ts))
