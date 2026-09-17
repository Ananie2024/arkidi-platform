import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polygon, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { LandParcel } from '../../core/types/land.types';

export const LAND_USE_COLORS: Record<string, string> = {
  CHURCH_COMPOUND: '#4f46e5', // indigo
  CENTRALE_CHAPEL: '#0284c7', // sky blue
  HEALTH_FACILITY: '#059669', // emerald
  EDUCATIONAL: '#d97706',     // amber
  AGRICULTURAL: '#65a30d',    // lime
  COMMERCIAL_RENTAL: '#7c3aed', // violet
  CONVENT_MONASTERY: '#db2777', // pink
  CEMETERY: '#475569',        // slate
  VACANT_RESERVE: '#9ca3af',   // gray
};

interface GisMapViewerProps {
  center?: [number, number];
  zoom?: number;
  markers?: Array<{
    id: string;
    position: [number, number];
    title: string;
    description?: string;
  }>;
  parcels?: LandParcel[];
  selectedParcelId?: string | null;
  onSelectParcel?: (parcel: LandParcel) => void;
  height?: string;
}

// Convert GeoJSON polygon coordinates [[lng, lat], ...] to Leaflet [[lat, lng], ...]
function parsePolygonCoordinates(geometry: any): [number, number][][] {
  if (!geometry || !geometry.coordinates) return [];
  try {
    if (geometry.type === 'Polygon') {
      return (geometry.coordinates as number[][][]).map((ring) =>
        ring.map(([lng, lat]) => [lat, lng] as [number, number])
      );
    }
    if (geometry.type === 'MultiPolygon') {
      const multi = geometry.coordinates as number[][][][];
      const allRings: [number, number][][] = [];
      for (const poly of multi) {
        for (const ring of poly) {
          allRings.push(ring.map(([lng, lat]) => [lat, lng] as [number, number]));
        }
      }
      return allRings;
    }
  } catch {
    return [];
  }
  return [];
}

export const GisMapViewer: React.FC<GisMapViewerProps> = ({
  center = [-1.9536, 30.0606], // Kigali Cathedral coordinates
  zoom = 13,
  markers = [],
  parcels = [],
  selectedParcelId,
  onSelectParcel,
  height = '450px',
}) => {
  return (
    <div style={{ height, width: '100%' }} className="rounded-xl overflow-hidden border border-gray-200 shadow-sm z-0 relative">
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

        {/* Render Point Markers */}
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

        {/* Render PostGIS Parcel Boundary Polygons */}
        {parcels.map((parcel) => {
          const positions = parsePolygonCoordinates(parcel.geojson_geometry);
          if (positions.length === 0) return null;

          const isSelected = parcel.id === selectedParcelId;
          const color = LAND_USE_COLORS[parcel.land_use] || '#3b82f6';

          return (
            <Polygon
              key={parcel.id}
              positions={positions}
              pathOptions={{
                color: isSelected ? '#dc2626' : color,
                weight: isSelected ? 3 : 2,
                fillColor: color,
                fillOpacity: isSelected ? 0.45 : 0.25,
              }}
              eventHandlers={{
                click: () => onSelectParcel?.(parcel),
              }}
            >
              <Tooltip sticky>
                <div className="text-xs">
                  <p className="font-bold">{parcel.parcel_name}</p>
                  <p className="text-gray-600">UPI: {parcel.upi}</p>
                  <p className="text-gray-500">{parcel.area_sqm.toLocaleString()} sqm</p>
                </div>
              </Tooltip>
              <Popup>
                <div className="text-xs space-y-1 p-1">
                  <p className="font-bold text-gray-900 text-sm">{parcel.parcel_name}</p>
                  <p className="text-gray-600 font-mono text-[11px]"><span className="font-semibold">UPI:</span> {parcel.upi}</p>
                  {parcel.title_deed_number && (
                    <p className="text-gray-600"><span className="font-semibold">Title Deed:</span> {parcel.title_deed_number}</p>
                  )}
                  <p className="text-gray-600"><span className="font-semibold">Land Use:</span> {parcel.land_use}</p>
                  <p className="text-gray-600"><span className="font-semibold">Tenure:</span> {parcel.tenure_status}</p>
                  <p className="text-gray-600"><span className="font-semibold">Area:</span> {parcel.area_sqm.toLocaleString()} m²</p>
                  {parcel.district && (
                    <p className="text-gray-500"><span className="font-semibold">Location:</span> {parcel.district} / {parcel.sector || ''}</p>
                  )}
                  {onSelectParcel && (
                    <button
                      type="button"
                      onClick={() => onSelectParcel(parcel)}
                      className="mt-2 text-[11px] text-blue-600 hover:text-blue-800 font-medium underline block"
                    >
                      View Parcel Dossier &rarr;
                    </button>
                  )}
                </div>
              </Popup>
            </Polygon>
          );
        })}
      </MapContainer>
    </div>
  );
};

