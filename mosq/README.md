# eclipse-mosquitto 用 Donkey Carパーツサンプル

## 概要
[part.py](./part.py) には、Publisherサンプルである `PubTelemetry` と Subscriberサンプルの `SubPilot` の２つのクラスを提供しているが、本ドキュメントでは前者側のインストール方法のみ紹介する。

## インストール

### ブローカの作成

1. Donkey Car と同じWiFiに接続されたPCへ[eclipse-mosquitto](https://mosquitto.org/download/)をインストール
2. `eclipse-mosquitto`の起動
3. PCのIPアドレスをメモ


### Publisherの追加

1. `mosq/template.yaml`を`mosq/<ブローカのホスト名>.yaml`へコピー
2. `mosq/<ブローカのホスト名>.yaml` を編集
   ```yaml
   broker:
     host: '127.0.0.1' # IPアドレスを変更する
     port: 1883
    publisher:
      topic: 'mosq/evt/status/fmt'
    subscriber:
      topic: 'mosq/evt/status/fmt'
   ```
3. `mosq/__init__.py` と `mosq/<ブローカのホスト名>.yaml`をraspberry Pi上の`~/mycar/mosq`へコピー
4. `manage.py`にインポート行を追加
   ```python
   from mosq import PubTelemetry
   ```
5. `manage.py`の`V.start()`直前に以下のコードを追加
   ```python
    tele = PubTelemetry('mosq/<ブローカのホスト名>.yaml', pub_count=20*5, debug=False)
    V.add(tele, inputs=['cam/image_array', 'user/mode', 'user/angle', 'user/throttle',
                  'pilot/angle', 'pilot/throttle'])
   ```

## Donkey Carの運転開始

1. Raspberry Pi上で `manage.py` を実行
   ```python
   # 手動運転
   python manage.py drive --js
   # 自動運転(Web UIから自動運転モードを設定すると運転開始)
   python manage.py drive --model models/mypilot
   ```
   
