# 要件定義書

## はじめに

本システムは、PDF画像から赤枠（濃い赤枠、薄い赤で中が塗りつぶされたもの）を検出し、地理座標情報を含むKMLファイルを生成するアプリケーションです。ユーザーはPDF画像をアップロードし、必要な地理参照情報を入力することで、検出された赤枠の位置を緯度経度に変換したKMLファイルを取得できます。

## 用語集

- **System**: PDF赤枠KML変換システム
- **User**: システムを使用してPDF画像からKMLファイルを生成するユーザー
- **PDF Image**: 地図を含むPDFファイル
- **Red Box**: PDF画像内の赤枠（濃い赤枠、または薄い赤で中が塗りつぶされた矩形）
- **KML File**: 地理座標情報を含むKeyhole Markup Language形式のファイル
- **Geo-reference Point**: PDF画像上の特定位置に対応する実際の緯度経度座標。ユーザーは対話型地図をクリックして設定する
- **Interactive Map**: Google MapsまたはLeafletを使用した、クリックで緯度経度を取得できる地図インターフェース
- **Affine Transformation**: PDF画像上の座標を実際の緯度経度に変換するための数学的変換
- **Map Scale**: PDF画像内の地図の拡大率（縮尺）、基準点から自動計算される

## 要件

### 要件1

**ユーザーストーリー:** ユーザーとして、PDF画像をシステムにアップロードできるようにしたい。そうすることで、画像内の赤枠を検出してKMLファイルを生成できるようになる。

#### 受入基準

1. THE System SHALL PDFファイルのアップロード機能を提供する
2. WHEN UserがPDFファイルを選択する, THE System SHALL ファイル形式がPDFであることを検証する
3. IF アップロードされたファイルがPDF形式でない, THEN THE System SHALL エラーメッセージを表示する
4. WHEN PDFファイルのアップロードが成功する, THE System SHALL ファイルを画像形式に変換する

### 要件2

**ユーザーストーリー:** ユーザーとして、PDF画像から赤枠を自動検出できるようにしたい。そうすることで、手動で座標を入力する手間を省ける。

#### 受入基準

1. THE System SHALL PDF画像から濃い赤枠を検出する
2. THE System SHALL PDF画像から薄い赤で中が塗りつぶされた矩形を検出する
3. WHEN 赤枠が検出される, THE System SHALL 各赤枠の画像上の座標（ピクセル位置）を記録する
4. WHEN 赤枠が検出される, THE System SHALL 検出された赤枠の数をUserに表示する
5. IF 赤枠が検出されない, THEN THE System SHALL Userに通知メッセージを表示する

### 要件3

**ユーザーストーリー:** ユーザーとして、PDF画像の地理参照情報を簡単に入力できるようにしたい。そうすることで、画像上の座標を実際の緯度経度に変換できるようになる。

#### 受入基準

1. THE System SHALL Userに最低3つの基準点を設定するインターフェースを提供する
2. THE System SHALL Userに各基準点のPDF画像上の位置をクリックで指定する機能を提供する
3. THE System SHALL 対話型地図インターフェース（Google MapsまたはLeaflet）を表示する
4. WHEN Userが地図上の位置をクリックする, THE System SHALL その位置の緯度経度を自動取得する
5. THE System SHALL 取得された緯度経度を基準点として記録する
6. THE System SHALL Userが手動で緯度経度を入力する代替手段も提供する
7. THE System SHALL 入力された緯度が-90度から90度の範囲内であることを検証する
8. THE System SHALL 入力された経度が-180度から180度の範囲内であることを検証する
9. IF 入力された座標値が有効範囲外である, THEN THE System SHALL エラーメッセージを表示する
10. THE System SHALL Userが3つ以上の基準点を追加できる機能を提供する
11. IF Userが入力した基準点が3つ未満である, THEN THE System SHALL 座標変換処理を実行しない
12. WHEN Userが3つ未満の基準点で処理を実行しようとする, THE System SHALL 最低3つの基準点が必要であることを通知する
13. THE System SHALL 各基準点にPDF画像上の位置と地図上の位置を対応付けて表示する

### 要件4

**ユーザーストーリー:** ユーザーとして、座標変換パラメータを自動計算できるようにしたい。そうすることで、手動で拡大率を入力する手間とエラーを削減できる。

#### 受入基準

1. WHEN Userが3つ以上の基準点を入力する, THE System SHALL アフィン変換行列を計算する
2. THE System SHALL 基準点のPDF画像上の座標と実際の緯度経度から変換パラメータを導出する
3. THE System SHALL 計算された変換パラメータの精度を検証する
4. WHEN 変換パラメータが計算される, THE System SHALL 推定される地図の縮尺をUserに表示する
5. IF 基準点の配置が不適切である（例：3点が一直線上にある）, THEN THE System SHALL 警告メッセージを表示する

### 要件5

**ユーザーストーリー:** ユーザーとして、検出された赤枠の緯度経度を自動計算できるようにしたい。そうすることで、手動計算の手間とエラーを削減できる。

#### 受入基準

1. WHEN Userが3つ以上の基準点を入力する, THE System SHALL 各赤枠の四隅の緯度経度を計算する
2. THE System SHALL 計算されたアフィン変換行列を使用して座標変換を実行する
3. THE System SHALL 計算された緯度経度の精度を小数点以下6桁まで保持する
4. WHEN 座標計算が完了する, THE System SHALL 計算結果をUserに表示する
5. THE System SHALL 各赤枠の中心点の緯度経度も計算する

### 要件6

**ユーザーストーリー:** ユーザーとして、検出された赤枠の情報を含むKMLファイルを生成できるようにしたい。そうすることで、Google EarthなどのGISアプリケーションで結果を可視化できる。

#### 受入基準

1. THE System SHALL 検出された各赤枠の緯度経度を含むKMLファイルを生成する
2. THE System SHALL KMLファイル内に各赤枠をPolygon要素として記述する
3. THE System SHALL 生成されたKMLファイルをUserがダウンロードできる機能を提供する
4. WHEN KMLファイルが生成される, THE System SHALL ファイル名に日時情報を含める
5. THE System SHALL 生成されたKMLファイルがKML 2.2標準に準拠することを保証する

### 要件7

**ユーザーストーリー:** ユーザーとして、検出された赤枠をプレビュー表示できるようにしたい。そうすることで、KMLファイル生成前に検出結果を確認できる。

#### 受入基準

1. WHEN 赤枠が検出される, THE System SHALL PDF画像上に検出された赤枠を重ねて表示する
2. THE System SHALL 各赤枠に識別番号を表示する
3. THE System SHALL Userが個別の赤枠を選択または選択解除できる機能を提供する
4. WHEN Userが赤枠を選択解除する, THE System SHALL その赤枠をKMLファイル生成から除外する

### 要件8

**ユーザーストーリー:** ユーザーとして、エラーが発生した場合に明確なメッセージを受け取りたい。そうすることで、問題を理解して適切に対処できる。

#### 受入基準

1. WHEN エラーが発生する, THE System SHALL Userに理解しやすい日本語のエラーメッセージを表示する
2. THE System SHALL エラーメッセージに問題の原因を含める
3. THE System SHALL エラーメッセージに推奨される対処方法を含める
4. IF システムエラーが発生する, THEN THE System SHALL エラーログを記録する
