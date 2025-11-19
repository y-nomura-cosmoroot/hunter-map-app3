import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polygon, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import type { MapMarker, GeoPoint, TransformedBox } from '../types';
import 'leaflet/dist/leaflet.css';
import './MapComponent.css';

// Fix for default marker icons in react-leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

interface MapComponentProps {
  onLocationSelect: (lat: number, lng: number) => void;
  markers: MapMarker[];
  transformedBoxes?: TransformedBox[];
}

// Component to handle map click events
const MapClickHandler: React.FC<{ onLocationSelect: (lat: number, lng: number) => void }> = ({ onLocationSelect }) => {
  useMapEvents({
    click: (e) => {
      const { lat, lng } = e.latlng;
      onLocationSelect(lat, lng);
    },
  });
  return null;
};

const MapComponent: React.FC<MapComponentProps> = ({ onLocationSelect, markers, transformedBoxes = [] }) => {
  // Default center position (Tokyo, Japan)
  const defaultCenter: GeoPoint = { lat: 35.6762, lng: 139.6503 };
  const defaultZoom = 10;

  return (
    <div className="map-component">
      <MapContainer
        center={[defaultCenter.lat, defaultCenter.lng]}
        zoom={defaultZoom}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapClickHandler onLocationSelect={onLocationSelect} />
        
        {markers.map((marker, index) => (
          <Marker
            key={`marker-${index}`}
            position={[marker.position.lat, marker.position.lng]}
          >
            <Popup>
              <div className="marker-popup">
                <strong>{marker.label}</strong>
                <div className="marker-coordinates">
                  緯度: {marker.position.lat.toFixed(6)}°<br />
                  経度: {marker.position.lng.toFixed(6)}°
                </div>
              </div>
            </Popup>
          </Marker>
        ))}

        {transformedBoxes.map((box, index) => (
          <Polygon
            key={`box-${box.id}`}
            positions={box.corners.map(corner => [corner.lat, corner.lng])}
            pathOptions={{
              color: 'red',
              fillColor: 'red',
              fillOpacity: 0.2,
              weight: 2
            }}
          >
            <Popup>
              <div className="box-popup">
                <strong>赤枠 {index + 1}</strong>
                <div className="box-info">
                  ID: {box.id.substring(0, 8)}<br />
                  中心: {box.center.lat.toFixed(6)}°, {box.center.lng.toFixed(6)}°<br />
                  頂点数: {box.corners.length}
                </div>
              </div>
            </Popup>
          </Polygon>
        ))}
      </MapContainer>
    </div>
  );
};

export default MapComponent;
