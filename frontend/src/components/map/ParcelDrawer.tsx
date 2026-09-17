import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Input } from '../common/Input';
import { Check, Upload, Sparkles, AlertCircle } from 'lucide-react';

interface ParcelDrawerProps {
  initialGeometry?: { type: string; coordinates: any } | null;
  onSave?: (geometry: { type: string; coordinates: any }) => void;
}

// Preset bounding polygons for Kigali parishes to allow quick testing & realistic demo
const KIGALI_PRESETS: Record<string, { name: string; geometry: { type: string; coordinates: number[][][] } }> = {
  sainte_famille: {
    name: 'Sainte Famille Compound (Nyarugenge)',
    geometry: {
      type: 'Polygon',
      coordinates: [
        [
          [30.0600, -1.9530],
          [30.0620, -1.9532],
          [30.0618, -1.9545],
          [30.0598, -1.9543],
          [30.0600, -1.9530],
        ],
      ],
    },
  },
  saint_michel: {
    name: 'Saint Michel Cathedral Compound (Kiyovu)',
    geometry: {
      type: 'Polygon',
      coordinates: [
        [
          [30.0640, -1.9500],
          [30.0665, -1.9502],
          [30.0662, -1.9520],
          [30.0638, -1.9518],
          [30.0640, -1.9500],
        ],
      ],
    },
  },
  regina_pacis: {
    name: 'Regina Pacis Remera Compound',
    geometry: {
      type: 'Polygon',
      coordinates: [
        [
          [30.1140, -1.9610],
          [30.1170, -1.9612],
          [30.1168, -1.9635],
          [30.1138, -1.9632],
          [30.1140, -1.9610],
        ],
      ],
    },
  },
};

export const ParcelDrawer: React.FC<ParcelDrawerProps> = ({ initialGeometry, onSave }) => {
  const { t } = useTranslation();
  const [geoJsonText, setGeoJsonText] = useState<string>(
    initialGeometry ? JSON.stringify(initialGeometry, null, 2) : ''
  );
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  const [vertexCount, setVertexCount] = useState<number>(
    initialGeometry?.coordinates?.[0]?.length || 0
  );

  const handleValidateAndSave = (rawText: string) => {
    setError(null);
    setSuccess(false);
    if (!rawText.trim()) {
      setError('Please provide GeoJSON polygon coordinates.');
      return;
    }
    try {
      const parsed = JSON.parse(rawText);
      if (parsed.type !== 'Polygon' && parsed.type !== 'MultiPolygon') {
        setError("GeoJSON geometry must be of type 'Polygon' or 'MultiPolygon'.");
        return;
      }
      if (!Array.isArray(parsed.coordinates) || parsed.coordinates.length === 0) {
        setError('GeoJSON geometry must include valid coordinates array.');
        return;
      }

      // Check closed ring for Polygon
      if (parsed.type === 'Polygon') {
        const outerRing = parsed.coordinates[0];
        if (!Array.isArray(outerRing) || outerRing.length < 4) {
          setError('A polygon ring must have at least 4 coordinate vertices.');
          return;
        }
        setVertexCount(outerRing.length);
      }

      setSuccess(true);
      onSave?.(parsed);
    } catch (err: any) {
      setError(`Invalid JSON syntax: ${err.message}`);
    }
  };

  const handleLoadPreset = (key: string) => {
    const preset = KIGALI_PRESETS[key];
    if (preset) {
      const text = JSON.stringify(preset.geometry, null, 2);
      setGeoJsonText(text);
      handleValidateAndSave(text);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      setGeoJsonText(content);
      handleValidateAndSave(content);
    };
    reader.readAsText(file);
  };

  return (
    <Card title={t('land_assets.drawer_title')} subtitle={t('land_assets.drawer_subtitle')}>
      <div className="space-y-4">
        {/* Presets and quick actions */}
        <div className="flex flex-wrap items-center justify-between gap-2 p-3 bg-gray-50 rounded-lg border border-gray-100">
          <div className="flex items-center gap-1.5 text-xs text-gray-700 font-medium">
            <Sparkles className="w-4 h-4 text-brand-600" />
            <span>Load Kigali Preset:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(KIGALI_PRESETS).map(([key, p]) => (
              <button
                key={key}
                type="button"
                onClick={() => handleLoadPreset(key)}
                className="text-xs px-2.5 py-1 bg-white border border-gray-300 hover:border-brand-500 rounded-md font-medium text-gray-700 hover:text-brand-600 transition"
              >
                {p.name.split(' ')[0]} {p.name.split(' ')[1]}
              </button>
            ))}
          </div>
        </div>

        {/* Textarea for GeoJSON Coordinates */}
        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-1">
            GeoJSON Geometry (Polygon / MultiPolygon)
          </label>
          <textarea
            rows={5}
            value={geoJsonText}
            onChange={(e) => {
              setGeoJsonText(e.target.value);
              setSuccess(false);
            }}
            placeholder={JSON.stringify(KIGALI_PRESETS.sainte_famille.geometry, null, 2)}
            className="w-full font-mono text-xs px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </div>

        {/* Error / Success indicator */}
        {error && (
          <div className="flex items-center gap-2 p-2.5 bg-red-50 border border-red-200 rounded text-xs text-red-700">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="flex items-center gap-2 p-2.5 bg-green-50 border border-green-200 rounded text-xs text-green-700">
            <Check className="w-4 h-4 shrink-0" />
            <span>Valid PostGIS boundary polygon ({vertexCount} vertices) attached.</span>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          <label className="cursor-pointer inline-flex items-center text-xs font-medium text-gray-600 hover:text-gray-900">
            <Upload className="w-3.5 h-3.5 mr-1" />
            <span>Upload .geojson file</span>
            <input
              type="file"
              accept=".json,.geojson"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>
          <Button
            type="button"
            size="sm"
            onClick={() => handleValidateAndSave(geoJsonText)}
          >
            Apply Boundary Polygon
          </Button>
        </div>
      </div>
    </Card>
  );
};

