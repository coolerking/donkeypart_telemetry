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
import datetime
import paho.mqtt.client as mqtt

class LogBase:
    """
    ログ出力ユーティリティメソッドを備えた基底クラス。
    """
    def __init__(self, debug=False):
        """
        デバッグフラグをインスタンス変数へ格納する。

        引数
            debug   デバッグモード
        戻り値
            なし
        """
        self.debug = debug
    
    def log(self, msg):
        """
        ログを出力する。

        引数
            msg メッセージ文字列
        戻り値
            なし
        """
        if self.debug:
            print(msg)

class ConfigBase(LogBase):
    """
    ログ基底クラスに設定ファイルを読み込みインスタンス変数へ格納する機能を
    デコレートした基底クラス。
    """
    def __init__(self, conf_path, debug=False):
        """
        設定ファイルを読み込み、インスタンス変数へ格納する。
        引数
            conf_path   設定ファイルのパス
            debug       デバッグフラグ
        戻り値
            なし
        """
        super().__init__(debug)

        conf_path = os.path.expanduser(conf_path)
        if not os.path.exists(conf_path):
            raise Exception('[__init__] conf_path={} is not exists'.format(conf_path))
        if not os.path.isfile(conf_path):
            raise Exception('[__init__] conf_path={} is not a file'.format(conf_path))

        with open(conf_path, 'r') as f:
            conf = yaml.load(f)
        self.log('[__init__] read conf : ' + str(conf))

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

        self.log('[__init__] host=' + self.host)
        self.log('[__init__] port=' + str(self.port))
        self.log('[__init__] pub_topic=' + self.pub_topic)
        self.log('[__init__] sub_topic=' + self.sub_topic)

class MosqPubBase(ConfigBase):
    """
    eclipse-mosquitto を MQTT ブローカとして使用する Publisher 基底クラス。
    """
    def __init__(self, conf_path, debug=False):
        """
        設定ファイルからデバイス情報を読み込み、MQTTブローカへ接続する。

        引数
            conf_path   デバイス設定ファイルのパス
            debug       デバッグフラグ
        戻り値
            なし
        """
        super().__init__(conf_path, debug)
        self.log('[__init__] start dev_conf_path={}'.format(conf_path))

        self.client = mqtt.Client(protocol=mqtt.MQTTv311)

        self.log("[__init__] new client")

        self.client.connect(self.host, port=self.port, keepalive=60)
        self.log("[__init__] connect client host:" + self.host + ', port:' + str(self.port))

    def publishJson(self, msg_dict={}):
        """
        引数msg_dictで与えられた辞書をJSONデータ化してpublish処理を実行する。

        引数
            msg_dict    送信メッセージ（辞書）
        戻り値
            なし
        """
        self.log('[publishJson] start msg_dict={}'.format(json.dumps(msg_dict)))
        self.client.publish(self.pub_topic + '/json', json.dumps(msg_dict))
        self.log('[publishJson] published topic:' + self.pub_topic + '/json')

    def publishBin(self, msg_bin=None):
        """
        引数msg_dictで与えられた辞書をJSONデータ化してpublish処理を実行する。

        引数
            msg_dict    送信メッセージ（辞書）
        戻り値
            なし
        """
        self.log('[publishBin] start msg_bin length={}'.format(len(msg_bin)))
        self.client.publish(self.pub_topic + '/bin', msg_bin)
        self.log('[publish] published topic:{}/bin'.format(self.pub_topic))
    
    def disconnect(self):
        """
        接続を解除する。

        引数
            なし
        戻り値
            なし
        """
        self.client.disconnect()
        self.log('[disconnect] disconnected client')


class MosqSubBase(ConfigBase):
    """
    eclipse-mosquitto をMQTTブローカとして使用するSubscriber基底クラス。
    """
    def __init__(self, conf_path, on_message=None, debug=False):
        """
        設定ファイルからデバイス情報を読み込み、MQTTブローカへ接続する。

        引数
            conf_path   デバイス設定ファイルのパス
            on_message  メッセージ受信時コールバック関数
            debug       デバッグフラグ
        戻り値
            なし
        """
        super().__init__(conf_path, debug)
        self.log('[__init__] start dev_conf_path={}'.format(conf_path))

        self.client = mqtt.Client(protocol=mqtt.MQTTv311)

        self.log("[__init__] new client")

        self.client.on_connect = self.on_connect
        self.log('[__init__] set default on_connect')
        if on_message is None:
            self.client.on_message = self._on_message
            self.log('[__init__] set default on_message')
        else:
            self.client.on_message = on_message
            self.log('[__init__] set on_message')

        self.client.connect(self.host, port=self.port, keepalive=60)
        self.log("[__init__] connect client host:" + self.host + ', port:' + str(self.port))
    
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
        self.log('[on_connect] status {0}'.format(respons_code))
        self.client.subscribe(self.sub_topic)
        self.log('[on_connect] subscribe topic=' + self.sub_topic)
    
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
        self.log('[_on_message] no operation ' + message.topic + ' ' + str(message.payload))

    def disconnect(self):
        """
        クライアント接続を解除する。

        引数   
            なし
        戻り値
            なし
        """
        self.client.disconnect()
        self.log('[disconnect] disconnected client')

class PubTelemetry(MosqPubBase):
    """
    スロットル、アングル値をMQTTブローカへPublishするPubTelemetryクラス。
    """
    def __init__(self, conf_path, tub_dir, pub_count=2000, debug=False):
        """
        設定ファイルを読み込み、MQTTクライアントを生成、接続する。

        引数
            config_path     設定ファイルのパス
            tub_dir         tubディレクトリのパス
            pub_count       publish実行間隔
            debug           デバッグフラグ
        戻り値
            なし
        """
        super().__init__(conf_path, debug)
        self.throttle = 1.0
        self.angle = 1.0
        self.delta = 0.005
        self.count = 0
        self.pub_count = pub_count
        self.tub_dir = os.path.expanduser(tub_dir)
        self.image_array = None
        if not os.path.exists(self.tub_dir) or not os.path.isdir(self.tub_dir):
            raise Exception('tub_dir={} not exists or not isdir'.format(tub_dir))
        self.log('[__init__] end')

    def run(self, image_array, user_mode, user_angle, user_throttle, pilot_angle, pilot_throttle):
        """
        スロットル値、アングル値を含むJSONデータをMQTTブローカへ送信する。
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
            #self.log('[run] ignnore data, very often sending')
            return
        else:
            self.count = 0
        
        angle, throttle = self.getAction(user_mode, user_angle, user_throttle, pilot_angle, pilot_throttle)
        if self.isInDelta(user_mode, user_angle, user_throttle, pilot_angle, pilot_throttle):
            self.log('[run] ignnore data, delta is small th:[{}, {}] an[{}, {}]'.format(
                str(throttle), str(self.throttle), str(angle), str(self.angle)))

        self.publishBin(msg_bin=self.ndarray_to_bin(image_array))
        self.log('[run] publish image') 
        msg_dict = {
            "user_mode":        user_mode,
            "user_angle":       user_angle,
            "user_throttle":    user_throttle,
            "pilot_angle":      pilot_angle,
            "pilot_throttle":   pilot_throttle,
            "angle":            angle,
            "throttle":         throttle,
            "timestamp":        str(datetime.now())
        }
        self.publishJson(msg_dict=msg_dict)
        self.log('[run] publish :' + json.dumps(msg_dict))
        self.throttle = throttle
        self.angle = angle
        self.image_array = image_array

    def getAction(self, user_mode, user_angle, user_throttle, pilot_angle, pilot_throttle):
        """
        ユーザモードから実際にDonkey Carが採用したアングル値、スロットル値を返却する。

        引数
            user_mode           運転モード(user,local_angle,local)
            user_angle          手動操作によるアングル値
            user_throttle       手動操作によるスロットル値
            pilot_angle         自動運転アングル値
            pilot_throttle      自動運転スロットル値
        戻り値
            angle               実際に採用したアングル値
            throttle            実際に採用したスロットル値
        """
        # 運転モードから実際に使用されたアングル、スロットル値を判断
        if user_mode == 'user':
            return user_angle, user_throttle
        elif user_mode == 'local_angle':
            return user_angle, pilot_throttle
        else:
            return pilot_angle, pilot_throttle

    def isInDelta(self, user_mode, user_angle, user_throttle, pilot_angle, pilot_throttle):
        """
        アングル、スロットル値が前に送信した値とほとんど変わらないかどうかを判定する。

        引数
            user_mode           運転モード(user,local_angle,local)
            user_angle          手動操作によるアングル値
            user_throttle       手動操作によるスロットル値
            pilot_angle         自動運転アングル値
            pilot_throttle      自動運転スロットル値
        戻り値
            eval                しきい値範囲内：真、しきい値範囲外：偽
        """
        # 運転モードから実際に使用されたアングル、スロットル値を判断
        angle, throttle = self.getAction(user_mode, user_angle, user_throttle, 
        pilot_angle, pilot_throttle)

        # アングル、スロットル値が前に送信した値とほとんど変わらないかどうか
        isInDelta_throttle = abs(abs(throttle) - abs(self.throttle)) < self.delta
        isInDelta_angle =  abs(abs(angle) - abs(self.angle)) < self.delta
        return isInDelta_throttle and isInDelta_angle

    def ndarray_to_bin(self, data):
        """
        np.ndarray形式の場合は、バイト配列に変換する。

        引数
            data    送信データ
        戻り値
            data    送信データ（np.ndarrayはdonkeycarユーティリティでバイナリへ変換）
        """
        if type(data) is np.ndarray:
          return dk.util.img.arr_to_binary(data)

    def shutdown(self):
        """
        MQTTクライアント接続を解除する。

        引数
            なし
        戻り値
            なし
        """
        self.disconnect()
        self.log('[shutdown] disconnect client')

class SubPilot(MosqSubBase):
    """
    AIのかわりにMQTTブローカからスロット、アングル値を受け取るSubPilotクラス
    """
    def __init__(self, conf_path, debug=False):
        """
        設定ファイルを読み込み、MQTTクライアントを生成、接続する。

        引数
            config_path     設定ファイルのパス
            debug           デバッグフラグ
        戻り値
            なし
        """
        super().__init__(conf_path, self.on_message, debug)
        self.throttle = 0.0
        self.angle = 0.0
        self.timestamp = datetime.datetime.now().isoformat()
        self.log('[__init__] end')

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
        self.log('[on_message] start ' + message.topic + ' ' + str(message.payload))
        data = message.payload
        self.log('[on_message] message.payload is ' + type(data))
        self.throttle = float(data['throttle'])
        self.angle = float(data['angle'])
        self.timestamp = str(data['timestamp'])
    
    def run(self):
        """
        最新のスロットル値、アングル値を返却する。

        引数
            なし
        戻り値
            throttle    スロットル値
            angle       アングル値
        """
        self.log('[run] return throttle={}, angle={}, timestamp={}'.format(
            str(self.throttle), str(self.angle), str(self.timestamp)))
        return self.throttle, self.angle #, self.timestamp
    
    def shutdown(self):
        """
        MQTTクライアント接続を解除する。

        引数
            なし
        戻り値
            なし
        """
        self.disconnect()
        self.log('[shutdown] disconnect client')