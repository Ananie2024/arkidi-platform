import React from 'react';
import { Menu, Bell, User as UserIcon, LogOut } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../core/hooks/useAuth';
import { useUiStore } from '../../core/store/uiStore';
import { LanguageSwitcher } from '../common/LanguageSwitcher';
import { ParishSelector } from '../common/ParishSelector';

export const Header: React.FC = () => {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const { toggleSidebar } = useUiStore();

  return (
    <header className="relative h-16 bg-gradient-to-r from-brand-900 via-brand-800 to-brand-700 border-b-[3px] border-gold-500 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30 shadow-md shadow-brand-900/10">
      <div className="flex items-center gap-3">
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-lg text-white/80 hover:text-white hover:bg-white/10 focus:outline-none"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="hidden sm:block">
          <h1 className="text-sm font-semibold text-white">{t('layout.archdiocese')}</h1>
          <p className="text-xs text-blue-100">{t('layout.header_subtitle')}</p>
        </div>
      </div>

      <div className="flex items-center gap-3 sm:gap-4">
        <ParishSelector />
        <LanguageSwitcher />

        <button className="p-2 text-blue-100 hover:text-white rounded-lg hover:bg-white/10 relative transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-brand-500 rounded-full"></span>
        </button>

        <div className="flex items-center gap-3 pl-2 border-l border-white/20">
          <div className="w-8 h-8 rounded-full bg-white/10 border border-gold-300/70 flex items-center justify-center text-gold-100 font-semibold text-xs">
            {user?.full_name?.charAt(0) || user?.username?.charAt(0) || <UserIcon className="w-4 h-4" />}
          </div>
          <div className="hidden md:block text-left">
            <div className="text-xs font-semibold text-white">{user?.full_name || user?.username || t('layout.user')}</div>
            <div className="text-[10px] text-gold-200 font-medium">{user?.role || t('layout.guest')}</div>
          </div>
          <button
            onClick={logout}
            title={t('layout.sign_out')}
            className="p-1.5 text-blue-100 hover:text-white rounded-lg hover:bg-white/10 transition-colors ml-1"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
