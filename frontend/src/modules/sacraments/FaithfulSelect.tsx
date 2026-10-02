import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { domainApi } from '../../core/api/domain';

interface Props {
  parishId: string;
  value: string;
  onChange: (id: string) => void;
  label: string;
  required?: boolean;
}

export const FaithfulSelect: React.FC<Props> = ({ parishId, value, onChange, label, required }) => {
  const { t } = useTranslation();
  const peopleQuery = useQuery({
    queryKey: ['faithful', parishId, 'sacrament-select'],
    queryFn: () => domainApi.listFaithful(undefined, parishId),
    enabled: Boolean(parishId),
  });

  return (
    <label className="block text-sm font-medium text-gray-700">
      {label}
      <select
        className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        required={required}
        disabled={peopleQuery.isLoading || peopleQuery.isError}
      >
        <option value="">{peopleQuery.isLoading ? t('common.loading', 'Loading...') : t('sacraments.select_faithful', 'Select a registered parishioner')}</option>
        {(peopleQuery.data?.items || []).map((person) => (
          <option key={person.id} value={person.id}>
            {t('sacraments.faithful_option', '{{registration}} · {{name}} ({{christian}})', {
              registration: person.registration_number,
              name: `${person.last_name}, ${person.first_name}`,
              christian: person.christian_name,
            })}
          </option>
        ))}
      </select>
      {peopleQuery.isError && <span role="alert" className="mt-1 block text-xs text-red-600">{t('faithful.empty_error')}</span>}
    </label>
  );
};
