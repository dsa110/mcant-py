from threading import Thread
import queue
import os
from os.path import dirname
from os.path import realpath
import sys
TOP_OF_TREE = dirname(dirname(realpath(__file__)))
sys.path.insert(0, TOP_OF_TREE + '\jl_dsacode')
import hwmc_logging as log
import commands as cmds
import dsa_labjack as dlj
import hw_monitor as mon
import unittest

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



#class TestLabjack(unittest.TestCase):

    #def test_switch_nd(self):
        #ndcmd = ('nd', 'a', 'on')
        #labjack.execute_cmd(ndcmd)
        #self.assertEqual(labjack_data['nd1'], 1)

        #ndcmd = ('nd', 'b', 'on')
        #labjack.execute_cmd(ndcmd)
        #self.assertEqual(labjack_data['nd2'], 1)

        #ndcmd = ('nd', 'ab', 'on')
        #labjack.execute_cmd(ndcmd)
        #self.assertEqual(labjack_data['nd1'], 1)
        #self.assertEqual(labjack_data['nd2'], 1)



def is_dict_empty(dict):

    if dict == None:
        print("The dictionary object does not exist")
    elif not dict:
        print("The dictionary is empty")
    else:
        print("The dictionary is not empty")


if __name__ == "__main__":
    #unittest.main()
    devices = dlj.LabjackList(log_msg_q, mp_q, simulate=SIM)
    ants = devices.ants

    labjack = ants[1]
    print("labjack is", labjack)

    labjack_data = labjack.get_data()

    is_dict_empty(ants)
    print("ants: ", ants)


    labjack_data = labjack.get_data()
    print("labjack data is", labjack_data)

    print(labjack_data['ant_el'])

    ndcmd = ('nd', 'b', 'off')
    labjack.execute_cmd(ndcmd)
    labjack_data = labjack.get_data()
    print("labjack data is", labjack_data)

    #movecmd = ('move', 'off')
    #labjack.execute_cmd(movecmd)


