# -*- coding: utf-8 -*-
from time import sleep
import paho.mqtt.client as mqtt

HOST = '127.0.0.1'
PORT = 1883
KEEP_ALIVE = 60
TOPIC = 'test_topic/test1'
MESSAGE = 'test message'

PUBLISH_NUMBER = 5
SLEEP_TIME = 5

def publish_many_times(client, topic='topic/default', message='default', number=1, time=1, print_flag=False):

    for i in range(number):
        client.publish(topic, message)
        if print_flag == True:
            print (topic + ' ' + message)
        sleep(time)

    client.disconnect()

if __name__ == '__main__':
    client = mqtt.Client(protocol=mqtt.MQTTv311)

    print("publish start " + str(type(client)))

    client.connect(HOST, port=PORT, keepalive=KEEP_ALIVE)

    publish_many_times(client,TOPIC, MESSAGE, PUBLISH_NUMBER, SLEEP_TIME)       