# PDF Red Box KML Converter - Backend

FastAPIベースのバックエンドサービスで、PDF画像から赤枠（多角形）を検出し、KMLファイルを生成します。

## 主な機能

### PDF処理とアップロード
- PDFファイルを画像に変換（pdf2image使用）
- 最大ファイルサイズ: 10MB
- 一時ファイルの自動管理（TTL: 3600秒）

### 赤枠検出（多角形対応）
- 3〜50頂点の多角形を検出
- 最小面積500ピクセル、最小周囲長50ピクセルでフィルタリング
- 重複領域の自動除外
- 線状の細長い領域を除外（compactness < 0.01）
- 濃い赤枠と薄い赤塗りつぶし領域の両方に対応

### 座標変換
- アフィン変換による画像座標から地理座標への変換
- 最低3点の基準点が必要
- 変換精度の検証と警告

### KMLファイル生成
- Google マイマップ対応のKML形式で出力
- 多角形の地理座標を含む
- ファイルダウンロード機能

## セットアップ

### 必要要件

- Python 3.10以上
- poppler（pdf2imageの依存関係）

### インストール

1. 仮想環境を作成:
```bash
python -m venv venv
```

2. 仮想環境を有効化:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. 依存関係をインストール:
```bash
pip install -r requirements.txt
```

4. 環境変数を設定:
```bash
cp .env.example .env
# .envファイルを編集して必要な設定を行う
```

### 赤枠検出のパラメータ調整

小さい領域を除外したい場合、`.env`ファイルで以下のパラメータを調整できます：

```bash
# 最小面積（ピクセル）- 大きくすると小さい領域を除外
MIN_BOX_AREA=500    # デフォルト: 500 (推奨: 500-5000)

# 最小周囲長（ピクセル）- 大きくすると小さい領域を除外
MIN_BOX_PERIMETER=50  # デフォルト: 50 (推奨: 50-200)
```

**推奨値の目安:**
- 軽度のフィルタリング: `MIN_BOX_AREA=1000`, `MIN_BOX_PERIMETER=100`
- 中程度のフィルタリング: `MIN_BOX_AREA=2000`, `MIN_BOX_PERIMETER=150`
- 強力なフィルタリング: `MIN_BOX_AREA=5000`, `MIN_BOX_PERIMETER=200`

**注意:** これらの値を大きくしすぎると、隣接する領域が結合される可能性があります。モルフォロジー処理は最小限に抑えられていますが、値の調整は慎重に行ってください。

## 実行

開発サーバーを起動:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

APIドキュメント: http://localhost:8000/docs

## プロジェクト構造

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPIアプリケーション
│   ├── config.py            # 設定管理
│   ├── api/                 # APIエンドポイント
│   │   ├── upload.py        # PDFアップロードAPI
│   │   ├── detection.py     # 赤枠検出API
│   │   ├── transform.py     # 座標変換API
│   │   └── kml.py           # KML生成API
│   ├── models/              # データモデル
│   │   ├── schemas.py       # Pydanticスキーマ
│   │   └── errors.py        # カスタムエラー
│   ├── services/            # ビジネスロジック
│   │   ├── pdf_processor.py      # PDF処理
│   │   ├── red_box_detector.py   # 赤枠検出
│   │   ├── geo_transformer.py    # 座標変換
│   │   └── kml_generator.py      # KML生成
│   └── utils/               # ユーティリティ
│       └── logging_config.py
├── logs/                    # ログファイル
├── temp/                    # 一時ファイル
├── poppler/                 # Poppler実行ファイル（Windows）
├── test_*.py                # テストファイル
├── requirements.txt
├── setup_poppler.py         # Poppler自動セットアップ
├── .env.example
└── README.md
```

## API エンドポイント

### POST /api/upload
PDFファイルをアップロードして画像に変換

### POST /api/detect
アップロードされた画像から赤枠を検出

### POST /api/transform
画像座標を地理座標に変換

### GET /api/kml/{file_id}
KMLファイルを生成してダウンロード

詳細なAPIドキュメント: http://localhost:8000/docs
