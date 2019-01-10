# -*- coding: utf-8 -*-
"""
pytestで実行可能なテストモジュール。
PubTelemetry/SubTelemetry を実際にIBM Watson IoT Platformへ接続してテストする。

テストを実行する前にまず IoT Platform を準備し、テスト用デバイス・アプリのための
APIキー情報を入手し、 conf/iotf/test.ini を編集する必要がある。
"""
import pytest

import os
from time import sleep
import random
import donkeycar as dk
from donkeycar.parts.transform import Lambda
from donkeypart_telemetry.iotf import PubTelemetry, SubTelemetry

#
# test contents
#
test_conf_path = 'conf/iotf/test.ini'
test_image_path = 'tub/0_cam-image_array_.jpg'
result_image_path = 'result_0.jpg'


class PubSubTest:
    """
    PubTelemetry/SubTelemetryの機能をテストするクラス。
    """
    def __init__(self, dev_conf_path=None, app_conf_path=None):
        self.sub = SubTelemetry(dev_conf_path=dev_conf_path, app_conf_path=app_conf_path)
        self.pub = PubTelemetry(dev_conf_path=dev_conf_path, pub_count=0)


    
    def test(self):
        with open(test_image_path, 'rb') as f:
            binary = f.read()
        exp_image_array = dk.util.img.img_to_arr(dk.util.img.binary_to_img(binary))
        exp_user_mode = 'user'
        exp_user_angle = random.uniform(-1.0, 1.0)
        exp_user_throttle = random.uniform(-1.0, 1.0)
        exp_pilot_angle = random.uniform(-1.0, 1.0)
        exp_pilot_throttle = random.uniform(-1.0, 1.0)
        exp_angle = random.uniform(-1.0, 1.0)
        exp_throttle = random.uniform(-1.0, 1.0)

        self.pub.run(exp_image_array, 
            exp_user_mode,
            exp_user_angle,
            exp_user_throttle,
            exp_pilot_angle,
            exp_pilot_throttle,
            exp_angle,
            exp_throttle)

        sleep(5)

        image_array, user_mode, user_angle, user_throttle, pilot_angle, pilot_throttle, angle, throttle = self.sub.run()

        print('user_mode:{} /{}'.format(user_mode, exp_user_mode))
        print('user_angle:{} /{}'.format(str(user_angle), str(exp_user_angle)))
        print('user_throttle:{} /{}'.format(str(user_throttle), str(exp_user_throttle)))
        print('pilot_angle:{} /{}'.format(str(pilot_angle), str(exp_pilot_angle)))
        print('pilot_throttle:{} /{}'.format(str(pilot_throttle), str(exp_pilot_throttle)))
        print('angle:{} /{}'.format(str(angle), str(exp_angle)))
        print('throttle:{} /{}'.format(str(throttle), str(exp_throttle)))
        assert user_mode == exp_user_mode
        assert user_angle == exp_user_angle
        assert user_throttle == exp_user_throttle
        assert pilot_angle == exp_pilot_angle
        assert pilot_throttle == exp_pilot_throttle
        assert angle == exp_angle
        assert throttle == exp_throttle

        print(type(image_array))
        exp_binary = dk.util.img.arr_to_binary(image_array)
        with open(result_image_path, 'wb') as f:
            f.write(exp_binary)
        print('please eval org:{} and result:{}'.format(test_image_path, result_image_path))

        self.pub.shutdown()
        self.sub.shutdown()

class VehicleTest:
    """
    Donkeycar パッケージのVehicleフレームワークのパーツとして正常動作するかを確認するためのクラス。
    donkeypart_tub_loaderを使用する。
    """
    def __init__(self, dev_conf_path=None, app_conf_path=None):
        from donkeypart_tub_loader import TubLoader, TubPrinter
        tubitems = [
            'cam/image_array',
            'user/mode',
            'user/angle',
            'user/throttle',
            'pilot/angle',
            'pilot/throttle',
            'angle',
            'throttle']

        self.vehicle = dk.vehicle.Vehicle()
        self.vehicle.add(TubLoader('tub'), outputs=tubitems)

        self.vehicle.add(PubTelemetry(dev_conf_path=dev_conf_path, pub_count=0), inputs=tubitems)
        self.vehicle.add(TubPrinter(), inputs=tubitems)

        def wait():
            delay=3
            #print('wait {} seconds'.format(str(delay)))
            sleep(delay)
        self.vehicle.add(Lambda(wait))

        self.vehicle.add(SubTelemetry(app_conf_path=app_conf_path, dev_conf_path=dev_conf_path), outputs=tubitems)
        self.vehicle.add(TubPrinter(), inputs=tubitems)
        

    
    def test(self):
        try:
            self.vehicle.start(rate_hz=1, max_loop_count=5)
            assert True
        except StopIteration:
            pytest.fail('StopIteration occurs!')



def test_pub_sub():
    """
    Publish/Subscribeが正しく機能するかどうかを確認するテストメソッド。

    引数
        なし
    戻り値
        なし
    例外
        AssertionError  テスト失敗時
    """
    test = PubSubTest(dev_conf_path=test_conf_path, app_conf_path=test_conf_path)
    test.test()

def test_donkey():
    """
    Vehicleフレームワーク内でPartとして動作するかを確認するテストメソッド。

    引数
        なし
    戻り値
        なし
    例外
        AssertionError  テスト失敗時
    """
    test = VehicleTest(dev_conf_path=test_conf_path, app_conf_path=test_conf_path)
    test.test()

if __name__ == '__main__':
    if os.path.exists(result_image_path):
        os.remove(result_image_path)
    if os.path.exists(test_conf_path):
        test_pub_sub()
        test_donkey()
    else:
        print('no config file {}. please creatte it.'.format(test_conf_path))
        print('* setup iot platform free on IBM Cloud (not work at quickstart)')
        print('* copy conf/iotf/test_template.ini conf/iotf/test.ini')
        print('* notepad/vi conf/iotf/test.ini')
        print('* re-run this')
        pytest.fail('no config file {}. please creatte it.'.format(test_conf_path))