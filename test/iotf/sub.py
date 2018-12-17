# -*- coding: utf-8 -*-
"""
IBM Watson IoT Platform 用テストPublisher。
一定時間ごとに、乱数生成したメッセージをMQTTブローカ(IoTP)へ送信し続ける。
IBM社提供のIoTFライブラリを使用（pip install ibmiotf）しており、デバイス設定はすべて外部の設定ファイルへ格納されている。

Usage:
    pub.py [--conf=CONFIG_PATH] [--dev_type=SUBSCRIBE_TYPE] [--dev_id=SUBSCRIBE_ID] [--event=SUBSCRIBE_EVENT] [--wait=WAITING_SECS]

Options:
    --config=CONFIG_PATH      設定ファイルパス
    --dev_type=SUBSCRIBE_TYPE 購読対象とするデバイスタイプ
    --dev_id=SUBSCRIBE_ID     購読対象とするデバイスID
    --event=SUBSCRIBE_EVENT   購読対象とするイベント
    --wait=WAITING_SECS       subscribe後待機時間（秒）
"""
# -*- coding: utf-8 -*-
import json
import random
import datetime
import docopt
from time import sleep
import ibmiotf.application

CONFIG_PATH='telemetry.ini'
WAIT=1000

def subscribe(config_path=CONFIG_PATH, device_type=None, device_id=None, event=None, wait=WAIT):
    try:
        options = ibmiotf.application.ParseConfigFile(config_path)
        client = ibmiotf.application.Client(options)
        print('[subscribe] config loaded')
    except ibmiotf.ConnectionException  as e:
        print('[subscribe] config load failed ' + config_path)
        raise e

    client.connect()
    print('[subscribe] connect client')

    client.deviceEventCallback = on_subscribe

    if device_type is None and device_id is None and event is None:
        client.subscribeToDeviceEvents()
        print('[subscribe] subscribe all')
    elif device_type is None and device_id is None and event is not None:
        client.subscribeToDeviceEvents(event=event)
        print('[subscribe] subscribe event=' + event)
    elif device_type is not None and device_id is not None and event is None:
        client.subscribeToDeviceEvents(deviceType=device_type, deviceId=device_id)
        print('[subscribe] subscribe dev_type={}, dev_id={}'.format(device_type, device_id))
    elif device_type is not None and device_id is None and event is None:
        client.subscribeToDeviceEvents(deviceType=device_type)
        print('[subscribe] subscribe dev_type={}'.format(device_type))
    elif device_type is not None and device_id is not None and event is not None:
        client.subscribeToDeviceEvents(deviceType=device_type, deviceId=device_id, event=event, msgFormat='json')
        print('[subscribe] subscribe dev_type={}, dev_id={}, event={}, format=json'.format(device_type, device_id, event))
    else:
        raise Exception('[subscribe] subscribe not match dev_type={}, dev_id={}, event={}, format=json'.format(device_type, device_id, event))

    if wait < 0:
        while(True):
            print('[subscribe] wait forever')
            sleep(wait*(-1.0))
    else:
        print('[subscribe] wait {} secs'.format(str(wait)))
        sleep(wait)

    client.disconnect()
    print('[subscribe] disconnect client')


def on_subscribe(event):
      str = "[on_subscribe] %s event '%s' received from device [%s]: %s"
      print(str % (event.format, event.event, event.device, json.dumps(event.data)))

if __name__ == '__main__':
    print('[__main__] start')
    # 引数情報の収集
    args = docopt.docopt(__doc__)

    conf_path = args['--conf']
    if conf_path is None:
        conf_path = CONFIG_PATH
    
    dev_id = args['--dev_id']
    dev_type = args['--dev_type']
    event = args['--event']


    wait = args['--wait']
    if wait is None:
        wait = WAIT
    else:
        wait = float(wait)
    
    subscribe(config_path=conf_path, device_type=dev_type, device_id=dev_id, event=event, wait=wait)

    print('[__main__] end')
