import paho.mqtt.client as mqtt
import time
import sys
import argparse
import ariston
import logging

class NonEmptyStringAction(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        if isinstance(values, str) and not values.strip():
            raise argparse.ArgumentTypeError(
                f"{option_string} cannot be an empty string"
            )
        setattr(args, self.dest, values)


# Parse command line arguments for configuration
parser = argparse.ArgumentParser(description='Heater MQTT Client')
parser.add_argument('--mqttserver', action=NonEmptyStringAction, required=True, help='MQTT server address')
parser.add_argument('--mqttuser', required=True, help='MQTT user')
parser.add_argument('--mqttpassword', required=True, help='MQTT password')
parser.add_argument('--user', action=NonEmptyStringAction, required=True, help='Thermo User')
parser.add_argument('--password', action=NonEmptyStringAction, required=True, help='Thermo Password')
parser.add_argument('--gwid', action=NonEmptyStringAction, required=True, help='Thermo Gateway ID')
parser.add_argument('--update-interval', help='Update Interval in seconds')
args = parser.parse_args()




logger = logging.getLogger('aristo2mqtt')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Constants
MQTT_TOPIC_PUBLISH = 'heater/status'
MQTT_TOPIC_PREFIX= 'heater/status/'
MQTT_TOPIC_SUBSCRIBE_PREFIX = 'heater/'
MQTT_TOPIC_SUBSCRIBE = 'heater/comfort_temperature'
UPDATE_INTERVAL = 600 # Update heater state every 60 seconds

if args.update_interval:
    UPDATE_INTERVAL = int(args.update_interval)

# Handler for successful MQTT connection
def on_connect(client, userdata, flags, rc):
    logger.debug("Connected to MQTT server")
    client.subscribe(MQTT_TOPIC_SUBSCRIBE)

# Handler for received messages from MQTT
def on_message(client, userdata, msg):
    logger.info ("received message:" + msg.topic + ":" + str(msg.payload))
    device = userdata
    if msg.topic == MQTT_TOPIC_SUBSCRIBE:
        try:
            new_temp = float(msg.payload)
            device.set_comfort_temp(new_temp, 1)
        except ValueError:
            logger.error("Received non-float value for temperature")
        except Exception as e:
            logger.error(f"Error setting new comfort temperature: {e}")

# Try to connect to the heater
def connect_heater():
    try:
        device = ariston.hello(args.user, args.password,args.gwid, True, "en-US")
        return device
    except Exception as e:
        logger.error(f"Error connecting to the heater: {e}")
        return None

# Publish heater status
def publish_heater_status(client, device):
    try:
        topics = {
            "zone_numbers": str(device.zone_numbers),
            "is_plant_in_heat_mode": device.is_plant_in_heat_mode,
            "is_flame_on_value": device.is_flame_on_value,
            "water_heater_current_temperature": device.water_heater_current_temperature,
            "water_heater_target_temperature": device.water_heater_target_temperature,
            "water_heater_maximum_temperature": device.water_heater_maximum_temperature,
            "water_heater_minimum_temperature": device.water_heater_minimum_temperature,
            "comfort_temperature": device.get_comfort_temp_value(1),
            "measured_temperature": device.get_measured_temp_value(1),
            "central_heating_total_energy_consumption": device.central_heating_total_energy_consumption,
            "ch_flow_temp_value": device.ch_flow_temp_value,
            "outside_temp_value": device.outside_temp_value,
        }
        for topic_suffix, value in topics.items():
            full_topic = f"{MQTT_TOPIC_PREFIX}{topic_suffix}"
            logger.debug("publishing:" + full_topic + ":" + str(value))
            client.publish(full_topic, value)
    except Exception as e:
        logger.error(f"Error publishing heater status: {e}")
def publish_heater_setters(client, device):
    try:
        topics = {
            "comfort_temperature": device.get_comfort_temp_value(1)
        }
        for topic_suffix, value in topics.items():
            full_topic = f"{MQTT_TOPIC_SUBSCRIBE_PREFIX}{topic_suffix}"
            logger.debug("publishing:" + full_topic + ":" + str(value))
            client.publish(full_topic, value)
    except Exception as e:
        logger.error(f"Error publishing heater status: {e}")

# Initialize MQTT client
def setup_mqtt_client(server, user, password, device):
    client = mqtt.Client(userdata=device)
    client.username_pw_set(user, password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(server)
    return client

def main():
    device = connect_heater()
    firstrun = True
    if not device:
        sys.exit("Failed to connect to the heater device. Exiting.")

    client = setup_mqtt_client(args.mqttserver, args.mqttuser, args.mqttpassword, device)
    client.loop_start()




    try:
        while True:
            if device is None:
                logger.info("Reconnecting to the heater...")
                device = connect_heater()
                if device:
                    client.user_data_set(device)
            logger.debug("update_state")
            device.update_state()
            logger.debug("update_energy")
            device.update_energy()
            logger.debug("publishing")
            publish_heater_status(client, device)
            if firstrun:
                publish_heater_setters(client, device)
                firstrun = False
            time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        logger.error("Program interrupted by user, stopping...")
    finally:
        client.loop_stop()
        logger.error("Disconnected from MQTT server")

if __name__ == '__main__':
    main()

