import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

interface GisMapViewerProps {
  center?: [number, number];
  zoom?: number;
  markers?: Array<{
    id: string;
    position: [number, number];
    title: string;
    description?: string;
  }>;
  height?: string;
}

export const GisMapViewer: React.FC<GisMapViewerProps> = ({
  center = [-1.9536, 30.0606], // Kigali coordinates
  zoom = 12,
  markers = [],
  height = '450px',
}) => {
  return (
    <div style={{ height, width: '100%' }} className="rounded-xl overflow-hidden border border-gray-200 shadow-sm z-0">
      <MapContainer
        center={center}
        zoom={zoom}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {markers.map((m) => (
          <Marker key={m.id} position={m.position}>
            <Popup>
              <div className="text-xs">
                <p className="font-semibold text-gray-900">{m.title}</p>
                {m.description && <p className="text-gray-600 mt-1">{m.description}</p>}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};
