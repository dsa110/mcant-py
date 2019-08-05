import mcant
import bridge as br

beb_br = br.EtcdBridge(mcant.read_yaml('etcdConfig.yml')['ant_num'])

beb_dict = beb_br.get_monitor_data()

print(beb_dict)