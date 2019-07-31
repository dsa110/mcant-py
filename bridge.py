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
import json
import mcant
import datetime

ETCD_MV = 'mv'
ETCD_ND1 = 'Pol1Noise'
ETCD_ND2 = 'Pol2Noise'
LJ_MV = 'move'
LJ_ND = 'nd'
POL1_ON = 'a'
POL2_ON = 'b'
ARRAY_SIZE = 2
TRUE = 1
FALSE = 0

SIM = False     # Simulation mode of LabJacks


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

        self.ant_num = ant_num
        devices = dlj.LabjackList(log_msg_q, mp_q, simulate=SIM)
        ants = devices.ants
        labjack = ants[ant_num]
        self.labjack  = labjack
        ljnames = {}
        ljnames['drive_state'] = 'drivestate'
        ljnames['brake'] = 'brake'
        ljnames['plus_limit'] = 'limit'
        ljnames['minus_limit'] = 'limit'
        ljnames['fan_err'] = 'fanerror'
        ljnames['ant_el'] = 'el'
        ljnames['nd1'] = 'polnoise'
        ljnames['nd2'] = 'polnoise'
        ljnames['foc_temp'] = 'foctemp'
        ljnames['lna_a_current'] = 'lnacurrent'
        ljnames['lna_a_current'] = 'lnacurrent'
        ljnames['rf_a_power'] = 'rfpower'
        ljnames['rf_b_power'] = 'rfpower'
        ljnames['laser_a_voltage'] = 'laservolt'
        ljnames['laser_b_voltage'] = 'laservolt'
        ljnames['feb_a_current'] = 'febcurrent'
        ljnames['feb_b_current'] = 'febcurrent'
        ljnames['feb_a_temp'] = 'febtemp'
        ljnames['feb_b_temp'] = 'febtemp'
        ljnames['lj_temp'] = 'computertemp'
        ljnames['psu_voltage'] = 'psuvolt'
        self.ljnames = ljnames

    def get_monitor_data(self):

        time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
        read = mcant.read_yaml('etcdConfig.yml')
        sim = read['SIM']

        md_dict = self.labjack.get_data()
        newDict = self._remap(md_dict)
        newDict['number'] = self.ant_num
        newDict['time'] = time
        newDict['sim'] = sim

        md_json = json.dumps(newDict)

        return md_json

    def _remap(self, dict):

        newDict = {}

        newDict[self.ljnames['drive_state']] = dict['drive_state']
        newDict[self.ljnames['ant_el']] = dict['ant_el']
        newDict[self.ljnames['foc_temp']] = dict['foc_temp']
        newDict[self.ljnames['lj_temp']] = dict['lj_temp']
        newDict[self.ljnames['psu_voltage']] = dict['psu_voltage']

        if dict['fan_err'] == FALSE:
            newDict[self.ljnames['fan_err']] = False
        elif dict['fan_err'] == TRUE:
            newDict[self.ljnames['fan_err']] = True

        if dict['brake'] == FALSE:
            newDict[self.ljnames['brake']] = False
        elif dict['brake'] == TRUE:
            newDict[self.ljnames['brake']] = True

        pn = [0] * ARRAY_SIZE
        if dict['nd1'] == FALSE:
            pn[0] = False
        elif dict['nd1'] == TRUE:
            pn[0] = True
        if dict['nd2'] == FALSE:
            pn[1] = False
        elif dict['nd2'] == TRUE:
            pn[1] = True
        newDict[self.ljnames['nd1']] = pn

        ft = [0] * ARRAY_SIZE
        ft[0] = dict['feb_a_temp']
        ft[1] = dict['feb_b_temp']
        newDict[self.ljnames['feb_a_temp']] = ft

        fc = [0] * ARRAY_SIZE
        fc[0] = dict['feb_a_current']
        fc[1] = dict['feb_b_current']
        newDict[self.ljnames['feb_a_current']] = fc

        lc = [0] * ARRAY_SIZE
        lc[0] = dict['lna_a_current']
        lc[1] = dict['lna_b_current']
        newDict[self.ljnames['lna_a_current']] = lc

        rfp = [0] * ARRAY_SIZE
        rfp[0] = dict['rf_a_power']
        rfp[1] = dict['rf_b_power']
        newDict[self.ljnames['rf_a_power']] = rfp

        lv = [0] * ARRAY_SIZE
        lv[0] = dict['laser_a_voltage']
        lv[1] = dict['laser_b_voltage']
        newDict[self.ljnames['laser_a_voltage']] = lv

        lim = [0] * ARRAY_SIZE
        if dict['minus_limit'] == FALSE:
            lim[0] = False
        elif dict['minus_limit'] == TRUE:
            lim[0] = True
        if dict['plus_limit'] == FALSE:
            lim[1] = False
        elif dict['plus_limit'] == TRUE:
            lim[1] = True
        newDict[self.ljnames['minus_limit']] = lim

        return newDict


    def process(self, key, cmd):
        # Main function, call private helper functions to convert move and polar noise commands

        command = cmd['Cmd']
        if command == ETCD_MV:
            self._move_process(cmd)

        if command == ETCD_ND1 or command == ETCD_ND2:
            self._polar_noise_process(cmd)

    def _move_process(self, cmd):
        # Private helper function, convert etcd move command into tuple then execute to the labjack

        command_name = LJ_MV
        value = cmd['Val']

        mv_tuple = (command_name, value)

        self.labjack.execute_cmd(mv_tuple)

    def _polar_noise_process(self, cmd):
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




