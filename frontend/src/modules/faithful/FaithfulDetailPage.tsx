import React from 'react';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { Scroll, Award, Heart } from 'lucide-react';

export const FaithfulDetailPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Jean-Baptiste Mugisha</h1>
          <p className="text-xs text-gray-500 mt-0.5">Registration Number: PAR-STF-2026-001</p>
        </div>
        <Badge variant="success">Canonical Marriage Registered</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card title="Civil & Contact Details">
          <div className="space-y-3 text-xs">
            <div><span className="font-semibold text-gray-700">Father's Name:</span> Emmanuel Habimana</div>
            <div><span className="font-semibold text-gray-700">Mother's Name:</span> Christine Mukamana</div>
            <div><span className="font-semibold text-gray-700">Date of Birth:</span> 12 April 1990</div>
            <div><span className="font-semibold text-gray-700">National ID:</span> 1199080012345678</div>
            <div><span className="font-semibold text-gray-700">Phone:</span> +250 788 123 456</div>
          </div>
        </Card>

        <Card title="Ecclesiastical & Parish Status">
          <div className="space-y-3 text-xs">
            <div><span className="font-semibold text-gray-700">Parish:</span> Sainte Famille</div>
            <div><span className="font-semibold text-gray-700">Centrale:</span> Centrale Saint Pierre</div>
            <div><span className="font-semibold text-gray-700">SCC (Umuryango-remezo):</span> Saint Joseph</div>
            <div><span className="font-semibold text-gray-700">Role in Family:</span> Head of Household</div>
          </div>
        </Card>

        <Card title="Canonical Sacraments Received">
          <div className="space-y-2 text-xs">
            <div className="flex items-center gap-2 p-2 bg-emerald-50 text-emerald-800 rounded">
              <Scroll className="w-4 h-4" />
              <span>Baptized &bull; Vol. 12, P. 45, Act 120 (1990)</span>
            </div>
            <div className="flex items-center gap-2 p-2 bg-blue-50 text-blue-800 rounded">
              <Award className="w-4 h-4" />
              <span>Confirmed &bull; Vol. 8, P. 10, Act 34 (2004)</span>
            </div>
            <div className="flex items-center gap-2 p-2 bg-purple-50 text-purple-800 rounded">
              <Heart className="w-4 h-4" />
              <span>Matrimony &bull; Vol. 15, P. 88, Act 5 (2020)</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
