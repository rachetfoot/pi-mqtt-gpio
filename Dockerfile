FROM python:3.7-alpine

ENV LANG C.UTF-8  
ENV LC_ALL C.UTF-8  

RUN apk add --no-cache build-base gcc make musl-dev linux-headers
RUN pip install --no-cache-dir pipenv

WORKDIR /app

#WORKDIR /home/mqttgpio
#RUN adduser --disabled-password --gecos "" --home "$(pwd)" --no-create-home -s /bin/bash mqttgpio
#RUN addgroup -g 997 gpio
#RUN addgroup mqttgpio gpio
#RUN chown -R mqttgpio .
#RUN addgroup i2c && chown :i2c /dev/i2c-1 \
#  && chmod g+rw /dev/i2c-1 \
#  && usermod -aG i2c mqttgpio
#USER mqttgpio

COPY Pipfile ./
RUN pipenv install --three --deploy

COPY pi_mqtt_gpio pi_mqtt_gpio

CMD [ "pipenv", "run", "python", "-m", "pi_mqtt_gpio.server", "/config.yml" ]
