import React, { useState, useRef } from 'react';
import type { DragEvent, ChangeEvent } from 'react';
import { uploadPDF } from '../services/api';
import type { UploadResponse } from '../types';
import './FileUploadComponent.css';

interface FileUploadComponentProps {
  onUploadSuccess: (fileId: string, imageUrl: string, width: number, height: number) => void;
  onUploadError: (error: string) => void;
}

const FileUploadComponent: React.FC<FileUploadComponentProps> = ({
  onUploadSuccess,
  onUploadError,
}) => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    // Check file type
    if (file.type !== 'application/pdf') {
      return 'PDFファイルを選択してください';
    }

    // Check file size (max 50MB)
    const maxSize = 50 * 1024 * 1024; // 50MB in bytes
    if (file.size > maxSize) {
      return 'ファイルサイズは50MB以下にしてください';
    }

    return null;
  };

  const handleFileUpload = async (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      onUploadError(validationError);
      return;
    }

    setUploading(true);
    setProgress(0);
    setSelectedFileName(file.name);

    try {
      // Simulate progress (since we don't have real progress from axios)
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response: UploadResponse = await uploadPDF(file);
      
      clearInterval(progressInterval);
      setProgress(100);

      // Call success callback
      setTimeout(() => {
        onUploadSuccess(response.file_id, response.image_url, response.width, response.height);
        setUploading(false);
        setProgress(0);
      }, 500);
    } catch (error) {
      setUploading(false);
      setProgress(0);
      setSelectedFileName(null);
      
      const errorMessage = error instanceof Error ? error.message : 'アップロードに失敗しました';
      onUploadError(errorMessage);
    }
  };

  const handleFileSelect = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleDragEnter = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);

    const file = event.dataTransfer.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleClick = () => {
    if (!uploading) {
      fileInputRef.current?.click();
    }
  };

  return (
    <div className="file-upload-component">
      <div
        className={`upload-area ${isDragging ? 'dragging' : ''} ${uploading ? 'uploading' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          disabled={uploading}
        />

        {!uploading ? (
          <div className="upload-prompt">
            <svg
              className="upload-icon"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <p className="upload-text">
              PDFファイルをドラッグ&ドロップ
              <br />
              または
              <br />
              <span className="upload-link">クリックして選択</span>
            </p>
            <p className="upload-hint">最大ファイルサイズ: 50MB</p>
          </div>
        ) : (
          <div className="upload-progress">
            <div className="spinner"></div>
            <p className="upload-status">アップロード中...</p>
            {selectedFileName && (
              <p className="file-name">{selectedFileName}</p>
            )}
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="progress-text">{progress}%</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUploadComponent;
