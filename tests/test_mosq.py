# -*- coding: utf-8 -*-
"""
eclipse-mosquitto用PubTelemetry/SubTelemetryテストクラス。
pytest test_mosq.py でテストを実施可能。
127.0.0.1 にて1883ポートで待受状態の mosquitto が存在している前提で作成されている。
"""
import pytest

import os
from time import sleep
import numpy as np
import donkeycar as dk
from donkeycar.parts.transform import Lambda
from donkeypart_telemetry.mosq import PubTelemetry, SubTelemetry

test_conf_path = 'conf/mosq/localhost.yaml'

class MosqTester:
    """
    テスト本体を実装しているクラス。
    """
    def __init__(self):
        """
        PubTelemetry/SubTelemetryをインスタンス化し、テスト結果想定をインスタンス変数へ格納する。

        引数
            なし
        戻り値
            なし
        """
        self.publisher = PubTelemetry(conf_path=test_conf_path, pub_count=0)
        self.subscriber = SubTelemetry(conf_path=test_conf_path)

        self.expected =[
            #"user/mode", "user/angle", "user/throttle", "pilot/angle", "pilot/throttle", "angle", "throttle"
            ["user", -0.2, 0.8, 0.0, 0.0, -0.2, 0.8],
            ["user", 0.2, 1.0, 0.0, 0.0, 0.2, 1.0],
            ["user", 0.678, -0.345, 0.0, 0.0, 0.678, -0.345],
            ["user", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            ["user", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            ["user", -0.213, 0.099, 0.0, 0.0, -0.213, 0.099]]
        self.exp_total = len(self.expected)
        self.index = 0

    def get_exp_image_array(self, index):
        """
        テスト用イメージの読み込み。
        """
        path = os.path.join('tub', str(index) + '_cam-image_array_.jpg')
        #print('use path:{}'.format(path))
        with open(path, 'rb') as f:
            bin = f.read()
        return dk.util.img.img_to_arr(dk.util.img.binary_to_img(bin))

    def test_tub(self):
        """
        １件のTubデータをテスト。
        PublishとSubscribeの間隔は3秒でテストを実行している。
        """
        if self.index < self.exp_total:
            index = self.index
        else:
            index = self.exp_total - 1
        exp = self.expected[index]
        exp_image_array = self.get_exp_image_array(index)
        #print(type(exp_image_array))
        if self.index < self.exp_total:
            self.publisher.run(exp_image_array, exp[0], exp[1], exp[2], exp[3], exp[4], exp[5], exp[6])
        sleep(5)
        act_image_array, act_0, act_1, act_2, act_3, act_4, act_5, act_6 = self.subscriber.run()
        if act_image_array is None:
            # calibrate sleep seconds if failed
            pytest.fail('image could not recieve')
        assert type(act_image_array) == type(exp_image_array)
        if type(act_image_array) is np.ndarray:
            assert act_image_array.dtype == exp_image_array.dtype
            assert act_image_array.shape == exp_image_array.shape
        assert act_0 == exp[0]
        assert act_1 == exp[1]
        assert act_2 == exp[2]
        assert act_3 == exp[3]
        assert act_4 == exp[4]
        assert act_5 == exp[5]
        assert act_6 == exp[6]
        self.index += 1
        return
    
    def shutdown(self):
        """
        それぞれの接続を解除する。
        """
        self.subscriber.shutdown()
        self.publisher.shutdown()

class VehicleTest:
    """
    Donkeycar パッケージのVehicleフレームワークのパーツとして正常動作するかを確認するためのクラス。
    donkeypart_tub_loaderを使用する。
    """
    def __init__(self, conf_path=test_conf_path):
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

        self.vehicle.add(PubTelemetry(conf_path=conf_path, pub_count=0), inputs=tubitems)
        self.vehicle.add(TubPrinter(), inputs=tubitems)

        def wait():
            delay=3
            #print('wait {} seconds'.format(str(delay)))
            sleep(delay)
        self.vehicle.add(Lambda(wait))

        self.vehicle.add(SubTelemetry(conf_path=conf_path), outputs=tubitems)
        self.vehicle.add(TubPrinter(), inputs=tubitems)
        

    
    def test(self):
        try:
            self.vehicle.start(rate_hz=1, max_loop_count=5)
            assert True
        except StopIteration:
            pytest.fail('StopIteration occurs!')



def test_pub_sub():
    """
    テストメソッド。実際のテストはMosqTesterクラス内で実装されている。
    """
    try:
        tester = MosqTester()
        total = tester.exp_total
        for _ in range(total + 1):
            tester.test_tub()
        tester.shutdown()
    except ConnectionRefusedError:
        pytest.fail('need to up mosquitto')

def test_vehicle():
    """
    テストメソッド。Vehicleフレームワーク上で動作するかを確認する。
    """
    try:
        tester = VehicleTest()
        tester.test()
    except ConnectionRefusedError:
        pytest.fail('need to up mosquitto')


if __name__ == '__main__':
    """
    テストメソッドを呼び出す。
    """
    test_pub_sub()
    test_vehicle()