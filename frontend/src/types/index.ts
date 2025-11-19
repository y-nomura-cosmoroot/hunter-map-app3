// Type definitions for the PDF Red Box KML Converter application

export interface Point {
  x: number;
  y: number;
}

export interface GeoPoint {
  lat: number;
  lng: number;
}

export interface ReferencePoint {
  imagePoint: Point;
  geoPoint: GeoPoint;
  id: string;
}

export interface DetectedBox {
  id: string;
  corners: Point[];
  center: Point;
  boxType: 'thick_border' | 'filled_area';
}

export interface TransformedBox {
  id: string;
  corners: GeoPoint[];
  center: GeoPoint;
}

export interface MapMarker {
  position: GeoPoint;
  label: string;
}

// API Response types
export interface UploadResponse {
  file_id: string;
  image_url: string;
  width: number;
  height: number;
}

export interface DetectionResponse {
  boxes: DetectedBox[];
  count: number;
}

export interface TransformRequest {
  file_id: string;
  reference_points: ReferencePoint[];
  boxes: string[];
}

export interface TransformResponse {
  transformed_boxes: TransformedBox[];
  map_scale: number;
  warnings: string[];
}

export interface KMLRequest {
  file_id: string;
  boxes: TransformedBox[];
}

export interface KMLResponse {
  download_url: string;
  filename: string;
}

export interface ErrorResponse {
  error: string;
  message: string;
  details: string;
  suggestion: string;
}
