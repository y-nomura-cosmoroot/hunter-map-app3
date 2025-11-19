import axios, { AxiosError } from 'axios';
import type { AxiosInstance } from 'axios';
import type {
  UploadResponse,
  DetectionResponse,
  TransformRequest,
  TransformResponse,
  KMLRequest,
  KMLResponse,
  ErrorResponse,
} from '../types';

// Create axios instance with base URL
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handler to extract Japanese error messages
const handleApiError = (error: unknown): never => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ErrorResponse>;
    
    if (axiosError.response?.data) {
      const errorData = axiosError.response.data;
      const message = errorData.message || 'エラーが発生しました';
      const suggestion = errorData.suggestion ? `\n推奨: ${errorData.suggestion}` : '';
      throw new Error(`${message}${suggestion}`);
    }
    
    if (axiosError.code === 'ECONNABORTED') {
      throw new Error('リクエストがタイムアウトしました。もう一度お試しください。');
    }
    
    if (axiosError.code === 'ERR_NETWORK') {
      throw new Error('ネットワークエラーが発生しました。接続を確認してください。');
    }
    
    throw new Error(`APIエラー: ${axiosError.message}`);
  }
  
  throw new Error('予期しないエラーが発生しました');
};

/**
 * Upload PDF file to the server
 * @param file - PDF file to upload
 * @returns Upload response with file_id and image_url
 */
export const uploadPDF = async (file: File): Promise<UploadResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post<UploadResponse>('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Detect red boxes in the uploaded image
 * @param fileId - File ID returned from upload
 * @returns Detection response with detected boxes
 */
export const detectBoxes = async (fileId: string): Promise<DetectionResponse> => {
  try {
    const response = await apiClient.post<DetectionResponse>('/api/detect-boxes', {
      file_id: fileId,
    });
    
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Transform image coordinates to geographic coordinates
 * @param request - Transform request with reference points and box IDs
 * @returns Transform response with transformed boxes and map scale
 */
export const transformCoordinates = async (
  request: TransformRequest
): Promise<TransformResponse> => {
  try {
    const response = await apiClient.post<TransformResponse>('/api/transform', request);
    
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Generate KML file from transformed boxes
 * @param request - KML request with file_id and transformed boxes
 * @returns KML response with download URL and filename
 */
export const generateKML = async (request: KMLRequest): Promise<KMLResponse> => {
  try {
    const response = await apiClient.post<KMLResponse>('/api/generate-kml', request);
    
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Download KML file
 * @param filename - Filename to download
 * @returns Blob of the KML file
 */
export const downloadKML = async (filename: string): Promise<Blob> => {
  try {
    const response = await apiClient.get(`/api/download/${filename}`, {
      responseType: 'blob',
    });
    
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

export default apiClient;
