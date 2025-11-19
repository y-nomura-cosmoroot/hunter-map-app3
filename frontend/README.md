# PDF Red Box KML Converter - Frontend

React + TypeScript + Vite フロントエンドアプリケーション

## 技術スタック

- **React 19.2** - UIフレームワーク
- **TypeScript 5.9** - 型安全性
- **Vite 7.2** - ビルドツール
- **Leaflet 1.9** - 地図ライブラリ
- **React Leaflet 5.0** - React用Leafletラッパー
- **Axios 1.13** - HTTP通信

## ディレクトリ構造

```
src/
├── components/     # Reactコンポーネント
│   ├── FileUploadComponent.tsx      # PDFファイルアップロード
│   ├── PDFViewerComponent.tsx       # PDF画像表示と赤枠選択
│   ├── MapComponent.tsx             # Leaflet地図コンポーネント
│   ├── ReferencePointManager.tsx   # 基準点管理
│   └── ResultPreviewComponent.tsx  # 変換結果とKML生成
├── services/       # APIサービスレイヤー
│   └── api.ts      # バックエンドAPI通信
├── types/          # TypeScript型定義
│   └── index.ts    # 共通型定義
├── App.tsx         # メインアプリケーション
└── App.css         # スタイル
```

## セットアップ

### 依存関係のインストール

```bash
npm install
```

### 開発サーバーの起動

```bash
npm run dev
```

アプリケーションは http://localhost:3000 で起動します。

### ビルド

```bash
npm run build
```

### プレビュー

```bash
npm run preview
```

## 環境変数

`.env.example`をコピーして`.env`ファイルを作成してください：

```bash
cp .env.example .env
```

## 主要な機能

### 1. PDFアップロード
- PDFファイルを画像に変換してアップロード
- 最大ファイルサイズ: 10MB
- 対応形式: PDF

### 2. 赤枠検出と選択
- 画像から赤枠（多角形）を自動検出
- 3〜50頂点の多角形に対応
- 検出された赤枠を個別に選択/解除可能
- 視覚的なプレビュー表示

### 3. 基準点設定
- PDF画像と地図上で対応する点をクリックして設定
- 最低3点の基準点が必要
- 基準点の編集・削除が可能
- リアルタイムプレビュー

### 4. 座標変換
- アフィン変換による画像座標から地理座標への変換
- 変換精度の警告表示
- 地図スケール計算

### 5. KML生成とダウンロード
- 変換結果をKMLファイルとして出力
- Google マイマップで直接インポート可能
- 変換結果の地図プレビュー

## ワークフロー

1. **アップロード** → PDFファイルを選択
2. **赤枠検出** → 自動検出された赤枠を確認・選択
3. **基準点設定** → PDF画像と地図上で対応点を設定（最低3点）
4. **座標変換** → 画像座標を地理座標に変換
5. **KML生成** → 結果をプレビューしてKMLファイルをダウンロード

## 開発ガイドライン

- コンポーネントは`components/`ディレクトリに配置
- API呼び出しは`services/api.ts`を経由
- 型定義は`types/index.ts`で一元管理
- CSSは各コンポーネントに対応する`.css`ファイルで管理
