# 実装タスクリスト

## バックエンド実装

- [x] 1. プロジェクト構造とコア設定のセットアップ





  - バックエンドのディレクトリ構造を作成（app/models, app/services, app/api, app/utils）
  - FastAPIアプリケーションの初期化とCORS設定
  - 環境変数管理（.envファイルとpydantic-settings）
  - ロギング設定
  - _要件: 1.1, 8.4_

- [x] 2. データモデルの実装





  - Pydanticモデルを定義（Point, GeoPoint, ReferencePoint, DetectedBox, TransformedBox）
  - リクエスト/レスポンスモデルを定義（UploadResponse, DetectionResponse, TransformRequest, TransformResponse, KMLRequest, KMLResponse）
  - バリデーションルールを実装（緯度経度の範囲チェック）
  - ErrorResponseモデルとエラーメッセージ辞書を作成
  - _要件: 3.7, 3.8, 3.9, 8.1, 8.2, 8.3_

- [x] 3. PDF処理モジュールの実装





  - PDFProcessorクラスを作成
  - pdf2imageを使用したPDF→画像変換機能を実装
  - 画像サイズ取得機能を実装
  - 画像リサイズ機能を実装（最大4000x4000ピクセル）
  - 一時ファイル管理機能を実装（UUID生成、保存、TTL管理）
  - _要件: 1.2, 1.4_

- [x] 4. ファイルアップロードAPIエンドポイントの実装






  - POST /api/uploadエンドポイントを作成
  - multipart/form-dataでのファイル受信
  - ファイル形式検証（MIMEタイプとPDF拡張子チェック）
  - ファイルサイズ制限（最大50MB）
  - PDFProcessorを呼び出して画像変換
  - UploadResponseを返却
  - エラーハンドリング（無効なファイル形式、サイズ超過）
  - _要件: 1.1, 1.2, 1.3, 1.4_

- [x] 5. 赤枠検出モジュールの実装





  - RedBoxDetectorクラスを作成
  - OpenCVを使用した画像読み込み
  - HSV色空間への変換機能
  - 濃い赤枠検出機能を実装（Cannyエッジ検出、輪郭検出、矩形近似）
  - 薄い赤の塗りつぶし領域検出機能を実装（色範囲マスク、モルフォロジー処理、輪郭検出）
  - 検出結果をDetectedBoxモデルに変換
  - 赤枠の四隅座標と中心点を計算
  - _要件: 2.1, 2.2, 2.3_

- [x] 6. 赤枠検出APIエンドポイントの実装





  - POST /api/detect-boxesエンドポイントを作成
  - file_idから画像ファイルを取得
  - RedBoxDetectorを呼び出して赤枠を検出
  - DetectionResponseを返却（検出された赤枠リストと数）
  - エラーハンドリング（ファイルが存在しない、赤枠が検出されない）
  - _要件: 2.3, 2.4, 2.5_

- [x] 7. 座標変換モジュールの実装





  - GeoTransformerクラスを作成
  - NumPyを使用したアフィン変換行列の計算（最小二乗法）
  - 基準点の配置検証（共線性チェック）
  - 画像座標から緯度経度への変換機能
  - 地図縮尺の推定機能（Haversine公式を使用）
  - _要件: 4.1, 4.2, 4.3, 4.4, 4.5, 5.2_

- [x] 8. 座標変換APIエンドポイントの実装





  - POST /api/transformエンドポイントを作成
  - TransformRequestを受信（file_id, reference_points, boxes）
  - 基準点が3つ以上あることを検証
  - GeoTransformerを呼び出してアフィン変換行列を計算
  - 選択された赤枠の四隅と中心点の緯度経度を計算
  - 地図縮尺を推定
  - TransformResponseを返却（transformed_boxes, map_scale, warnings）
  - エラーハンドリング（基準点不足、共線性エラー）
  - _要件: 3.11, 3.12, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 9. KML生成モジュールの実装





  - KMLGeneratorクラスを作成
  - simplekmlを使用したKMLファイル生成
  - Polygon要素の作成（四隅の座標を使用）
  - KML 2.2標準に準拠した構造
  - ファイル名に日時情報を含める
  - _要件: 6.1, 6.2, 6.4, 6.5_

- [x] 10. KML生成APIエンドポイントの実装





  - POST /api/generate-kmlエンドポイントを作成
  - KMLRequestを受信（file_id, boxes）
  - KMLGeneratorを呼び出してKMLファイルを生成
  - 生成されたKMLファイルを一時ディレクトリに保存
  - KMLResponseを返却（download_url, filename）
  - _要件: 6.1, 6.2, 6.3, 6.4_

- [x] 11. KMLファイルダウンロードエンドポイントの実装





  - GET /api/download/{filename}エンドポイントを作成
  - ファイルの存在確認
  - FileResponseでKMLファイルを返却
  - Content-Dispositionヘッダーを設定
  - _要件: 6.3_

## フロントエンド実装

- [x] 13. Reactプロジェクトのセットアップ





  - Create React AppまたはViteでプロジェクトを作成
  - TypeScript設定
  - 必要なライブラリをインストール（axios, react-leaflet, leaflet）
  - ディレクトリ構造を作成（components, services, types, utils）
  - _要件: 1.1_

- [x] 14. TypeScript型定義の作成





  - 型定義ファイルを作成（types/index.ts）
  - Point, GeoPoint, ReferencePoint, DetectedBox, TransformedBox, MapMarkerインターフェースを定義
  - APIレスポンス型を定義
  - _要件: すべての要件に関連_

- [x] 15. APIサービスレイヤーの実装





  - axiosインスタンスを作成（ベースURL設定）
  - uploadPDF関数を実装
  - detectBoxes関数を実装
  - transformCoordinates関数を実装
  - generateKML関数を実装
  - エラーハンドリング（日本語エラーメッセージの表示）
  - _要件: 1.1, 2.4, 5.4, 6.3, 8.1_

- [x] 16. FileUploadComponentの実装





  - ファイル選択UIを作成
  - ドラッグ&ドロップ機能を実装
  - アップロード進捗表示
  - uploadPDF APIを呼び出し
  - 成功時にonUploadSuccessコールバックを実行
  - エラー時にエラーメッセージを表示
  - _要件: 1.1, 1.2, 1.3_

- [x] 17. PDFViewerComponentの実装





  - Canvas要素を作成
  - 画像の読み込みと描画
  - ズーム機能（マウスホイール）
  - パン機能（ドラッグ）
  - クリック位置の座標取得
  - 基準点マーカーの表示
  - 検出された赤枠の重ね表示
  - 赤枠の選択/選択解除機能（クリックまたはチェックボックス）
  - _要件: 2.3, 3.2, 7.1, 7.2, 7.3, 7.4_

- [x] 18. MapComponentの実装





  - react-leafletを使用した地図コンポーネント
  - 初期表示位置とズームレベルの設定
  - クリックイベントハンドラー（緯度経度を取得）
  - onLocationSelectコールバックを実行
  - 基準点マーカーの表示
  - マーカーにラベルを表示
  - _要件: 3.3, 3.4, 3.5_

- [x] 19. ReferencePointManagerの実装





  - 基準点リストの表示（テーブルまたはカード形式）
  - 各基準点の画像座標と緯度経度を表示
  - 削除ボタンの実装
  - 手動編集機能（緯度経度の直接入力）
  - 基準点が3つ未満の場合の警告表示
  - _要件: 3.1, 3.6, 3.10, 3.11, 3.12, 3.13_

- [x] 20. ResultPreviewComponentの実装





  - 変換結果の表示（各赤枠の緯度経度）
  - 推定された地図縮尺の表示
  - 警告メッセージの表示（共線性など）
  - KML生成ボタン
  - generateKML APIを呼び出し
  - ダウンロードリンクの表示
  - _要件: 4.4, 4.5, 5.4, 6.3_

- [x] 21. メインアプリケーションの統合





  - App.tsxでステート管理を実装
  - 各コンポーネントを配置
  - ワークフローの実装（アップロード→検出→基準点設定→変換→KML生成）
  - ステップインジケーターの表示
  - エラー表示エリアの実装
  - _要件: すべての要件に関連_
