import React from 'react';
import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard,
  MapPin,
  Users,
  Scroll,
  BookOpen,
  Calendar,
  DollarSign,
  HeartHandshake,
  Map,
  Archive,
  BarChart3,
} from 'lucide-react';
import { useUiStore } from '../../core/store/uiStore';

export const Sidebar: React.FC = () => {
  const { t } = useTranslation();
  const { sidebarOpen } = useUiStore();

  const navigationItems = [
    { to: '/dashboard', label: t('nav.dashboard'), icon: LayoutDashboard },
    { to: '/geography', label: t('nav.geography'), icon: MapPin },
    { to: '/faithful', label: t('nav.faithful'), icon: Users },
    { to: '/sacraments', label: t('nav.sacraments'), icon: Scroll },
    { to: '/clergy', label: t('nav.clergy'), icon: BookOpen },
    { to: '/liturgy', label: t('nav.liturgy'), icon: Calendar },
    { to: '/finance', label: t('nav.finance'), icon: DollarSign },
    { to: '/ministries', label: t('nav.ministries'), icon: HeartHandshake },
    { to: '/land-assets', label: t('nav.land_assets'), icon: Map },
    { to: '/archive', label: t('nav.archive'), icon: Archive },
    { to: '/statistics', label: t('nav.statistics'), icon: BarChart3 },
  ];

  if (!sidebarOpen) return null;

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col flex-shrink-0 min-h-[calc(100vh-4rem)]">
      {/* Brand Header */}
      <div className="p-4 border-b border-gray-100 flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-brand-500 flex items-center justify-center text-white font-bold text-lg shadow-sm">
          ☩
        </div>
        <div>
          <div className="font-bold text-gray-900 text-sm tracking-wide">ARKIDI</div>
          <div className="text-[10px] text-gray-400 font-medium uppercase tracking-wider">
            Archdiocese of Kigali
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-brand-50 text-brand-600 font-semibold border-r-4 border-brand-500'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-gray-100 text-[11px] text-gray-400 text-center">
        Arkidi Platform v1.0 &copy; 2026
      </div>
    </aside>
  );
};
