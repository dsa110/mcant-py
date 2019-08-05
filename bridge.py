import queue
import json
import mcant
import datetime
from os.path import dirname
from os.path import realpath
from pathlib import Path
import sys
TOP_OF_TREE = dirname(dirname(realpath(__file__)))
sys.path.append(str(Path(TOP_OF_TREE + '/jl_dsacode')))
import dsa_labjack as dlj
import hw_monitor as mon

# commands coming from the etcd
ETCD_MV = 'mv'
ETCD_ND1 = 'Pol1Noise'
ETCD_ND2 = 'Pol2Noise'

# commands readable by the labjack
LJ_MV = 'move'
LJ_ND = 'nd'
POL1_ON = 'a'
POL2_ON = 'b'

ARRAY_SIZE = 2
TRUE = 1
FALSE = 0

log_msg_q = queue.Queue()
mp_q = mon.Monitor_q("dsa-110-test-", log_msg_q)


class EtcdBridge:
    """ Convert UI etcd commands into tuples to integrate with the dsa labjack hwmc, convert hw
    monitor data to integrate with the etcd
    """

    def __init__(self, ant_num):
        """Create dictionary of labjacks on the network- use ant_num to extract specific antenna,
        create a dictionary with labjack names as keys and etcd names as values

        :param ant_num: number designating which antenna to get data from- read from yml file
        :type ant_num: integer
        :raise: KeyError, SystemExit
        """

        self.ant_num = ant_num
        devices = dlj.LabjackList(log_msg_q, mp_q, mcant.read_yaml('etcdConfig.yml')['SIM'])
        ants = devices.ants
        print("ants is:", ants)
        abes = devices.abes
        print("abes is:", abes)

        try:
            self.labjack  = ants[ant_num]
        except KeyError:
            mcant.dprint("__init__(): Error Finding a Handle to the Specified Labjack. Check Connection."
                         " ant_num = {}".format(ant_num), 'ERR')
            raise SystemExit
        self.lj_names = {'drive_state': 'drivestate',
                          'brake': 'brake',
                          'plus_limit': 'limit',
                          'minus_limit': 'limit',
                          'fan_err': 'fanerror',
                          'ant_el': 'el',
                          'nd1': 'polnoise',
                          'nd2': 'polnoise',
                          'foc_temp': 'foctemp',
                          'lna_a_current': 'lnacurrent',
                          'lna_b_current': 'lnacurrent',
                          'rf_a_power': 'rfpower',
                          'rf_b_power': 'rfpower',
                          'laser_a_voltage': 'laservolt',
                          'laser_b_voltage': 'laservolt',
                          'feb_a_current': 'febcurrent',
                          'feb_b_current': 'febcurrent',
                          'feb_a_temp': 'febtemp',
                          'feb_b_temp': 'febtemp',
                          'lj_temp': 'computertemp',
                          'psu_voltage': 'psuvolt'}

    def get_monitor_data(self):
        """Obtain labjack monitor data in a dictionary, call private method _remap. Add
         time (UTC) and sim (True in sim mode, False in real mode) keys. Convert and
        return changed dictionary into JSON string format

        :return: JSON string of labjack monitor data with converted key names and values in
        the form: {"key":"value"} or {"key":number|bool} or {"key":"[number, number]} or
        {"key":[bool, bool]}
        :rtype: String
        :raise: ValueError
        """

        time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
        read = mcant.read_yaml('etcdConfig.yml')
        sim = read['SIM']

        md_dict = self.labjack.get_data()
        new_dict = self._remap(md_dict)
        new_dict['number'] = self.ant_num
        new_dict['time'] = time
        new_dict['sim'] = sim

        try:
            md_json = json.dumps(new_dict)
        except ValueError:
            mcant.dprint("get_monitor_data(): JSON encode error. Check JSON."
                         "new_dict = {}".format(new_dict), 'ERR')

        return md_json

    def _remap(self, dict):
        """Private method- Take in dictionary of labjack monitor data and create a new
        dictionary with renamed keys to be input into the UI- access new names with
        lj_names{}. Assign corresponding labjack values to new keys. Create a value array
        of numbers or bools for cases in which two distinct labjack keys match up with
        one etcd key. Convert 0 and 1 values to be boolean values (0 is False, 1 is True).

        :param dict: Dictionary of the labjacks monitor data
        :type: Dictionary
        :return: Dictionary with renamed keys and array/boolean formatted values
        :rtype: Dictionary
        """

        new_dict = {}

        new_dict[self.lj_names['drive_state']] = dict['drive_state']
        new_dict[self.lj_names['ant_el']] = dict['ant_el']
        new_dict[self.lj_names['foc_temp']] = dict['foc_temp']
        new_dict[self.lj_names['lj_temp']] = dict['lj_temp']
        new_dict[self.lj_names['psu_voltage']] = dict['psu_voltage']

        if dict['fan_err'] == FALSE:
            new_dict[self.lj_names['fan_err']] = False
        elif dict['fan_err'] == TRUE:
            new_dict[self.lj_names['fan_err']] = True

        if dict['brake'] == FALSE:
            new_dict[self.lj_names['brake']] = False
        elif dict['brake'] == TRUE:
            new_dict[self.lj_names['brake']] = True

        pn_array = [0] * ARRAY_SIZE
        if dict['nd1'] == FALSE:
            pn_array[0] = False
        elif dict['nd1'] == TRUE:
            pn_array[0] = True
        if dict['nd2'] == FALSE:
            pn_array[1] = False
        elif dict['nd2'] == TRUE:
            pn_array[1] = True
        new_dict[self.lj_names['nd1']] = pn_array

        ft_array = [0] * ARRAY_SIZE
        ft_array[0] = dict['feb_a_temp']
        ft_array[1] = dict['feb_b_temp']
        new_dict[self.lj_names['feb_a_temp']] = ft_array

        fc_array = [0] * ARRAY_SIZE
        fc_array[0] = dict['feb_a_current']
        fc_array[1] = dict['feb_b_current']
        new_dict[self.lj_names['feb_a_current']] = fc_array

        lc_array = [0] * ARRAY_SIZE
        lc_array[0] = dict['lna_a_current']
        lc_array[1] = dict['lna_b_current']
        new_dict[self.lj_names['lna_a_current']] = lc_array

        rfp_array = [0] * ARRAY_SIZE
        rfp_array[0] = dict['rf_a_power']
        rfp_array[1] = dict['rf_b_power']
        new_dict[self.lj_names['rf_a_power']] = rfp_array

        lv_array = [0] * ARRAY_SIZE
        lv_array[0] = dict['laser_a_voltage']
        lv_array[1] = dict['laser_b_voltage']
        new_dict[self.lj_names['laser_a_voltage']] = lv_array

        lim_array = [0] * ARRAY_SIZE
        if dict['minus_limit'] == FALSE:
            lim_array[0] = False
        elif dict['minus_limit'] == TRUE:
            lim_array[0] = True
        if dict['plus_limit'] == FALSE:
            lim_array[1] = False
        elif dict['plus_limit'] == TRUE:
            lim_array[1] = True
        new_dict[self.lj_names['minus_limit']] = lim_array

        return new_dict

    def process(self, cmd):
        """Convert etcd commands into a format readable by the hardware script. If the
        value contains the move key, the private method _move_process is invoked. If
        the value contains a polarization noise key, the private method
        _polar_noise_process is invoked

        :param cmd: etcd value which is a dictionary with a cmd key as a command and a val
        key as a number or string
        :type: Dictionary
        """

        command = cmd['Cmd']
        if command == ETCD_MV:
            self._move_process(cmd)

        if command == ETCD_ND1 or command == ETCD_ND2:
            self._polar_noise_process(cmd)

    def _move_process(self, cmd):
        """Private method- Take in etcd value dictionary with the move command. Create
        tuple with labjack readable command and cmd value. Execute command to the labjack

        :param cmd: etcd value which is a dictionary with a cmd key as the move command
        and a val key as a number decribing the desired elevation
        :type: Dictionary
        """

        command_name = LJ_MV
        value = cmd['Val']

        mv_tuple = (command_name, value)

        self.labjack.execute_cmd(mv_tuple)

    def _polar_noise_process(self, cmd):
        """Private method- Take in etcd value dictionary with one of the two polarization
        noise commands. Create tuple with labjack readable command and cmd value. Execute
        command to the labjack

        :param cmd: etcd value which is a dictionary with a cmd key as the polarization
        noise command and a val key as a string of either "on" or "off"
        :type: Dictionary
        """

        command_name = LJ_ND
        command = cmd['Cmd']
        if command == ETCD_ND1:
            pol_id = POL1_ON
        elif command == ETCD_ND2:
            pol_id = POL2_ON

        pol_state = cmd['Val']

        nd_tuple = (command_name, pol_id, pol_state)

        self.labjack.execute_cmd(nd_tuple)





