import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card } from '../common/Card';
import { Button } from '../common/Button';

interface ParcelDrawerProps {
  onSave?: (geometry: GeoJSON.Geometry) => void;
}

export const ParcelDrawer: React.FC<ParcelDrawerProps> = () => {
  const { t } = useTranslation();
  return (
    <Card title={t('land_assets.drawer_title')} subtitle={t('land_assets.drawer_subtitle')}>
      <div className="bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
        <p className="text-sm text-gray-600 mb-2">
          {t('land_assets.drawer_body')}
        </p>
        <p className="text-xs text-gray-400 mb-4">
          {t('land_assets.drawer_inputs')}
        </p>
        <div className="flex justify-center gap-3">
          <Button variant="outline" size="sm">{t('land_assets.upload_geojson')}</Button>
          <Button variant="primary" size="sm">{t('land_assets.start_drawing')}</Button>
        </div>
      </div>
    </Card>
  );
};
