import React from 'react';
import { Menu, Bell, User as UserIcon, LogOut } from 'lucide-react';
import { useAuth } from '../../core/hooks/useAuth';
import { useUiStore } from '../../core/store/uiStore';
import { LanguageSwitcher } from '../common/LanguageSwitcher';

export const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const { toggleSidebar } = useUiStore();

  return (
    <header className="h-16 bg-white border-b border-gray-200 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 focus:outline-none"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="hidden sm:block">
          <h1 className="text-sm font-semibold text-gray-800">Archdiocese of Kigali</h1>
          <p className="text-xs text-gray-500">Parish Management & Digital Archive</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <LanguageSwitcher />

        <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-brand-500 rounded-full"></span>
        </button>

        <div className="flex items-center gap-3 pl-2 border-l border-gray-200">
          <div className="w-8 h-8 rounded-full bg-brand-50 border border-brand-200 flex items-center justify-center text-brand-500 font-semibold text-xs">
            {user?.full_name?.charAt(0) || user?.username?.charAt(0) || <UserIcon className="w-4 h-4" />}
          </div>
          <div className="hidden md:block text-left">
            <div className="text-xs font-semibold text-gray-900">{user?.full_name || user?.username || 'User'}</div>
            <div className="text-[10px] text-brand-500 font-medium">{user?.role || 'Guest'}</div>
          </div>
          <button
            onClick={logout}
            title="Sign out"
            className="p-1.5 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors ml-1"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
