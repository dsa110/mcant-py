#import hwmc_logging as log
#import commands as cmds
#import dsa_labjack as dlj
import time
from threading import Thread
import threading
import Queue
#import hw_monitor as mon
import os
#from monitor_server import MpServer
from os.path import dirname
from os.path import realpath
import sys
TOP_OF_TREE = dirname(dirname(realpath(__file__)))
print(TOP_OF_TREE)
sys.path.insert(0, TOP_OF_TREE + '\jl_dsacode')
print(sys.path)
import hwmc_logging as log
print("1")
import commands as cmds
print("2")
import dsa_labjack as dlj
print("4")
import hw_monitor as mon
print("5")
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






def ant_array_length(x):
    non_zero = False
    if len(x) > 0:
        non_zero = True

if __name__ == "__main__":
    print("finished import")
    #devices = dlj.LabjackList(log_msg_q, mp_q, simulate=SIM)
    print("got devices")
    #ants = devices.ants

    #if ant_array_length(ants):
     #   print("array length is greater than zero")
    #else:
     #   print("error: array length is zero")