import React from 'react';
import { Church, ChevronDown } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useActiveParish } from '../../core/hooks/useActiveParish';

export const ParishSelector: React.FC = () => {
  const { t } = useTranslation();
  const {
    parishes,
    activeParishId,
    activeParish,
    canChangeParish,
    changeActiveParish,
    isLoading,
  } = useActiveParish();

  if (isLoading || parishes.length === 0) {
    return null;
  }

  if (!canChangeParish && activeParish) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 border border-gray-200 rounded-lg text-xs text-gray-700 font-medium">
        <Church className="w-4 h-4 text-brand-600 flex-shrink-0" />
        <span className="truncate max-w-[160px] sm:max-w-[220px]">{activeParish.name}</span>
      </div>
    );
  }

  return (
    <div className="relative flex items-center">
      <div className="flex items-center gap-1.5 px-2.5 py-1.5 bg-brand-50 border border-brand-200 rounded-lg text-xs font-medium text-brand-900 hover:bg-brand-100/70 transition-colors cursor-pointer group">
        <Church className="w-4 h-4 text-brand-600 flex-shrink-0" />
        <select
          value={activeParishId || ''}
          onChange={(e) => changeActiveParish(e.target.value)}
          aria-label={t('layout.select_parish', 'Select Parish')}
          className="bg-transparent text-brand-900 text-xs font-semibold focus:outline-none cursor-pointer pr-4 appearance-none"
        >
          {parishes.map((parish) => (
            <option key={parish.id} value={parish.id} className="text-gray-900 bg-white">
              {parish.name} ({parish.code})
            </option>
          ))}
        </select>
        <ChevronDown className="w-3.5 h-3.5 text-brand-500 pointer-events-none absolute right-2" />
      </div>
    </div>
  );
};
