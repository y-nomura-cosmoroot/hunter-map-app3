import React, { useState } from 'react';
import type { TransformedBox } from '../types';
import { generateKML } from '../services/api';
import './ResultPreviewComponent.css';

interface ResultPreviewComponentProps {
  fileId: string;
  transformedBoxes: TransformedBox[];
  mapScale: number;
  warnings: string[];
  onGenerateKML: () => void;
}

const ResultPreviewComponent: React.FC<ResultPreviewComponentProps> = ({
  fileId,
  transformedBoxes,
  mapScale,
  warnings,
  onGenerateKML,
}) => {
  const [generating, setGenerating] = useState<boolean>(false);
  const [downloadUrl, setDownloadUrl] = useState<string>('');
  const [filename, setFilename] = useState<string>('');
  const [error, setError] = useState<string>('');

  // Handle KML generation
  const handleGenerateKML = async () => {
    setGenerating(true);
    setError('');
    setDownloadUrl('');
    setFilename('');

    try {
      const response = await generateKML({
        file_id: fileId,
        boxes: transformedBoxes,
      });

      setDownloadUrl(response.download_url);
      setFilename(response.filename);
      onGenerateKML();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'KMLファイルの生成に失敗しました';
      setError(errorMessage);
    } finally {
      setGenerating(false);
    }
  };

  // Handle download
  const handleDownload = () => {
    if (downloadUrl) {
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <>
    <div className="result-preview">
      <div className="preview-header">
        <h3>変換結果</h3>
        <span className="box-count">
          {transformedBoxes.length} 個の赤枠
        </span>
      </div>

      {/* Warnings section */}
      {warnings.length > 0 && (
        <div className="warnings-section">
          <div className="warning-header">
            <span className="warning-icon">⚠️</span>
            <span className="warning-title">警告</span>
          </div>
          <ul className="warning-list">
            {warnings.map((warning, index) => (
              <li key={index}>{warning}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Map scale display */}
      <div className="map-scale-section">
        <div className="scale-label">推定地図縮尺:</div>
        <div className="scale-value">
          1:{mapScale.toLocaleString('ja-JP')}
        </div>
        <div className="scale-hint">
          ※ 基準点から自動計算された縮尺です
        </div>
      </div>

      {/* Transformed boxes list */}
      <div className="boxes-section">
        <h4>変換された赤枠の座標</h4>
        {transformedBoxes.length === 0 ? (
          <div className="empty-boxes">
            <p>変換された赤枠がありません</p>
          </div>
        ) : (
          <div className="boxes-list">
            {transformedBoxes.map((box, index) => (
              <div key={box.id} className="box-item">
                <div className="box-header">
                  <span className="box-label">赤枠 {index + 1}</span>
                  <span className="box-id">{box.id}</span>
                </div>
                <div className="box-coords">
                  <div className="coord-section">
                    <div className="coord-label">中心点:</div>
                    <div className="coord-value">
                      緯度: {box.center.lat.toFixed(6)}°, 
                      経度: {box.center.lng.toFixed(6)}°
                    </div>
                  </div>
                  <div className="coord-section">
                    <div className="coord-label">頂点の座標 ({box.corners.length}点):</div>
                    <div className="corners-grid">
                      {box.corners.map((corner, cornerIndex) => (
                        <div key={cornerIndex} className="corner-coord">
                          <span className="corner-label">P{cornerIndex + 1}:</span>
                          <span className="corner-value">
                            ({corner.lat.toFixed(6)}°, {corner.lng.toFixed(6)}°)
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>

      {/* KML generation section */}
      <div className="kml-section">
        <button
          onClick={handleGenerateKML}
          disabled={generating || transformedBoxes.length === 0}
          className="btn-generate-kml"
        >
          {generating ? (
            <>
              <span className="spinner"></span>
              <span>KMLファイルを生成中...</span>
            </>
          ) : (
            <>
              <span className="icon">📄</span>
              <span>KMLファイルを生成</span>
            </>
          )}
        </button>

        {error && (
          <div className="error-message">
            <span className="error-icon">❌</span>
            <span>{error}</span>
          </div>
        )}

        {downloadUrl && (
          <div className="download-section">
            <div className="success-message">
              <span className="success-icon">✅</span>
              <span>KMLファイルが生成されました！</span>
            </div>
            <button onClick={handleDownload} className="btn-download">
              <span className="icon">⬇️</span>
              <span>{filename} をダウンロード</span>
            </button>
            <div className="download-hint">
              ※ Google EarthやGISアプリケーションで開くことができます
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default ResultPreviewComponent;
