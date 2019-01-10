# -*- coding: utf-8 -*-
import uuid
import numpy as np
import ibmiotf.device
import ibmiotf.application
from .img import ImageCodec

from logging import getLogger, basicConfig, DEBUG
basicConfig(filename='donkeypart_telemetry_iotf.log', filemode='w', level=DEBUG)
logger = getLogger(__name__)

class PubTelemetry:
    def __init__(self, dev_conf_path, pub_count=20):
        self.count = 0
        self.pub_count = pub_count
        try:
            options = ibmiotf.device.ParseConfigFile(dev_conf_path)
            self.client = ibmiotf.device.Client(options)
            self.client.setMessageEncoderModule('image', ImageCodec)
            self.client.connect()
        except ibmiotf.ConnectionException  as e:
            logger.error('error at PubTelemetry __init__', exc_info=True)
            raise e

    def run(self, image_array, user_mode, user_angle, user_throttle, pilot_angle, pilot_throttle, angle, throttle):
        # pub_count数に達したら実行
        self.count = self.count + 1
        if self.count <= self.pub_count:
            logger.debug('publish ignored')
            return
        else:
            self.count = 0

        message = {
            "user/mode":        user_mode,
            "user/angle":       user_angle,
            "user/throttle":    user_throttle,
            "pilot/angle":      pilot_angle,
            "pilot/throttle":   pilot_throttle,
            "angle":            angle,
            "throttle":         throttle,
            "timestamp":        ImageCodec.get_now_str()
        }

        success = self.client.publishEvent(
            event='status', 
            msgFormat='image', 
            data=image_array, 
            qos=0, 
            on_publish=self.on_publish_image)
        logger.debug('publish image result={}'.format(str(success)))
        success = self.client.publishEvent(
            event='status', 
            msgFormat='json', 
            data=message, 
            qos=0, 
            on_publish=self.on_publish_json)
        logger.debug('publish json result={}'.format(str(success)))

    def on_publish_image(self):
        logger.debug('on_publish_image called')
    def on_publish_json(self):
        logger.debug('on_publish_json called')
    def shutdown(self):
        logger.debug('shutdown called')
        self.client.disconnect()

class SubTelemetry:
    def __init__(self, app_conf_path, dev_conf_path=None):
        self.user_mode = 'n/a'
        self.user_angle = 0.0
        self.user_throttle = 0.0
        self.pilot_angle = 0.0
        self.pilot_throttle = 0.0
        self.angle = 0.0
        self.throttle = 0.0
        self.timestamp = ImageCodec.get_now_str()
        self.image_array = np.zeros(shape=(120 ,160 ,3), dtype='uint8')
        try:
            # 送信元情報の入手
            if dev_conf_path is None:
                dev_conf_path = app_conf_path
            dev_options = ibmiotf.device.ParseConfigFile(dev_conf_path)
            self.dev_type = dev_options.get('type', '+')
            self.dev_id = dev_options.get('id', '+')

            app_options = ibmiotf.application.ParseConfigFile(app_conf_path)
            self.client = ibmiotf.application.Client(app_options)
            self.client.setMessageEncoderModule('image', ImageCodec)
            self.client.connect()

            self.client.deviceEventCallback = self.on_subscribe
            logger.debug('set device event callback')
            self.client.subscribeToDeviceEvents(
                    deviceType=self.dev_type, 
                    deviceId=self.dev_id, 
                    event='status')
            logger.debug('subscribe start devType:{} devId:{} event:status'.format(self.dev_type, self.dev_id))
        except ibmiotf.ConnectionException  as e:
            logger.error('error at SubTelemetry __init__', exc_info=True)
            raise e
    
    def on_subscribe(self, event):
        data = event.data
        logger.debug('on_subscribe: data is {}'.format(str(type(data))))
        if event.format == 'image':
            logger.debug('image data')
            self.image_array = ImageCodec.encode_to_arr(data)
        elif event.format == 'json':
            logger.debug('json data')
            self.user_mode = data.get('user/mode', self.user_mode)
            self.user_angle = float(data.get('user/angle', self.user_angle))
            self.user_throttle = float(data.get('user/throttle', self.user_throttle))
            self.pilot_angle = float(data.get('pilot/angle', self.pilot_angle))
            self.pilot_throttle = float(data.get('pilot/throttle', self.pilot_throttle))
            self.angle = float(data.get('angle', self.angle))
            self.throttle = float(data.get('throttle', self.throttle))
            self.timestamp = data.get('timestamp', self.timestamp)
        else:
            logger.debug('otherwise data')

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
            self.angle              採用されたアングル値
            self.throttle           採用されたスロットル値
        """
        logger.debug('run called')
        return self.image_array, self.user_mode, self.user_angle, self.user_throttle, self.pilot_angle, self.pilot_throttle, self.angle, self.throttle #, self.timestamp

    def shutdown(self):
        logger.debug('shutdown called')
        self.client.disconnect()