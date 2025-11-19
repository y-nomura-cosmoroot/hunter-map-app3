import React, { useState } from 'react';
import type { ReferencePoint } from '../types';
import './ReferencePointManager.css';

interface ReferencePointManagerProps {
  referencePoints: ReferencePoint[];
  onPointDelete: (index: number) => void;
  onPointEdit: (index: number, point: ReferencePoint) => void;
}

const ReferencePointManager: React.FC<ReferencePointManagerProps> = ({
  referencePoints,
  onPointDelete,
  onPointEdit,
}) => {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editLat, setEditLat] = useState<string>('');
  const [editLng, setEditLng] = useState<string>('');
  const [editError, setEditError] = useState<string>('');
  const [highlightedIndex, setHighlightedIndex] = useState<number | null>(null);

  // Start editing a reference point
  const handleStartEdit = (index: number) => {
    const point = referencePoints[index];
    setEditingIndex(index);
    setEditLat(point.geoPoint.lat.toString());
    setEditLng(point.geoPoint.lng.toString());
    setEditError('');
  };

  // Cancel editing
  const handleCancelEdit = () => {
    setEditingIndex(null);
    setEditLat('');
    setEditLng('');
    setEditError('');
  };

  // Save edited reference point
  const handleSaveEdit = (index: number) => {
    const lat = parseFloat(editLat);
    const lng = parseFloat(editLng);

    // Validate latitude
    if (isNaN(lat) || lat < -90 || lat > 90) {
      setEditError('緯度は-90度から90度の範囲で入力してください');
      return;
    }

    // Validate longitude
    if (isNaN(lng) || lng < -180 || lng > 180) {
      setEditError('経度は-180度から180度の範囲で入力してください');
      return;
    }

    // Create updated reference point
    const updatedPoint: ReferencePoint = {
      ...referencePoints[index],
      geoPoint: { lat, lng },
    };

    onPointEdit(index, updatedPoint);
    handleCancelEdit();
  };

  // Handle delete with confirmation
  const handleDelete = (index: number) => {
    if (window.confirm(`基準点 P${index + 1} を削除しますか？`)) {
      onPointDelete(index);
    }
  };

  // Highlight newly added point
  React.useEffect(() => {
    if (referencePoints.length > 0) {
      const lastIndex = referencePoints.length - 1;
      setHighlightedIndex(lastIndex);
      const timer = setTimeout(() => {
        setHighlightedIndex(null);
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [referencePoints.length]);

  return (
    <div className="reference-point-manager">
      <div className="manager-header">
        <h3>基準点リスト</h3>
        <span className="point-count">
          {referencePoints.length} / 最低3つ必要
        </span>
      </div>

      {referencePoints.length < 3 && (
        <div className="warning-message">
          <span className="warning-icon">⚠️</span>
          <span>
            座標変換を実行するには、最低3つの基準点が必要です。
            現在: {referencePoints.length}個
          </span>
        </div>
      )}

      {referencePoints.length === 0 ? (
        <div className="empty-state">
          <p>基準点が設定されていません</p>
          <p className="empty-hint">
            PDF画像と地図をクリックして基準点を追加してください
          </p>
        </div>
      ) : (
        <div className="points-table">
          <table>
            <thead>
              <tr>
                <th>番号</th>
                <th>画像座標 (x, y)</th>
                <th>緯度</th>
                <th>経度</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {referencePoints.map((point, index) => (
                <tr 
                  key={point.id} 
                  className={`
                    ${editingIndex === index ? 'editing' : ''} 
                    ${highlightedIndex === index ? 'highlighted' : ''}
                  `.trim()}
                >
                  <td className="point-number">
                    <span className="point-label">P{index + 1}</span>
                  </td>
                  <td className="image-coords">
                    ({point.imagePoint.x.toFixed(1)}, {point.imagePoint.y.toFixed(1)})
                  </td>
                  <td className="geo-coord">
                    {editingIndex === index ? (
                      <input
                        type="number"
                        value={editLat}
                        onChange={(e) => setEditLat(e.target.value)}
                        step="0.000001"
                        min="-90"
                        max="90"
                        className="coord-input"
                        placeholder="緯度"
                      />
                    ) : (
                      <span>{point.geoPoint.lat.toFixed(6)}°</span>
                    )}
                  </td>
                  <td className="geo-coord">
                    {editingIndex === index ? (
                      <input
                        type="number"
                        value={editLng}
                        onChange={(e) => setEditLng(e.target.value)}
                        step="0.000001"
                        min="-180"
                        max="180"
                        className="coord-input"
                        placeholder="経度"
                      />
                    ) : (
                      <span>{point.geoPoint.lng.toFixed(6)}°</span>
                    )}
                  </td>
                  <td className="actions">
                    {editingIndex === index ? (
                      <div className="edit-actions">
                        <button
                          onClick={() => handleSaveEdit(index)}
                          className="btn-save"
                          title="保存"
                        >
                          ✓
                        </button>
                        <button
                          onClick={handleCancelEdit}
                          className="btn-cancel"
                          title="キャンセル"
                        >
                          ✕
                        </button>
                      </div>
                    ) : (
                      <div className="view-actions">
                        <button
                          onClick={() => handleStartEdit(index)}
                          className="btn-edit"
                          title="編集"
                        >
                          ✎
                        </button>
                        <button
                          onClick={() => handleDelete(index)}
                          className="btn-delete"
                          title="削除"
                        >
                          🗑
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {editError && (
            <div className="edit-error">
              <span className="error-icon">⚠️</span>
              <span>{editError}</span>
            </div>
          )}
        </div>
      )}

      <div className="manager-footer">
        <div className="instructions">
          <h4>基準点の設定方法:</h4>
          <ol>
            <li>PDF画像上の既知の位置をクリック</li>
            <li>地図上で対応する実際の位置をクリック</li>
            <li>この操作を3回以上繰り返す</li>
          </ol>
          <p className="tip">
            💡 ヒント: 基準点は画像全体に分散して配置すると、より正確な変換が可能です
          </p>
        </div>
      </div>
    </div>
  );
};

export default ReferencePointManager;
