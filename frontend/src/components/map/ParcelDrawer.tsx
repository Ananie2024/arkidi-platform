import React from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';

interface ParcelDrawerProps {
  onSave?: (geometry: GeoJSON.Geometry) => void;
}

export const ParcelDrawer: React.FC<ParcelDrawerProps> = () => {
  return (
    <Card title="GIS Boundary Polygon Editor" subtitle="Draw or upload GeoJSON parcel boundary">
      <div className="bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
        <p className="text-sm text-gray-600 mb-2">
          PostGIS Polygon CAD/GIS boundary editor integration
        </p>
        <p className="text-xs text-gray-400 mb-4">
          Supported inputs: GeoJSON, Shapefile (.shp), KML coordinates (EPSG:4326)
        </p>
        <div className="flex justify-center gap-3">
          <Button variant="outline" size="sm">Upload GeoJSON</Button>
          <Button variant="primary" size="sm">Start Drawing Boundary</Button>
        </div>
      </div>
    </Card>
  );
};
