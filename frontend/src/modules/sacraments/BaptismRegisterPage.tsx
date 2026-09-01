import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Plus } from 'lucide-react';
import { BaptismRecord } from '../../core/types/sacrament.types';

export const BaptismRegisterPage: React.FC = () => {
  const { t } = useTranslation();

  const columns: Column<BaptismRecord>[] = [
    { header: t('sacraments.col_act'), accessor: 'act_number' },
    { header: t('sacraments.col_book_vol'), accessor: (row) => `${row.volume_number}, ${row.page_number}` },
    { header: t('sacraments.col_celebration_date'), accessor: 'celebration_date' },
    { header: t('sacraments.col_minister'), accessor: 'minister_name' },
    { header: t('sacraments.col_godparent'), accessor: (row) => `${row.godfather_name || '-'} / ${row.godmother_name || '-'}` },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('sacraments.baptism_title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('sacraments.baptism_subtitle')}</p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> {t('sacraments.record_baptism')}
        </Button>
      </div>

      <Card>
        <Table columns={columns} data={[]} emptyMessage={t('sacraments.register_empty')} />
      </Card>
    </div>
  );
};
