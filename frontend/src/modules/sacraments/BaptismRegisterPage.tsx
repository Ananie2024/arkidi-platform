import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Plus, Award } from 'lucide-react';
import { BaptismRecord } from '../../core/types/sacrament.types';
import { domainApi } from '../../core/api/domain';
import { useActiveParish } from '../../core/hooks/useActiveParish';
import { BaptismRecordModal } from './BaptismRecordModal';
import { CertificateGeneratorModal } from './CertificateGeneratorModal';

export const BaptismRegisterPage: React.FC = () => {
  const { t } = useTranslation();
  const { activeParishId } = useActiveParish();
  const [isRecordModalOpen, setIsRecordModalOpen] = useState(false);
  const [certModalProps, setCertModalProps] = useState<{ isOpen: boolean; faithfulId?: string }>({
    isOpen: false,
  });

  const baptismsQuery = useQuery({
    queryKey: ['baptisms', activeParishId],
    queryFn: () => domainApi.listBaptisms(activeParishId as string),
    enabled: Boolean(activeParishId),
  });

  const columns: Column<BaptismRecord>[] = [
    { header: t('sacraments.col_act'), accessor: 'act_number' },
    { header: t('sacraments.col_book_vol'), accessor: (row) => `${row.volume_number}, ${row.page_number}` },
    { header: t('sacraments.col_celebration_date'), accessor: 'celebration_date' },
    { header: t('sacraments.col_minister'), accessor: 'minister_name' },
    { header: t('sacraments.col_godparent'), accessor: (row) => `${row.godfather_name || '-'} / ${row.godmother_name || '-'}` },
    {
      header: t('common.actions', 'Actions'),
      accessor: (row) => (
        <Button
          variant="outline"
          size="sm"
          onClick={() => setCertModalProps({ isOpen: true, faithfulId: row.faithful_id })}
          title={t('sacraments.cert_generate', 'Generate Certificate')}
          className="text-xs py-1 px-2 h-7"
        >
          <Award className="w-3.5 h-3.5 mr-1 text-brand-600" />
          {t('sacraments.tab_certificates', 'Certificate')}
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('sacraments.baptism_title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('sacraments.baptism_subtitle')}</p>
        </div>
        <Button size="sm" onClick={() => setIsRecordModalOpen(true)}>
          <Plus className="w-4 h-4 mr-1.5" /> {t('sacraments.record_baptism')}
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          data={baptismsQuery.data || []}
          isLoading={Boolean(activeParishId && baptismsQuery.isLoading && !baptismsQuery.data)}
          emptyMessage={t('sacraments.register_empty')}
        />
      </Card>

      {activeParishId && (
        <BaptismRecordModal
          isOpen={isRecordModalOpen}
          onClose={() => setIsRecordModalOpen(false)}
          parishId={activeParishId}
        />
      )}

      <CertificateGeneratorModal
        isOpen={certModalProps.isOpen}
        onClose={() => setCertModalProps({ isOpen: false })}
      />
    </div>
  );
};
