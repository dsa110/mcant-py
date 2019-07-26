from os.path import dirname
from os.path import realpath
import sys
TOP_OF_TREE = dirname(dirname(realpath(__file__)))
sys.path.insert(0, TOP_OF_TREE + '\jl_dsacode')
import dsa_labjack as dlj
import mcant

class EtcdToArray:

    def __init__(self, key, cmd):
        #key is a string (ex. '/cmd/ant/0-N') and cmd is a dictionary (ex. {'cmd': 'mv', 'val:22.3'})
        self.key = key
        self.cmd = cmd

    def process(self):
        number = int(self.key[9:])
        if number == 0:
            print("applies to all antenna")
            #apply code to all 110 antenna
        elif number <= 110:
            print("applies to antenna: ", number)
            #apply code only to ants[key]
        else:
            print("0: control all antenna, 1-110: control a specific antenna")

        if self.cmd['cmd'] == 'mv':
            return self.__move_process()

        if self.cmd['cmd'] == 'Pol1Noise' or self.cmd['cmd'] == 'Pol2Noise':
            return self.__switch_process()

    def __move_process(self):
        mv_array = [0] * 2
        value = self.cmd['val']
        mv_array[0] = 'move'
        mv_array[1] = value
        return mv_array

    def __switch_process(self):
        nd_array = [0] * 3
        nd_array[0] = 'nd'
        value = self.cmd['val']
        if self.cmd['cmd'] == 'Pol1Noise':
            nd_array[1] = 'a'
        elif self.cmd['cmd'] == 'Pol2Noise':
            nd_array[1] = 'b'
        if value == 'on':
            nd_array[2] = 'on'
        elif value == 'off':
            nd_array[2] = 'off'
        return nd_array


if __name__ == '__main__':
    key = '/cmd/ant/1'
    cmd = {'cmd':'Pol2Noise', 'val': 'on'}
    etcd_command = EtcdToArray(key, cmd)
    now =  EtcdToArray.process(etcd_command)
    print(now)

