# ResultPreviewComponent

変換結果を表示し、KMLファイルを生成するコンポーネント。

## 使用方法

```tsx
import { ResultPreviewComponent } from './components';
import type { TransformedBox } from './types';

function App() {
  const [transformedBoxes, setTransformedBoxes] = useState<TransformedBox[]>([]);
  const [mapScale, setMapScale] = useState<number>(0);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [fileId, setFileId] = useState<string>('');

  const handleGenerateKML = () => {
    console.log('KML generated successfully');
  };

  return (
    <ResultPreviewComponent
      fileId={fileId}
      transformedBoxes={transformedBoxes}
      mapScale={mapScale}
      warnings={warnings}
      onGenerateKML={handleGenerateKML}
    />
  );
}
```

## Props

| Prop | Type | 説明 |
|------|------|------|
| `fileId` | `string` | アップロードされたファイルのID |
| `transformedBoxes` | `TransformedBox[]` | 変換された赤枠の配列 |
| `mapScale` | `number` | 推定された地図縮尺 |
| `warnings` | `string[]` | 警告メッセージの配列 |
| `onGenerateKML` | `() => void` | KML生成成功時のコールバック |

## 機能

1. **変換結果の表示**
   - 各赤枠の緯度経度（中心点と四隅）を表示
   - 赤枠の数を表示

2. **地図縮尺の表示**
   - 基準点から自動計算された縮尺を表示
   - 見やすい形式（1:25000など）で表示

3. **警告メッセージの表示**
   - 共線性エラーなどの警告を表示
   - 視覚的に目立つデザイン

4. **KML生成**
   - ボタンクリックでKMLファイルを生成
   - 生成中はローディング表示
   - エラー時はエラーメッセージを表示

5. **ダウンロード**
   - 生成されたKMLファイルのダウンロードリンクを表示
   - ファイル名を表示
   - ワンクリックでダウンロード

## スタイリング

コンポーネントは `ResultPreviewComponent.css` でスタイリングされています。
レスポンシブデザインに対応しており、モバイルデバイスでも適切に表示されます。

## 要件対応

- **要件 4.4**: 変換パラメータが計算される時、推定される地図の縮尺をユーザーに表示する
- **要件 4.5**: 基準点の配置が不適切である場合、警告メッセージを表示する
- **要件 5.4**: 座標計算が完了する時、計算結果をユーザーに表示する
- **要件 6.3**: 生成されたKMLファイルをユーザーがダウンロードできる機能を提供する
