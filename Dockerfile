FROM python:3.12


RUN apt remove -y  libtiff*
RUN pip install --upgrade pip


WORKDIR /app

COPY requirements.txt .
COPY aristo2mqtt.py .
COPY get_gateway_id.py .
COPY entrypoint.sh .
COPY get_gateway_id.py .

RUN chmod 755 entrypoint.sh

RUN pip install --no-cache-dir -r requirements.txt

ENV MQTT_SERVER=""
ENV MQTT_USER=""
ENV MQTT_PASSWORD=""
ENV USER=""
ENV PASSWORD=""
ENV GWID=""

# Specify the command to run the application
CMD [ "/app/entrypoint.sh" ]
