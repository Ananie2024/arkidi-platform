import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Plus } from 'lucide-react';

interface MatrimonyItem {
  id: string;
  act_number: string;
  celebration_date: string;
  groom_name: string;
  bride_name: string;
  priest_celebrant: string;
}

export const MatrimonyRegisterPage: React.FC = () => {
  const { t } = useTranslation();

  const columns: Column<MatrimonyItem>[] = [
    { header: t('sacraments.col_act'), accessor: 'act_number' },
    { header: t('sacraments.col_marriage_date'), accessor: 'celebration_date' },
    { header: t('sacraments.col_groom'), accessor: 'groom_name' },
    { header: t('sacraments.col_bride'), accessor: 'bride_name' },
    { header: t('sacraments.col_celebrant_priest'), accessor: 'priest_celebrant' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('sacraments.matrimony_title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('sacraments.matrimony_subtitle')}</p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> {t('sacraments.record_matrimony')}
        </Button>
      </div>

      <Card>
        <Table columns={columns} data={[]} emptyMessage={t('sacraments.register_empty')} />
      </Card>
    </div>
  );
};
