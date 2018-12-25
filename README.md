# Donkeypart Telemetry


Donkey Car上のパーツからMQTTブローカへ送信されているデータを可視化テレメトリプログラム　Donkey Telemeter へデータを送り出すDonkeyパーツプログラムを提供する。

## システム構成

MQTTをハブとした非同期通信で実現している。

![Donkey Telemetry アーキテクチャ](./assets/architecture.png)

* [Donkey Car](http://www.donkeycar.com/)
   自律走行をRaspberryPiや市販のRCカーで実現できるオープンソースの自動運転プラットフォーム。
* [IBM Watson IoT Platform](https://www.ibm.com/jp-ja/marketplace/internet-of-things-cloud)
   IBM Cloud上で提供しているMQTTブローカサービス。検証はライトプランの無料枠で実施。
- [Glitch.com](https://glitch.com)
   Node.js開発・実行環境を無料で提供してくれるサービス。シェルコンソールもありpython3.xも既にインストール済みであるため、テストスクリプトの実行も可能。GitHub連携可能。

### Donkey Car

[Donkey Car](http://www.donkeycar.com/)とは、Raspberry Piを市販のRCカーに搭載して、安価に自動運転を実現するプラットフォームである。

自動運転のための[プログラム](https://github.com/autorope/donkeycar)や一部の改造用パーツの[設計図](https://www.thingiverse.com/thing:2260575)がオープンソース化されている。またコミュニティが運営しているネット店舗（[Donkey Store/US](https://squareup.com/store/donkeycar)/[Robocar Store/香港](https://www.robocarstore.com/)）よりフルキットで購入することも可能である。

組み立て方は[ドキュメント](https://github.com/coolerking/donkeycar_jpdocs)やこちらの[スライド](https://www.slideshare.net/HoriTasuku/donkey-car)を参考にすれば、RCカーやRaspberry Piの結線に関する経験の少ない人でも制作することができる。

![Donkey Car](./assets/donkeycar.jpg)

* Donkey Car は Vehiecleフレームワークを採用しており、登録された一連の作業をループすることができる
* 指定されたメソッドを実装したパーツと呼ばれるPythonクラスを作成すると、Vehicleフレームワークへ追加することができる
* パーツに実装する"一連の作業"は同期処理、非同期処理どちらでも実装可能である

### Donkeypart Telemetry

本リポジトリでは、MQTTブローカへPublishするパーツおよびMQTTブローカからメッセージを受け取るSubscriberパーツの２つを提供する。

IBM Watson IoT Platform用 は [./iotf/part.py](./iotf/part.py)に、eclipse-mosquitte用 は [./mosq/part.py](./mosq/part.py) に実装が存在する。

#### Publisher パーツ

- テレメトリー用Publisherパーツ `PubTelemetry`
   リアルタイムのスロットル値、アングル値の監視ができるように、MQTTブローカへ送信するパーツをPublisherのサンプルとして作成した。


#### Subscriber パーツ

- 外部のオートパイロットサーバから操作情報を取得するパーツ `SubPilot`
   PubTelemetryとは逆に、スロットル値、アングル値を外部のサーバから受け取るためのパーツをサンプルとして作成した。ただし、判断要素となるイメージファイルデータを送信していないため、本格的に外部ノード上で推論処理を実行させるには、機能が不足している。あくまで参考の実装の位置づけである。


### Donkey Telemetry

Donkeypart TelemetryによってMQTTブローカへpublishしているデータを参照することのできるWeb UI。

詳細は、[GitHubリポジトリ coolerking/donkey_telemetry](https://github.com/coolerking/donkey_telemetry)を参照のこと。


## ライセンス

本リポジトリ上のコンテンツはすべて[MITライセンス](./LICENSE)準拠とする。







