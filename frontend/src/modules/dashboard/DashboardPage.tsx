import React from 'react';
import { Users, Scroll, DollarSign, MapPin } from 'lucide-react';
import { StatCard } from './components/StatCard';
import { Card } from '../../components/common/Card';
import { GisMapViewer } from '../../components/map/GisMapViewer';

export const DashboardPage: React.FC = () => {
  const kigaliParishMarkers: Array<{
    id: string;
    position: [number, number];
    title: string;
    description: string;
  }> = [
    { id: '1', position: [-1.9536, 30.0606], title: 'Cathédrale Saint Michel', description: 'See Parish - Doyenné Saint Michel' },
    { id: '2', position: [-1.9441, 30.0619], title: 'Paroisse Sainte Famille', description: 'Historical Parish founded 1913' },
    { id: '3', position: [-1.9705, 30.1044], title: 'Paroisse Regina Pacis (Remera)', description: 'Doyenné Saint Michel' },
    { id: '4', position: [-1.9961, 30.0789], title: 'Paroisse Saint Joseph (Kicukiro)', description: 'Doyenné Kicukiro' },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-brand-700 via-brand-600 to-brand-500 rounded-2xl p-6 text-white shadow-md">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">Archidiocèse de Kigali &bull; Arkidi Platform</h1>
            <p className="text-brand-100 text-xs mt-1">
              Consolidated Parish Administration, Sacramental Registers & GIS Land Intelligence
            </p>
          </div>
          <div className="bg-white/10 backdrop-blur-md px-4 py-2 rounded-xl text-xs border border-white/20">
            Current Year: <span className="font-bold">2026</span> &bull; 34 Parishes
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Faithful"
          value="482,150"
          subtitle="Across 34 Parishes"
          icon={Users}
          trend="+4.2% YoY"
          color="brand"
        />
        <StatCard
          title="Baptisms Recorded"
          value="14,820"
          subtitle="Year to date"
          icon={Scroll}
          color="blue"
        />
        <StatCard
          title="Parish Land Parcels"
          value="218"
          subtitle="100% PostGIS Geocoded"
          icon={MapPin}
          color="emerald"
        />
        <StatCard
          title="Tithes & Offerings"
          value="184,250,000 RWF"
          subtitle="Consolidated Curia Total"
          icon={DollarSign}
          color="amber"
        />
      </div>

      {/* Main Grid: GIS Map & Recent Activities */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card
            title="Archdiocesan GIS Parish & Property Map"
            subtitle="Geospatial distribution of parishes and central chapels in Kigali"
          >
            <GisMapViewer markers={kigaliParishMarkers} height="380px" />
          </Card>
        </div>

        <div>
          <Card title="Quick Canonical Actions" subtitle="Frequently used secretary workflows">
            <div className="space-y-3">
              <a
                href="/sacraments"
                className="block p-3 rounded-lg border border-gray-100 hover:border-brand-200 hover:bg-brand-50 transition-colors"
              >
                <div className="text-xs font-semibold text-gray-900">Record New Baptism</div>
                <div className="text-[11px] text-gray-500 mt-0.5">Enter canonical register page and act number</div>
              </a>
              <a
                href="/faithful"
                className="block p-3 rounded-lg border border-gray-100 hover:border-brand-200 hover:bg-brand-50 transition-colors"
              >
                <div className="text-xs font-semibold text-gray-900">Register Parishioner / Family</div>
                <div className="text-[11px] text-gray-500 mt-0.5">Assign to Small Christian Community (Umuryango-remezo)</div>
              </a>
              <a
                href="/land-assets"
                className="block p-3 rounded-lg border border-gray-100 hover:border-brand-200 hover:bg-brand-50 transition-colors"
              >
                <div className="text-xs font-semibold text-gray-900">Cadastral UPI Parcel Registry</div>
                <div className="text-[11px] text-gray-500 mt-0.5">View title deeds and parcel polygons</div>
              </a>
              <a
                href="/statistics"
                className="block p-3 rounded-lg border border-gray-100 hover:border-brand-200 hover:bg-brand-50 transition-colors"
              >
                <div className="text-xs font-semibold text-gray-900">Annuario Pontificio Extracts</div>
                <div className="text-[11px] text-gray-500 mt-0.5">Generate Holy See statistical returns</div>
              </a>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
