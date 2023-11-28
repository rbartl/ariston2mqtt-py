import argparse
import ariston

parser = argparse.ArgumentParser(description='Heater MQTT Client')
parser.add_argument('--user', required=True, help='Thermo Username')
parser.add_argument('--password', required=True, help='Thermo Password')
args = parser.parse_args()

raw_devices = ariston.discover(args.user, args.password)

print(f"Your Gateway ID is: {raw_devices[0]['gw']}")
