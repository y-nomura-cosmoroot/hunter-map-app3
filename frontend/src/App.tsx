import { useState } from 'react';
import './App.css';
import FileUploadComponent from './components/FileUploadComponent';
import PDFViewerComponent from './components/PDFViewerComponent';
import MapComponent from './components/MapComponent';
import ReferencePointManager from './components/ReferencePointManager';
import ResultPreviewComponent from './components/ResultPreviewComponent';
import { detectBoxes, transformCoordinates } from './services/api';
import type {
  ReferencePoint,
  DetectedBox,
  TransformedBox,
  MapMarker,
  Point
} from './types';

type WorkflowStep = 'upload' | 'detect' | 'reference' | 'transform' | 'result';

function App() {
  // Workflow state
  const [currentStep, setCurrentStep] = useState<WorkflowStep>('upload');
  const [error, setError] = useState<string>('');

  // File state
  const [fileId, setFileId] = useState<string>('');
  const [imageUrl, setImageUrl] = useState<string>('');
  const [, setImageWidth] = useState<number>(0);
  const [, setImageHeight] = useState<number>(0);

  // Detection state
  const [detectedBoxes, setDetectedBoxes] = useState<DetectedBox[]>([]);
  const [selectedBoxIds, setSelectedBoxIds] = useState<string[]>([]);

  // Reference points state
  const [referencePoints, setReferencePoints] = useState<ReferencePoint[]>([]);
  const [pendingImagePoint, setPendingImagePoint] = useState<Point | null>(null);

  // Transform state
  const [transformedBoxes, setTransformedBoxes] = useState<TransformedBox[]>([]);
  const [mapScale, setMapScale] = useState<number>(0);
  const [warnings, setWarnings] = useState<string[]>([]);

  // Step 1: Handle file upload
  const handleUploadSuccess = async (
    uploadedFileId: string,
    uploadedImageUrl: string,
    width: number,
    height: number
  ) => {
    setFileId(uploadedFileId);
    setImageUrl(uploadedImageUrl);
    setImageWidth(width);
    setImageHeight(height);
    setError('');

    // Automatically detect boxes
    try {
      const response = await detectBoxes(uploadedFileId);
      setDetectedBoxes(response.boxes);
      setSelectedBoxIds(response.boxes.map(box => box.id));
      setCurrentStep('detect');
    } catch (err) {
      setError(err instanceof Error ? err.message : '赤枠の検出に失敗しました');
    }
  };

  const handleUploadError = (errorMessage: string) => {
    setError(errorMessage);
  };

  // Step 2: Handle box selection
  const handleBoxToggle = (boxId: string) => {
    setSelectedBoxIds(prev =>
      prev.includes(boxId)
        ? prev.filter(id => id !== boxId)
        : [...prev, boxId]
    );
  };

  const handleProceedToReference = () => {
    if (selectedBoxIds.length === 0) {
      setError('少なくとも1つの赤枠を選択してください');
      return;
    }
    setError('');
    setCurrentStep('reference');
  };

  // Step 3: Handle reference point setting
  const handlePDFClick = (x: number, y: number) => {
    if (currentStep !== 'reference') return;

    setPendingImagePoint({ x, y });
    setError(''); // Clear any previous errors
  };

  const handleMapClick = (lat: number, lng: number) => {
    if (currentStep !== 'reference' || !pendingImagePoint) return;

    const newPoint: ReferencePoint = {
      id: `ref-${Date.now()}`,
      imagePoint: pendingImagePoint,
      geoPoint: { lat, lng }
    };

    setReferencePoints(prev => [...prev, newPoint]);
    setPendingImagePoint(null);
    setError('');
  };

  const handlePointDelete = (index: number) => {
    setReferencePoints(prev => prev.filter((_, i) => i !== index));
  };

  const handlePointEdit = (index: number, point: ReferencePoint) => {
    setReferencePoints(prev =>
      prev.map((p, i) => i === index ? point : p)
    );
  };

  // Step 4: Handle coordinate transformation
  const handleTransform = async () => {
    if (referencePoints.length < 3) {
      setError('最低3つの基準点を設定してください（現在: ' + referencePoints.length + '個）');
      return;
    }

    try {
      setError('');
      const response = await transformCoordinates({
        file_id: fileId,
        reference_points: referencePoints,
        boxes: selectedBoxIds
      });

      setTransformedBoxes(response.transformed_boxes);
      setMapScale(response.map_scale);
      setWarnings(response.warnings || []);
      setCurrentStep('result');
    } catch (err) {
      setError(err instanceof Error ? err.message : '座標変換に失敗しました');
    }
  };

  // Step indicator
  const steps = [
    { id: 'upload', label: 'アップロード' },
    { id: 'detect', label: '赤枠検出' },
    { id: 'reference', label: '基準点設定' },
    { id: 'transform', label: '座標変換' },
    { id: 'result', label: 'KML生成' }
  ];

  const getStepIndex = (step: WorkflowStep): number => {
    return steps.findIndex(s => s.id === step);
  };

  const currentStepIndex = getStepIndex(currentStep);

  // Map markers for reference points
  const mapMarkers: MapMarker[] = referencePoints.map((point, index) => ({
    position: point.geoPoint,
    label: `基準点 ${index + 1}`
  }));

  // Reset workflow
  const handleReset = () => {
    setCurrentStep('upload');
    setFileId('');
    setImageUrl('');
    setDetectedBoxes([]);
    setSelectedBoxIds([]);
    setReferencePoints([]);
    setPendingImagePoint(null);
    setTransformedBoxes([]);
    setMapScale(0);
    setWarnings([]);
    setError('');
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-text">
            <h1>マイマップ用KMLファイル作成アプリ</h1>
            <p className="app-description">
              PDF画像から赤枠を検出し、地理座標情報を含むKMLファイルを生成します
            </p>
          </div>
          <div className="step-indicator">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className={`step ${index <= currentStepIndex ? 'active' : ''} ${index === currentStepIndex ? 'current' : ''}`}
              >
                <div className="step-number">{index + 1}</div>
                <div className="step-label">{step.label}</div>
              </div>
            ))}
          </div>
        </div>
      </header>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
          <button
            className="error-close"
            onClick={() => setError('')}
          >
            ×
          </button>
        </div>
      )}

      {/* Warnings Display */}
      {warnings.length > 0 && (
        <div className="warning-message">
          <span className="warning-icon">⚠️</span>
          <div>
            {warnings.map((warning, index) => (
              <div key={index}>{warning}</div>
            ))}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="app-content">
        {/* Step 1: Upload */}
        {currentStep === 'upload' && (
          <div className="step-content">
            <h2>ステップ 1: PDFファイルをアップロード</h2>
            <FileUploadComponent
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
            />
          </div>
        )}

        {/* Step 2: Detect and Select Boxes */}
        {currentStep === 'detect' && (
          <div className="step-content">
            <h2>ステップ 2: 赤枠の検出と選択</h2>
            <p className="step-instruction">
              検出された赤枠を確認し、KMLファイルに含める赤枠を選択してください
            </p>
            <PDFViewerComponent
              imageUrl={imageUrl}
              referencePoints={[]}
              onPointClick={() => { }}
              detectedBoxes={detectedBoxes}
              selectedBoxes={selectedBoxIds}
              onBoxToggle={handleBoxToggle}
            />
            <div className="step-actions">
              <button onClick={handleReset} className="btn-secondary">
                最初からやり直す
              </button>
              <button
                onClick={handleProceedToReference}
                className="btn-primary"
                disabled={selectedBoxIds.length === 0}
              >
                次へ: 基準点設定
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Set Reference Points */}
        {currentStep === 'reference' && (
          <div className="step-content">
            <h2>ステップ 3: 基準点の設定</h2>
            <p className="step-instruction">
              {pendingImagePoint
                ? '地図上で対応する位置をクリックしてください'
                : 'PDF画像上の既知の位置をクリックしてください（最低3点必要）'}
            </p>

            <div className="reference-point-grid">
              <div className="reference-point-section">
                <h3>PDF画像</h3>
                <PDFViewerComponent
                  imageUrl={imageUrl}
                  referencePoints={referencePoints}
                  onPointClick={handlePDFClick}
                  detectedBoxes={detectedBoxes}
                  selectedBoxes={selectedBoxIds}
                  onBoxToggle={() => { }}
                  pendingImagePoint={pendingImagePoint}
                />
              </div>

              <div className="reference-point-section">
                <h3>地図</h3>
                <MapComponent
                  onLocationSelect={handleMapClick}
                  markers={mapMarkers}
                  transformedBoxes={[]}
                />
              </div>
            </div>

            <ReferencePointManager
              referencePoints={referencePoints}
              onPointDelete={handlePointDelete}
              onPointEdit={handlePointEdit}
            />

            <div className="step-actions">
              <button onClick={handleReset} className="btn-secondary">
                最初からやり直す
              </button>
              <button
                onClick={handleTransform}
                className="btn-primary"
                disabled={referencePoints.length < 3}
              >
                座標変換を実行
              </button>
            </div>
          </div>
        )}

        {/* Step 4 & 5: Transform and Generate KML */}
        {currentStep === 'result' && (
          <div className="step-content">
            <h2>ステップ 4: 変換結果とKML生成</h2>
            <div className="result-grid">
              <div className="result-section">
                <h3>変換結果プレビュー</h3>
                <MapComponent
                  onLocationSelect={() => { }}
                  markers={mapMarkers}
                  transformedBoxes={transformedBoxes}
                />
              </div>
              <div className="result-section">
                <ResultPreviewComponent
                  fileId={fileId}
                  transformedBoxes={transformedBoxes}
                  mapScale={mapScale}
                  warnings={warnings}
                  onGenerateKML={() => { }}
                />
              </div>
            </div>
            <div className="step-actions">
              <button onClick={handleReset} className="btn-primary">
                新しいファイルを処理
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
