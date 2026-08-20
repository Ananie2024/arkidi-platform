import React from 'react';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';

export const ParishDetailPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Paroisse Sainte Famille</h1>
          <p className="text-xs text-gray-500 mt-1">Code: PAR-STF &bull; Doyenné Sainte Famille</p>
        </div>
        <Badge variant="success">Active Parish</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card title="Parish Information">
          <div className="space-y-3 text-xs">
            <div><span className="font-semibold text-gray-700">Patron Saint:</span> Sainte Famille (Jésus, Marie, Joseph)</div>
            <div><span className="font-semibold text-gray-700">Erection Year:</span> 1913</div>
            <div><span className="font-semibold text-gray-700">Curé de Paroisse:</span> Abbé Curé</div>
            <div><span className="font-semibold text-gray-700">District / Sector:</span> Nyarugenge / Muhima</div>
          </div>
        </Card>

        <Card title="Centrales & Communities">
          <div className="space-y-2 text-xs">
            <div className="p-2 bg-gray-50 rounded">Centrale Saint Pierre (4 SCCs)</div>
            <div className="p-2 bg-gray-50 rounded">Centrale Sainte Anne (6 SCCs)</div>
            <div className="p-2 bg-gray-50 rounded">Centrale Saint Jean (5 SCCs)</div>
          </div>
        </Card>

        <Card title="Parish Land & Real Estate">
          <div className="space-y-2 text-xs">
            <div><span className="font-semibold">Main Compound UPI:</span> 1/01/03/04/120</div>
            <div><span className="font-semibold">Area:</span> 18,450 sqm</div>
            <div><span className="font-semibold">Title Deed:</span> Freehold Title Registered</div>
          </div>
        </Card>
      </div>
    </div>
  );
};
