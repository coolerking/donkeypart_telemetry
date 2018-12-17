# IBM Watson IoT Platform 用MQTT通信動作確認プログラム

## 実行手順

### ブローカの作成

* IBM Cloud コンソールを開く
* ログイン
* 「カタログ」を選択
* 「IoT」> 「Internet of Things Platform」
* 「デプロイする地域/ロケーションの選択」を適当に選択
* 「組織の選択」を適当に選択
* 「スペースの選択」を適当に選択
* 画面右下の「作成」押下
* ダッシュボード画面のCloudFoundryサービス上から作成したサービスを選択
* 「起動」押下

### デバイス（Publisher）の追加

* 「＋デバイスの追加」押下
* 「デバイスタイプ」に`donkeycar`と入力
* 「デバイスID」にDonkeyCar固有名を入力（例：RaspberryPiのホスト名やMacアドレス）
* 「次へ」押下
* 「次へ」押下
* 「次へ」押下
* 「完了」押下
* 画面に表示された、組織ID、デバイスタイプ、デバイスID、認証トークンをメモしておく

実際に接続しているかどうかを確認したい場合は、該当デバイスを選択することで詳細な状態確認可能。

* ローカルPC上の`device.ini`を`<デバイスID>.ini`という名前でコピー
* `<デバイスID>.ini`を編集
 * `{}`部分をすべて編集
 * `auth-metho`行は編集不要
 * `clean-session` 行は`true`としておく

### アプリケーション（Subscriber）の追加

* 画面左のメニューから「アプリ」を選択
* 「＋APIキーの生成」押下
* 「説明」を適当に入力
* 「次へ」押下
* 「キーの生成」押下
* 画面に表示された、APIキー、認証トークンをメモしておく
* 「閉じる」押下
* 「クローズの確認」押下

実際に接続しているかどうかを確認したい場合は、該当アプリケーションを選択することで詳細な状態確認可能。

* アプリケーションIDを決める
* ローカルPC上の`application.ini`を`<アプリケーションID>.ini`という名前でコピー
* `<アプリケーションID>.ini`を編集
 * `{}`部分をすべて編集
 * `auth-metho`行は編集不要
 * `clean-session` 行は`true`としておく

### Publisher の実行
* AnacondaコンソールのようなPython3が実行可能なプロンプトを起動
* `pub.py` を実行
   ```bash
   pip install docopt
   pip install ibmiotf
   python pub.py --conf <デバイスID>.iniのフルパス
   ```

一定時間に複数件publishしたら終了してしまうので、Subscriberで確認したい場合は、すぐに起動する必要がある。

## Subscriber
* AnacondaコンソールのようなPython3が実行可能なプロンプトを起動
* `pub.py` を実行
   ```bash
   pip install docopt
   pip install ibmiotf
   python pub.py --conf <アプリケーションID>.iniのフルパス
   ```

停止させるにはCtrl+Cを押す。

