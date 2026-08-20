import React from 'react';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';

export const ClergyDetailPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Abbé Jean-Marie Vianney</h1>
          <p className="text-xs text-gray-500 mt-0.5">Diocesan Priest &bull; Curé de Paroisse (Sainte Famille)</p>
        </div>
        <Badge variant="success">Active Canonical Faculties</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Biographical & Ordination Data">
          <div className="space-y-3 text-xs">
            <div><span className="font-semibold text-gray-700">Date of Ordination:</span> 16 July 2005</div>
            <div><span className="font-semibold text-gray-700">Ordaining Bishop:</span> Mgr. Thaddée Ntihinyurwa</div>
            <div><span className="font-semibold text-gray-700">Congregation / Incardination:</span> Archidiocèse de Kigali</div>
            <div><span className="font-semibold text-gray-700">Phone:</span> +250 788 555 123</div>
          </div>
        </Card>

        <Card title="Canonical Decrees & Assignments History">
          <div className="space-y-2 text-xs">
            <div className="p-2.5 bg-gray-50 rounded border border-gray-100">
              <div className="font-semibold text-gray-800">Curé &bull; Paroisse Sainte Famille</div>
              <div className="text-gray-500">2021 &ndash; Present (Decree #DEC-2021-08)</div>
            </div>
            <div className="p-2.5 bg-gray-50 rounded border border-gray-100">
              <div className="font-semibold text-gray-800">Vicaire Paroissial &bull; Cathédrale Saint Michel</div>
              <div className="text-gray-500">2015 &ndash; 2021</div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
