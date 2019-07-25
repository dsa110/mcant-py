#import hwmc_logging as log
#import commands as cmds
#import dsa_labjack as dlj
import time
from threading import Thread
import threading
import queue
#import hw_monitor as mon
import os
#from monitor_server import MpServer
from os.path import dirname
from os.path import realpath
import sys
TOP_OF_TREE = dirname(dirname(realpath(__file__)))
sys.path.insert(0, TOP_OF_TREE + '\jl_dsacode')
import hwmc_logging as log
import commands as cmds
import dsa_labjack as dlj
import hw_monitor as mon
from labjack import ljm
MODULE = os.path.basename(__file__)

# Set up some parameters to control execution, memory allocation, and logging

SIM = False     # Simulation mode of LabJacks

ANT_CMD_Q_DEPTH = 5

log_level = log.INFO

# --------- Start main script ------------
thread_count = 1    # This starts with main thread

# Start logging
logfile_prefix = "dsa-110-test-"
log_msg_q = queue.Queue()
level = log.ALL
hw_log = log.HwmcLog(logfile_prefix, log_msg_q, level)
log_thread = Thread(target=hw_log.logging_thread)
log_thread.start()
thread_count += 1

# Start monitor point queue
mp_q = mon.Monitor_q("dsa-110-test-", log_msg_q)
monitor_thread = Thread(target=mp_q.run, name='mp_q-thread')
monitor_thread.start()
thread_count += 1




def is_dict_empty(dict):

    result = True
    if dict == None:
        print("The dictionary object does not exist")
    elif not dict:
        print("The dictionary is empty")
    else:
        print("The dictionary is not empty")
        result = False
    return result

if __name__ == "__main__":
    devices = dlj.LabjackList(log_msg_q, mp_q, simulate=SIM)
    ants = devices.ants

    is_dict_empty(ants)
    print("ants: ", ants)


    labjack = ants[1]
    print("labjack is", labjack)
    default_data = labjack.monitor_points
    print("default data is", default_data)

    labjack_data = labjack.get_data()
    print("labjack data is", labjack_data)

    ndcmd = ('nd', 'a', 'on')
    labjack.execute_cmd(ndcmd)

    labjack_data = labjack.get_data()
    print("labjack data is", labjack_data)
