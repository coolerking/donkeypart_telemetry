# -*- coding: utf-8 -*-
"""
スロットル、アングル値をMQTTブローカへPublishするPubTelemetryクラスと
AIのかわりにMQTTブローカからスロット、アングル値を受け取るSubPilotクラスを提供する。
なお本ファイル上のクラスはすべて eclipse-mosquitto をMQTTブローカとして使用しており、
paho-mqtt パッケージをインストールする必要がある。

pip install paho-mqtt
"""

import os
import json
import yaml
from datetime import datetime
import numpy as np
import paho.mqtt.client as mqtt

import donkeycar as dk

class ConfigBase:
    """
    設定ファイルを読み込みインスタンス変数へ格納する機能を提供する基底クラス。
    """
    def __init__(self, conf_path):
        """
        設定ファイルを読み込み、インスタンス変数へ格納する。
        引数
            conf_path   設定ファイルのパス
            debug       デバッグフラグ
        戻り値
            なし
        """
        conf_path = os.path.expanduser(conf_path)
        if not os.path.exists(conf_path):
            raise Exception('conf_path={} is not exists'.format(conf_path))
        if not os.path.isfile(conf_path):
            raise Exception('conf_path={} is not a file'.format(conf_path))

        with open(conf_path, 'r') as f:
            conf = yaml.load(f)

        broker_conf = conf['broker']

        self.host = broker_conf['host']
        if self.host is None:
            self.host = '127.0.0.1'
        self.port = broker_conf['port']
        if self.port is None:
            self.port = 1883
        else:
            self.port = int(self.port)
        
        pub_conf = conf['publisher']
        self.pub_topic = pub_conf['topic']

        sub_conf = conf['subscriber']
        self.sub_topic = sub_conf['topic']


class MosqPubBase(ConfigBase):
    """
    eclipse-mosquitto を MQTT ブローカとして使用する Publisher 基底クラス。
    """
    def __init__(self, conf_path):
        """
        設定ファイルからデバイス情報を読み込み、MQTTブローカへ接続する。

        引数
            conf_path   デバイス設定ファイルのパス
            debug       デバッグフラグ
        戻り値
            なし
        """
        super().__init__(conf_path)

        self.client = mqtt.Client(protocol=mqtt.MQTTv311)
        self.client.connect(self.host, port=self.port, keepalive=60)

    def publishJson(self, msg_dict={}):
        """
        引数msg_dictで与えられた辞書をJSONデータ化してpublish処理を実行する。

        引数
            msg_dict    送信メッセージ（辞書）
        戻り値
            なし
        """
        self.client.publish(self.pub_topic + '/json', json.dumps(msg_dict))

    def publishBin(self, msg_bin=None):
        """
        引数msg_dictで与えられた辞書をJSONデータ化してpublish処理を実行する。

        引数
            msg_dict    送信メッセージ（辞書）
        戻り値
            なし
        """
        self.client.publish(self.pub_topic + '/image', msg_bin)
    
    def disconnect(self):
        """
        接続を解除する。

        引数
            なし
        戻り値
            なし
        """
        self.client.disconnect()

class MosqSubBase(ConfigBase):
    """
    eclipse-mosquitto をMQTTブローカとして使用するSubscriber基底クラス。
    """
    def __init__(self, conf_path, on_message=None):
        """
        設定ファイルからデバイス情報を読み込み、MQTTブローカへ接続する。

        引数
            conf_path   デバイス設定ファイルのパス
            on_message  メッセージ受信時コールバック関数
            debug       デバッグフラグ
        戻り値
            なし
        """
        super().__init__(conf_path)
        self.client = mqtt.Client(protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect

        if on_message is None:
            self.client.on_message = self._on_message
        else:
            self.client.on_message = on_message

        self.client.connect(self.host, port=self.port, keepalive=60)
        self.client.loop_start()
    
    def on_connect(self, client, userdata, flags, respons_code):
        """
        接続時コールバック関数、この中でトピックの購読を開始している。

        引数
            client          MQTTクライアントオブジェクト
            userdata        ユーザデータ
            flags           フラグ
            response_code   返却コード
        戻り値
            なし
        """
        self.client.subscribe(self.sub_topic)
    
    def _on_message(self, client, userdata, message):
        """
        デフォルトのメッセージ受信時コールバック関数、実装なし。

        引数
            client          MQTTクライアントオブジェクト
            userdata        ユーザデータ
            message         受診メッセージ
        戻り値
            なし
        """
        pass
        #print('no operation ' + message.topic + ' ' + str(message.payload))

    def disconnect(self):
        """
        クライアント接続を解除する。

        引数   
            なし
        戻り値
            なし
        """
        self.client.loop_stop()
        self.client.disconnect()

class PubTelemetry(MosqPubBase):
    """
    スロットル、アングル値をMQTTブローカへPublishするPubTelemetryクラス。
    """
    def __init__(self, conf_path, pub_count=2000):
        """
        設定ファイルを読み込み、MQTTクライアントを生成、接続する。

        引数
            config_path     設定ファイルのパス
            pub_count       publish実行間隔
        戻り値
            なし
        """
        super().__init__(conf_path)
        self.count = 0
        self.pub_count = pub_count

    def run(self, image_array, user_mode, user_angle, user_throttle, pilot_angle, pilot_throttle, angle, throttle):
        """
        イメージデータ、スロットル値、アングル値を含むJSONデータをMQTTブローカへ送信する。
        引数
            image_array         カメラ画像イメージデータ(np.ndarray)
            user_mode           運転モード(user,local_angle,local)
            user_angle          手動操作によるアングル値
            user_throttle       手動操作によるスロットル値
            pilot_angle         自動運転アングル値
            pilot_throttle      自動運転スロットル値
        戻り値
            なし
        """
        # pub_count数に達したら実行
        self.count = self.count + 1
        if self.count <= self.pub_count:
            return
        else:
            self.count = 0
        
        if type(image_array) is np.ndarray:
            image = dk.util.img.arr_to_binary(image_array)
        elif type(image_array) is bytes:
            image = image_array
        else:
            raise Exception('unknown image_array type=' +str(type(image_array)))

        self.publishBin(msg_bin=image)

        msg_dict = {
            "user/mode":        user_mode,
            "user/angle":       user_angle,
            "user/throttle":    user_throttle,
            "pilot/angle":      pilot_angle,
            "pilot/throttle":   pilot_throttle,
            "angle":            angle,
            "throttle":         throttle,
            "timestamp":        str(datetime.now())
        }
        self.publishJson(msg_dict=msg_dict)

    def shutdown(self):
        """
        MQTTクライアント接続を解除する。

        引数
            なし
        戻り値
            なし
        """
        self.disconnect()

class SubTelemetry(MosqSubBase):
    """
    AIのかわりにMQTTブローカからスロット、アングル値を受け取るSubPilotクラス
    """
    def __init__(self, conf_path):
        """
        設定ファイルを読み込み、MQTTクライアントを生成、接続する。

        引数
            config_path     設定ファイルのパス
            debug           デバッグフラグ
        戻り値
            なし
        """
        super().__init__(conf_path, self.on_message)
        self.user_mode = 'user'
        self.user_angle = 0.0
        self.user_throttle = 0.0
        self.pilot_angle = 0.0
        self.pilot_throttle = 0.0
        self.throttle = 0.0
        self.angle = 0.0
        self.timestamp = str(datetime.now())
        self.image_array = None

    def on_message(self, client, userdata, message):
        """
        デフォルトのメッセージ受信時コールバック関数。
        取得したスロットル値、アングル値をインスタンス変数へ格納する。

        引数
            client          MQTTクライアントオブジェクト
            userdata        ユーザデータ
            message         受診メッセージ
        戻り値
            なし
        """
        data = message.payload
        if message.topic.endswith('json'):
            data = json.loads(data)
            self.user_mode = data.get('user/mode', self.user_mode)
            self.user_angle = float(data.get('user/angle', 0.0))
            self.user_throttle = float(data.get('user/throttle', self.user_throttle))
            self.pilot_angle = float(data.get('pilot/angle', self.pilot_angle))
            self.pilot_throttle = float(data.get('pilot/throttle', self.pilot_throttle))
            self.angle = float(data.get('angle', self.angle))
            self.throttle = float(data.get('throttle', self.throttle))
            self.timestamp = data.get('timestamp', self.timestamp)
        elif message.topic.endswith('image'):
            if type(data) is np.ndarray:
                self.image_array = data
            elif type(data) is bytes:
                img = dk.util.img.binary_to_img(data)
                self.image_array = dk.util.img.img_to_arr(img)
            else:
                pass
        # 他のフォーマットを増やす場合は、ここに追加
        else:
            pass

    def run(self):
        """
        最新の値を返却する。

        引数
            なし
        戻り値
            self.image_array        カメラ画像イメージデータ(np.ndarray)
            self.user_mode          運転モード(user,local_angle,local)
            self.user_angle         手動操作によるアングル値
            self.user_throttle      手動操作によるスロットル値
            self.pilot_angle        自動運転アングル値
            self.pilot_throttle     自動運転スロットル値
            self.angle              実際に採用されたアングル値
            self.throttle           実際に採用されたスロットル値
        """
        return self.image_array, self.user_mode, self.user_angle, self.user_throttle, self.pilot_angle, self.pilot_throttle, self.angle, self.throttle #, self.timestamp
    
    def shutdown(self):
        """
        MQTTクライアント接続を解除する。

        引数
            なし
        戻り値
            なし
        """
        self.disconnect()