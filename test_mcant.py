import mcant
import unittest
from unittest.mock import Mock

class TestMcant(unittest.TestCase):

    # This class is applying unit tests to the functions found in mcant.py

    def test_read_yaml(self):
        # Test if mcant.read_yaml returns the contents of the yaml file.

        result1 = mcant.read_yaml('etcdConfig.yml')
        self.assertEqual(result1, {'endpoints': ['192.168.1.132:2379'], 'timeout': '1s', 'command': '/cmd/ant/', 'ant_num' : 1, 'SIM' : False})

    def test_dprint(self):
        # Test if mcant.dprint prints in correct format contingent on a True boolean parameter, the return is None.

        result20 = mcant.dprint("cmd key= {}, cmd val= {}".format("key", "val"), 'INFO', True)

        print("expected: \nINFO: hello")
        print("result:")
        result2 = mcant.dprint("hello", "INFO", True)
        self.assertIsNone(result2)
        print("\n")

        print("expected:")
        print("result:")
        result3 = mcant.dprint("hello", "INFO", False)
        self.assertIsNone(result3)
        print("\n")

        print("expected: \nWARN: this is invalid")
        print("result:")
        result4 = mcant.dprint("this is invalid", "WARN", True)
        self.assertIsNone(result4)
        print("\n")

    def test_parse_endpoint(self):
        # Test if mcant.parse_endpoint returns tuple format of the endpoint from the list.

        result5 = mcant.parse_endpoint(["123:456"])
        self.assertEqual(result5, ('123', '456'))

        result6 = mcant.parse_endpoint(["192.168.1.132:2379"])
        self.assertEqual(result6, ('192.168.1.132','2379'))

        result7 = mcant.parse_endpoint(["hgd7325642gdhsd:asghr8732rghe"])
        self.assertEqual(result7, ('hgd7325642gdhsd', 'asghr8732rghe'))

        result8 = mcant.parse_endpoint(["1:2", "3:4"])
        self.assertEqual(result8, ('1', '2'))


    def test_parse_value(self):
        # Test if mcant.parse_value returns a key, value dictionary from the JSON string.

        result9 = mcant.parse_value('{"key":"value"}')
        self.assertEqual(result9, {'key':'value'})

        result10 = mcant.parse_value('{"key": true}')
        self.assertEqual(result10, {'key': True})

        result11 = mcant.parse_value('{"key": false}')
        self.assertEqual(result11, {'key': False})

        result12 = mcant.parse_value('{"/cmd/ant/1" : "\'mv\', 34.2"}')
        self.assertEqual(result12, {'/cmd/ant/1':"'mv', 34.2"})

        result13 = mcant.parse_value('{"/cmd/ant/0" : "\'Pol1Noise\', off"}')
        self.assertEqual(result13, {'/cmd/ant/0': "'Pol1Noise', off"})

        print('expected: \nERR: parse_value(): JSON Decode Error. Check JSON. value= {"hello"}')
        print("result:")
        result14 = mcant.parse_value('{"hello"}')
        self.assertEqual(result14, {})
        print('\n')


if __name__ == '__main__':
    unittest.main()