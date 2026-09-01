import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Plus } from 'lucide-react';

interface ConfirmationItem {
  id: string;
  act_number: string;
  volume_page: string;
  celebration_date: string;
  administering_bishop: string;
  sponsor_name: string;
}

export const ConfirmationRegisterPage: React.FC = () => {
  const { t } = useTranslation();

  const columns: Column<ConfirmationItem>[] = [
    { header: t('sacraments.col_act'), accessor: 'act_number' },
    { header: t('sacraments.col_registry_location'), accessor: 'volume_page' },
    { header: t('sacraments.col_date'), accessor: 'celebration_date' },
    { header: t('sacraments.col_bishop'), accessor: 'administering_bishop' },
    { header: t('sacraments.col_sponsor'), accessor: 'sponsor_name' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('sacraments.confirmation_title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('sacraments.confirmation_subtitle')}</p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> {t('sacraments.record_confirmation')}
        </Button>
      </div>

      <Card>
        <Table columns={columns} data={[]} emptyMessage={t('sacraments.register_empty')} />
      </Card>
    </div>
  );
};
