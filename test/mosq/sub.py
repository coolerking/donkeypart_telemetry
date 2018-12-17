# -*- coding: utf-8 -*-
"""
MQTTブローカの動作を確認するためのプログラム。
paho-mqttパッケージが必要です。

pip install paho-mqtt

"""
import paho.mqtt.client as mqtt


"""
MQTTブローカ情報
接続対象のブローカに合わせて設定を変更してください。
"""
HOST = '127.0.0.1'
PORT = 1883
KEEP_ALIVE = 60
TOPIC = 'test_topic/test1'
"""
接続を試みたときに実行する。
必ずしも成功したから呼び出されるとは限らない。
response_codeを確認すること。
"""
def on_connect(client, userdata, flags, respons_code):
    print('status {0}'.format(respons_code))
    client.subscribe(client.topic)

"""
topicを受信したときに実行する。
"""
def on_message(client, userdata, message):
    print(message.topic + ' ' + str(message.payload))

"""
ブローカの疎通を確認する。
"""
if __name__ == '__main__':

    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.topic = TOPIC

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(HOST, port=PORT, keepalive=KEEP_ALIVE)

    # ループ
    client.loop_forever()      
