import React, { useRef, useEffect, useState, useCallback } from 'react';
import type { MouseEvent, WheelEvent } from 'react';
import type { Point, ReferencePoint, DetectedBox } from '../types';
import './PDFViewerComponent.css';

interface PDFViewerComponentProps {
  imageUrl: string;
  referencePoints: ReferencePoint[];
  onPointClick: (x: number, y: number) => void;
  detectedBoxes: DetectedBox[];
  selectedBoxes: string[];
  onBoxToggle: (boxId: string) => void;
  pendingImagePoint?: Point | null;
}

const PDFViewerComponent: React.FC<PDFViewerComponentProps> = ({
  imageUrl,
  referencePoints,
  onPointClick,
  detectedBoxes,
  selectedBoxes,
  onBoxToggle,
  pendingImagePoint = null,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  const [scale, setScale] = useState(1);
  const [panOffset, setPanOffset] = useState<Point>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState<Point>({ x: 0, y: 0 });
  const [imageLoaded, setImageLoaded] = useState(false);
  const [clickFeedback, setClickFeedback] = useState<Point | null>(null);

  // Load image
  useEffect(() => {
    const img = new Image();
    img.onload = () => {
      setImage(img);
      setImageLoaded(true);
      // Calculate scale to fit image in container with some padding
      if (containerRef.current) {
        const containerWidth = containerRef.current.clientWidth;
        const containerHeight = containerRef.current.clientHeight;

        // Calculate scale to fit width and height with 20px padding
        const padding = 40;
        const scaleX = (containerWidth - padding) / img.width;
        const scaleY = (containerHeight - padding) / img.height;

        // Use the smaller scale to ensure the entire image fits
        const fitScale = Math.min(scaleX, scaleY, 1); // Don't scale up beyond 100%

        setScale(fitScale);

        // Center the image with the new scale
        const scaledWidth = img.width * fitScale;
        const scaledHeight = img.height * fitScale;
        setPanOffset({
          x: (containerWidth - scaledWidth) / 2,
          y: (containerHeight - scaledHeight) / 2,
        });
      }
    };
    img.onerror = () => {
      console.error('Failed to load image');
      setImageLoaded(false);
    };
    img.src = imageUrl;
  }, [imageUrl]);

  // Draw on canvas
  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx || !image) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Save context state
    ctx.save();

    // Apply transformations
    ctx.translate(panOffset.x, panOffset.y);
    ctx.scale(scale, scale);

    // Draw image
    ctx.drawImage(image, 0, 0);

    // Draw detected boxes
    detectedBoxes.forEach((box) => {
      const isSelected = selectedBoxes.includes(box.id);

      ctx.beginPath();
      ctx.moveTo(box.corners[0].x, box.corners[0].y);
      for (let i = 1; i < box.corners.length; i++) {
        ctx.lineTo(box.corners[i].x, box.corners[i].y);
      }
      ctx.closePath();

      // Style based on selection
      if (isSelected) {
        ctx.strokeStyle = '#00ff00';
        ctx.lineWidth = 3 / scale;
        ctx.fillStyle = 'rgba(0, 255, 0, 0.1)';
        ctx.fill();
      } else {
        ctx.strokeStyle = '#ffff00';
        ctx.lineWidth = 2 / scale;
        ctx.fillStyle = 'rgba(255, 255, 0, 0.05)';
        ctx.fill();
      }
      ctx.stroke();

      // Draw box ID label
      ctx.fillStyle = isSelected ? '#00ff00' : '#ffff00';
      ctx.font = `${14 / scale}px Arial`;
      ctx.fillText(
        `Box ${box.id.substring(0, 8)}`,
        box.center.x,
        box.center.y
      );
    });

    // Draw reference point markers
    referencePoints.forEach((refPoint, index) => {
      const { x, y } = refPoint.imagePoint;

      // Draw marker circle
      ctx.beginPath();
      ctx.arc(x, y, 8 / scale, 0, 2 * Math.PI);
      ctx.fillStyle = '#ff0000';
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2 / scale;
      ctx.stroke();

      // Draw marker label
      ctx.fillStyle = '#ff0000';
      ctx.font = `bold ${16 / scale}px Arial`;
      ctx.fillText(`P${index + 1}`, x + 12 / scale, y + 5 / scale);
    });

    // Draw pending image point (waiting for map click)
    if (pendingImagePoint) {
      const { x, y } = pendingImagePoint;

      // Draw marker circle (same style as confirmed points)
      ctx.beginPath();
      ctx.arc(x, y, 8 / scale, 0, 2 * Math.PI);
      ctx.fillStyle = '#ff0000';
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2 / scale;
      ctx.stroke();

      // Draw marker label with "?" to indicate pending
      ctx.fillStyle = '#ff0000';
      ctx.font = `bold ${16 / scale}px Arial`;
      ctx.fillText(`P${referencePoints.length + 1}?`, x + 12 / scale, y + 5 / scale);
    }

    // Draw click feedback (temporary marker)
    if (clickFeedback) {
      const { x, y } = clickFeedback;

      // Draw pulsing circle
      ctx.beginPath();
      ctx.arc(x, y, 12 / scale, 0, 2 * Math.PI);
      ctx.fillStyle = 'rgba(255, 0, 0, 0.3)';
      ctx.fill();
      ctx.strokeStyle = '#ff0000';
      ctx.lineWidth = 3 / scale;
      ctx.stroke();

      // Draw inner circle
      ctx.beginPath();
      ctx.arc(x, y, 6 / scale, 0, 2 * Math.PI);
      ctx.fillStyle = '#ff0000';
      ctx.fill();
    }

    // Restore context state
    ctx.restore();
  }, [image, scale, panOffset, referencePoints, detectedBoxes, selectedBoxes, pendingImagePoint, clickFeedback]);

  // Redraw when dependencies change
  useEffect(() => {
    draw();
  }, [draw]);

  // Clear click feedback after animation
  useEffect(() => {
    if (clickFeedback) {
      const timer = setTimeout(() => {
        setClickFeedback(null);
      }, 800);
      return () => clearTimeout(timer);
    }
  }, [clickFeedback]);

  // Handle canvas resize
  useEffect(() => {
    const handleResize = () => {
      const canvas = canvasRef.current;
      const container = containerRef.current;
      if (canvas && container) {
        canvas.width = container.clientWidth;
        // Set fixed height instead of using container height
        canvas.height = 800; // Fixed height in pixels
        draw();
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [draw]);

  // Handle mouse wheel for zoom
  const handleWheel = (event: WheelEvent<HTMLCanvasElement>) => {
    event.preventDefault();

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    // Calculate zoom
    const zoomFactor = event.deltaY > 0 ? 0.9 : 1.1;
    const newScale = Math.max(0.1, Math.min(10, scale * zoomFactor));

    // Adjust pan offset to zoom towards mouse position
    const scaleChange = newScale / scale;
    const newPanX = mouseX - (mouseX - panOffset.x) * scaleChange;
    const newPanY = mouseY - (mouseY - panOffset.y) * scaleChange;

    setScale(newScale);
    setPanOffset({ x: newPanX, y: newPanY });
  };

  // Handle mouse down for panning
  const handleMouseDown = (event: MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    // Check if clicking on a detected box
    const clickedBox = getBoxAtPosition(mouseX, mouseY);
    if (clickedBox) {
      onBoxToggle(clickedBox.id);
      return;
    }

    // Start dragging for pan
    setIsDragging(true);
    setDragStart({ x: mouseX - panOffset.x, y: mouseY - panOffset.y });
  };

  // Handle mouse move for panning
  const handleMouseMove = (event: MouseEvent<HTMLCanvasElement>) => {
    if (!isDragging) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    setPanOffset({
      x: mouseX - dragStart.x,
      y: mouseY - dragStart.y,
    });
  };

  // Handle mouse up
  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Handle click for reference point placement
  const handleClick = (event: MouseEvent<HTMLCanvasElement>) => {
    if (isDragging) return;

    const canvas = canvasRef.current;
    if (!canvas || !image) return;

    const rect = canvas.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    // Convert screen coordinates to image coordinates
    const imageX = (mouseX - panOffset.x) / scale;
    const imageY = (mouseY - panOffset.y) / scale;

    // Check if click is within image bounds
    if (imageX >= 0 && imageX <= image.width && imageY >= 0 && imageY <= image.height) {
      // Check if clicking on a box (already handled in mouseDown)
      const clickedBox = getBoxAtPosition(mouseX, mouseY);
      if (!clickedBox) {
        // Show click feedback
        setClickFeedback({ x: imageX, y: imageY });
        onPointClick(imageX, imageY);
      }
    }
  };

  // Helper function to check if a point is inside a box
  const getBoxAtPosition = (screenX: number, screenY: number): DetectedBox | null => {
    if (!image) return null;

    const imageX = (screenX - panOffset.x) / scale;
    const imageY = (screenY - panOffset.y) / scale;

    for (const box of detectedBoxes) {
      if (isPointInPolygon({ x: imageX, y: imageY }, box.corners)) {
        return box;
      }
    }

    return null;
  };

  // Point in polygon test (ray casting algorithm)
  const isPointInPolygon = (point: Point, polygon: Point[]): boolean => {
    let inside = false;
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      const xi = polygon[i].x;
      const yi = polygon[i].y;
      const xj = polygon[j].x;
      const yj = polygon[j].y;

      const intersect =
        yi > point.y !== yj > point.y &&
        point.x < ((xj - xi) * (point.y - yi)) / (yj - yi) + xi;

      if (intersect) inside = !inside;
    }
    return inside;
  };

  // Handle zoom controls
  const handleZoomIn = () => {
    setScale((prev) => Math.min(10, prev * 1.2));
  };

  const handleZoomOut = () => {
    setScale((prev) => Math.max(0.1, prev / 1.2));
  };

  const handleResetView = () => {
    if (image && containerRef.current) {
      const containerWidth = containerRef.current.clientWidth;
      const containerHeight = containerRef.current.clientHeight;

      // Calculate scale to fit width and height with padding
      const padding = 40;
      const scaleX = (containerWidth - padding) / image.width;
      const scaleY = (containerHeight - padding) / image.height;

      // Use the smaller scale to ensure the entire image fits
      const fitScale = Math.min(scaleX, scaleY, 1);

      setScale(fitScale);

      // Center the image with the new scale
      const scaledWidth = image.width * fitScale;
      const scaledHeight = image.height * fitScale;
      setPanOffset({
        x: (containerWidth - scaledWidth) / 2,
        y: (containerHeight - scaledHeight) / 2,
      });
    }
  };

  return (
    <div className="pdf-viewer-component" ref={containerRef}>
      {!imageLoaded && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <p>画像を読み込み中...</p>
        </div>
      )}

      <canvas
        ref={canvasRef}
        className="pdf-canvas"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onClick={handleClick}
        style={{ 
          cursor: isDragging ? 'grabbing' : 'crosshair',
        }}
        title="クリックして基準点を設定"
      />

      <div className="viewer-controls">
        <button onClick={handleZoomIn} title="ズームイン">
          +
        </button>
        <button onClick={handleZoomOut} title="ズームアウト">
          −
        </button>
        <button onClick={handleResetView} title="リセット">
          ⟲
        </button>
        <span className="zoom-level">{Math.round(scale * 100)}%</span>
      </div>

      {detectedBoxes.length > 0 && (
        <div className="box-list">
          <h4>検出された赤枠</h4>
          <div className="box-items">
            {detectedBoxes.map((box) => (
              <label key={box.id} className="box-item">
                <input
                  type="checkbox"
                  checked={selectedBoxes.includes(box.id)}
                  onChange={() => onBoxToggle(box.id)}
                />
                <span>Box {box.id.substring(0, 8)}</span>
                <span className="box-type">
                  ({box.boxType === 'thick_border' ? '濃い枠' : '塗りつぶし'})
                </span>
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PDFViewerComponent;
