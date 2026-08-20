import React from 'react';
import { useLanguage } from '../../core/hooks/useLanguage';
import { Globe } from 'lucide-react';

export const LanguageSwitcher: React.FC = () => {
  const { currentLanguage, changeLanguage } = useLanguage();

  const languages = [
    { code: 'en', label: 'English' },
    { code: 'fr', label: 'Français' },
    { code: 'rw', label: 'Ikinyarwanda' },
  ];

  return (
    <div className="flex items-center gap-1.5 bg-gray-100 p-1 rounded-lg">
      <Globe className="w-4 h-4 text-gray-500 ml-1.5" />
      <select
        value={currentLanguage}
        onChange={(e) => changeLanguage(e.target.value as 'en' | 'fr' | 'rw')}
        className="bg-transparent text-xs font-medium text-gray-700 focus:outline-none cursor-pointer pr-2 py-0.5"
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.label}
          </option>
        ))}
      </select>
    </div>
  );
};
