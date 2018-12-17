# Donkey Telemetry v2

## 概要
走行中のDonkey Carより定期的にMQTTブローカ(IBM Watson IoT Platform)へ送信しており、
このデータをglitch上のnodeでsubsvcribe、受信した中で最新のデータを可視化する。


## インストール

1. IBM Watson IoT Platform をセットアップ

* インスタンスを作成
* コンソールからデバイスを登録
* デバイスのpublisherプログラム側に以下の項目をセット
 - 組織ID
 - デバイスタイプ
 - デバイスID
 - 認証トークン
* コンソールからアプリケーションを登録
* アプリケーションプログラム側に以下の項目をセット
 - 組織ID
 - アプリケーションID(コンソールから得られない項目、一意になるように各自で適当に決定する)
 - API キー
 - 認証トークン

 * 通常のNode.js実行環境の場合は、`server.js`の`appClientConfig`内に記述
 * Glitchの場合は、`.env`に記述

* Node.js プログラムを開始

 * 通常のNode.js実行環境の場合は、以下のように実行
   ```bash
   cd <project_top>
   npm install
   node server.js
   ```

 * Glitchの場合は、配置した時点で更新される

## 使用ソフトウェア

[Donkey Car](http://www.donkeycar.com/)
------------
donkeycar OSS ベースで構築したDonkey Carに、独自のMQTT Publisherパーツを作成し、Vehiecle フレームワークにaddして動作させている。Donkey CarはMITライセンス準拠である。

[IBM Watson IoT Platform](https://console.bluemix.net/services/iotf-service/)
------------
IBM Cloud コンソールより、ダラスの無料プランを使ってMQTTブローカを立てている。
動作確認はライトプランの無料版環境を使用した。

[Node.js](https://nodejs.org/ja/)
-----------
Node.jsはMITライセンス準拠のサーバサイドJavascriptアプリケーションエンジンです。

[express](https://expressjs.com/ja/)
------------
express を使っているWebサーバコンテンツにAjaxを使って定期的に図を再描画させている。
expressは[Creative Commons Attribution-ShareAlike 3.0](https://github.com/expressjs/expressjs.com/blob/gh-pages/LICENSE.md)準拠のOSSである。

[Node.js Client Library](https://github.com/ibm-watson-iot/iot-python)
------------
JavaScript 上での IBM Watson IoT Platformとの接続には、ibmiotfパッケージを使用している。
package.jsonに記述しているので、通常のセットアップ（`npm install`）でパッケージがインストールされる。
ibmiotfパッケージは、Eclipse Public License1.0準拠のOSSである。

[D3.js](https://d3js.org/) / [VizJS](https://github.com/NPashaP/Viz) [GaugeIII](http://bl.ocks.org/npashap/a9cefa705b63ff4ab2297b855a79f1aa)
------------
グラフ化にはBSDライセンス準拠の視覚化ライブラリD3.jsを使用した。
D3.js サイトで公開されていたBSD-3ーClauseライセンス準拠の[VizJS](https://github.com/NPashaP/Viz)および[サンプルコードGaugeIII](http://bl.ocks.org/NPashaP/a9cefa705b63ff4ab2297b855a79f1aa)を流用した。

[jQuerry](https://jquery.com/)
------------
Ajax処理にはjQuerry上の機能を使用した。jQuerryはMITライセンス準拠である。

Made by [Glitch](https://glitch.com/)
-------------------
動作確認で使用したnode.js実行環境PaaS。
