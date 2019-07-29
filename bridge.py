from threading import Thread
import queue
from os.path import dirname
from os.path import realpath
import sys
TOP_OF_TREE = dirname(dirname(realpath(__file__)))
sys.path.insert(0, TOP_OF_TREE + '\jl_dsacode')
import hwmc_logging as log
import dsa_labjack as dlj
import hw_monitor as mon


ant_num = 1
ETCD_MV = 'mv'
ETCD_ND1 = 'Pol1Noise'
ETCD_ND2 = 'Pol2Noise'
LJ_MV = 'move'
LJ_ND = 'nd'
POL1_ON = 'a'
POL2_ON = 'b'

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

class ConvertEtcd:
    # Convert UI etcd commands into a tuple to integrate with the dsa labjack hwmc

    def __init__(self, ant_num):
        # Create dictionary of labjacks on the network, focus on specific- or all antenna

        devices = dlj.LabjackList(log_msg_q, mp_q, simulate=SIM)
        ants = devices.ants
        labjack = ants[ant_num]
        self.ant__num = ant_num
        self.labjack  = labjack

    def process(self, key, cmd):
        # Main function, call private helper functions to convert move and polar noise commands

        command = cmd['Cmd']
        if command == ETCD_MV:
            self.__move_process(cmd)

        if command == ETCD_ND1 or command == ETCD_ND2:
            self.__polarnoise_process(cmd)

    def __move_process(self, cmd):
        # Private helper function, convert etcd move command into tuple then execute to the labjack

        command_name = LJ_MV
        value = cmd['Val']

        mv_tuple = (command_name, value)

        self.labjack.execute_cmd(mv_tuple)

    def __polarnoise_process(self, cmd):
        # Private helper function, convert etcd polar noise command into tuple then execute to the labjack

        command_name = LJ_ND
        command = cmd['Cmd']
        if command == ETCD_ND1:
            pol_id = POL1_ON
        elif command == ETCD_ND2:
            pol_id = POL2_ON

        pol_state = cmd['Val']

        nd_tuple = (command_name, pol_id, pol_state)

        self.labjack.execute_cmd(nd_tuple)



