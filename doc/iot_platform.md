# PubTelemetry with IBM Watson IoT Platform

Donkey Telemetryを使用する場合は `PubTelemetry` クラスを `manage.py` に追加する。

## 注意事項

* Quickstart環境はイメージデータを送信できないためPubTelemetry/SubTelemetryが動作しない
* 以下の手順は、ライトアカウント・Freeプランを用いて動作検証を行った

## セットアップ

### ブローカの作成

1. IBM Cloud コンソールを開く
2. ログイン
3. 「カタログ」を選択
4. 「IoT」> 「Internet of Things Platform」
5. 「デプロイする地域/ロケーションの選択」を適当に選択
6. 「組織の選択」を適当に選択
7. 「スペースの選択」を適当に選択
8. 画面右下の「作成」押下
9. ダッシュボード画面のCloudFoundryサービス上から作成したサービスを選択
10. 「起動」押下

## デバイス（Publisher）の追加

1. 「＋デバイスの追加」押下
2. 「デバイスタイプ」に`donkeycar`と入力
3. 「デバイスID」にDonkeyCar固有名を入力（例：RaspberryPiのホスト名やMacアドレス）
4. 「次へ」押下
5. 「次へ」押下
6. 「次へ」押下
7. 「完了」押下
8. 画面に表示された、組織ID、デバイスタイプ、デバイスID、認証トークンをメモしておく

実際に接続しているかどうかを確認したい場合は、該当デバイスを選択することで詳細な状態確認可能。

1. ローカルPC上の`device.ini`を`<デバイスID>.ini`という名前でコピー
2. `<デバイスID>.ini`を編集
3. `{}`部分をすべて編集
4. `auth-metho`行は編集不要
5. `clean-session` 行は`true`としておく
6. `part.py` と `<デバイスID>.ini`をraspberry Pi上の`~/mycar/iotf`へコピー
7. `manage.py`にインポート行を追加
   ```python
   from donkeypart_telemetry.iotf import PubTelemetry
   ```
8. `manage.py`の`V.start()`直前に以下のコードを追加
   ```python
    # テレメトリーデータの送信
    tubitems = [
        'cam/image_array',
        'user/mode',
        'user/angle',
        'user/throttle',
        'pilot/angle',
        'pilot/throttle',
        'angle',
        'throttle']
    tele = PubTelemetry('iotf/emperor.ini', pub_count=2000)
    V.add(tele, inputs=tubitems)
   ```

## Donkey Carの運転開始

1. Raspberry Pi上で `manage.py` を実行
   ```python
   # 手動運転
   python manage.py drive --js
   # 自動運転
   python manage.py drive --model models/mypilot
   ```
   
