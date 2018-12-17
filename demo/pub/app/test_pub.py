# -*- coding: utf-8 -*-

import random
import datetime
import logging
import json
from time import sleep
#from sub import Sub
import paho.mqtt.client as mqtt



class Pub:

    log = logging.getLogger('test')

    def __init__(self, host, port, topic):
        Pub.log.setLevel(10)
        Pub.log.addHandler(logging.StreamHandler())

        self.topic = topic

        self.client = mqtt.Client(protocol=mqtt.MQTTv311)
        Pub.log.info('[__init__] new client')

        self.client.connect(host, port=port, keepalive=60)
        Pub.log.info('[__init__] connect client')


    def run(self, throttle, angle, timestamp):
        self.client.publish(self.topic, self.filter(throttle, angle, timestamp))
        Pub.log.info('[run] publish topic=' + self.topic)

    def shutdown(self):
        self.client.disconnect()
        Pub.log.info('[shutdown] disconnect client')

    def filter(self, throttle, angle, timestamp):
        payload_dict = {
            "throttle": throttle,
            "angle": angle,
            "timestamp": timestamp}
        payload_str = json.dumps(payload_dict)
        Pub.log.debug('[_filter] payload dict to str(' + payload_str + ')')
        return payload_str



if __name__ == '__main__':
    host = 'broker'
    port = 1883
    topic = 'test_topic/pilot'
    pub = Pub(host, port, topic)
    while(True):
        sleep(1.0)
        throttle = random.uniform(0, 100)
        angle = random.uniform(0, 100)
        timestamp = str(datetime.datetime.now())
        pub.run(throttle, angle, timestamp)
        print('[pub] throttle:{}, angle:{}, timestamp:{}'.format(str(throttle), str(angle), timestamp))

    pub.shutdown()