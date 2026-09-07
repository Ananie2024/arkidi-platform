import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Plus, Award } from 'lucide-react';
import { MatrimonyRecord, domainApi } from '../../core/api/domain';
import { useActiveParish } from '../../core/hooks/useActiveParish';
import { MatrimonyRecordModal } from './MatrimonyRecordModal';
import { CertificateGeneratorModal } from './CertificateGeneratorModal';

export const MatrimonyRegisterPage: React.FC = () => {
  const { t } = useTranslation();
  const { activeParishId } = useActiveParish();
  const [isRecordModalOpen, setIsRecordModalOpen] = useState(false);
  const [certModalProps, setCertModalProps] = useState<{ isOpen: boolean; faithfulId?: string }>({
    isOpen: false,
  });

  const matrimoniesQuery = useQuery({
    queryKey: ['matrimonies', activeParishId],
    queryFn: () => domainApi.listMatrimonies(activeParishId as string),
    enabled: Boolean(activeParishId),
  });

  const columns: Column<MatrimonyRecord>[] = [
    { header: t('sacraments.col_act'), accessor: 'act_number' },
    { header: t('sacraments.col_marriage_date'), accessor: 'celebration_date' },
    { header: t('sacraments.col_groom'), accessor: 'groom_faithful_id' },
    { header: t('sacraments.col_bride'), accessor: 'bride_faithful_id' },
    { header: t('sacraments.col_celebrant_priest'), accessor: 'priest_celebrant' },
    {
      header: t('common.actions', 'Actions'),
      accessor: (row) => (
        <Button
          variant="outline"
          size="sm"
          onClick={() => setCertModalProps({ isOpen: true, faithfulId: row.groom_faithful_id })}
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
          <h1 className="text-xl font-bold text-gray-900">{t('sacraments.matrimony_title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('sacraments.matrimony_subtitle')}</p>
        </div>
        <Button size="sm" onClick={() => setIsRecordModalOpen(true)}>
          <Plus className="w-4 h-4 mr-1.5" /> {t('sacraments.record_matrimony')}
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          data={matrimoniesQuery.data || []}
          isLoading={Boolean(activeParishId && matrimoniesQuery.isLoading && !matrimoniesQuery.data)}
          emptyMessage={t('sacraments.register_empty')}
        />
      </Card>

      {activeParishId && (
        <MatrimonyRecordModal
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
