# Ariston to MQTT Bridge

This project connects an Ariston or Elco heating system to an MQTT server, allowing smart home enthusiasts and developers to integrate heating controls with home automation systems.

## How to Use

### Get Gateway ID (`get_gateway_id.py`)

The `get_gateway_id.py` script is used to obtain the gateway ID of your Ariston heating system. This information is needed to interface with the heating system programmatically.

```sh
python get_gateway_id.py --user YOUR_EMAIL --password YOUR_PASSWORD
```

Replace `YOUR_EMAIL` and `YOUR_PASSWORD` with your actual credentials for the Ariston heating system. Upon execution, this script will output the gateway ID.

### Start the Bridge (`aristo2mqtt.py`)

To start the bridge script `aristo2mqtt.py`, you will need to provide several parameters:

```sh
python aristo2mqtt.py --server MQTT_SERVER_ADDRESS --user MQTT_USER --password MQTT_PASSWORD --user YOUR_EMAIL --password YOUR_PASSWORD
```

Here is the explanation of the parameters:

- `--server`: This is the MQTT server's address to which the bridge will connect.
- `--user`: MQTT username needed for authentication with the MQTT server.
- `--password`: MQTT password for the corresponding username.
- `--user`: Your email address used to log in to the Ariston heating system.
- `--password`: Your password for the Ariston heating system.
- `--gwid`: The gateway ID of your Ariston heating system.
 
### Docker Setup

The `Dockerfile` in this repository makes it simple to containerize and run the bridge.

To build the Docker image locally, navigate to the directory containing your Dockerfile and run:

```sh
docker build -t ariston2mqtt .
```

Once the image is built, you can run a container from this image. The bridge runs inside the container, using environment variables that map to the script parameters:

```sh
docker run -d \
  --name ariston2mqtt \
  -e MQTT_SERVER="MQTT_SERVER_ADDRESS" \
  -e MQTT_USER="MQTT_USER" \
  -e MQTT_PASSWORD="MQTT_PASSWORD" \
  -e USER="YOUR_EMAIL" \
  -e PASSWORD="YOUR_PASSWORD" \
  -e GWID="GATEWAY_ID" \
  ariston2mqtt
```

Replace `MQTT_SERVER_ADDRESS`, `MQTT_USER`, `MQTT_PASSWORD`, `YOUR_EMAIL`, `YOUR_PASSWORD`, and `GATEWAY_ID` with their respective values.

The container will automatically execute the `entrypoint.sh` script, which should start the `aristo2mqtt.py` script with the supplied environment variables as parameters.

## License

MIT License  https://opensource.org/license/mit/