# eclipse-mosquitto用MQTT通信動作確認プログラム

## 実行手順

### ブローカの起動

* ローカルPC上にDocker Desktopをインストール
* DOSパワーシェルを管理者権限で起動
* mosqディレクトリへ移動
* `docker-compose up -d`を実行する
* `docker-compose logs -f`で常時ログ監視

### Publisher
* AnacondaコンソールのようなPython3が実行可能なプロンプトを起動
* donkeyを有効化
   ```bash
   activate donkey
   ```

* `pub.py` を実行
   ```bash
   pip install paho-mqtt
   python pub.py
   ```

## Subscriber
* AnacondaコンソールのようなPython3が実行可能なプロンプトを起動
* donkeyを有効化
   ```bash
   activate donkey
   ```

* `sub.py` を実行
   ```bash
   pip install paho-mqtt
   python sub.py
   ```

## ブローカの停止

* ログ監視中のパワーシェル上でCtrl+Cを押してログ監視終了
* 以下のコマンドを実行
   ```bash
   docker-compose stop
   docker-compose rm -f
   docker systemm prune
   ```
   