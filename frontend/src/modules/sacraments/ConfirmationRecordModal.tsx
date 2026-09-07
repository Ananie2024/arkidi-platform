import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { domainApi } from '../../core/api/domain';

interface ConfirmationRecordModalProps {
  isOpen: boolean;
  onClose: () => void;
  parishId: string;
}

export const ConfirmationRecordModal: React.FC<ConfirmationRecordModalProps> = ({
  isOpen,
  onClose,
  parishId,
}) => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const currentYear = new Date().getFullYear();

  const [faithfulId, setFaithfulId] = useState('');
  const [registryYear, setRegistryYear] = useState(currentYear);
  const [volumeNumber, setVolumeNumber] = useState('I');
  const [pageNumber, setPageNumber] = useState('1');
  const [actNumber, setActNumber] = useState('');
  const [celebrationDate, setCelebrationDate] = useState(new Date().toISOString().split('T')[0]);
  const [bishopOrVicar, setBishopOrVicar] = useState('');
  const [sponsorName, setSponsorName] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => domainApi.createConfirmation(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['confirmations'] });
      onClose();
    },
    onError: (err: any) => {
      setErrorMsg(err?.response?.data?.message || err.message || 'Failed to record confirmation');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    mutation.mutate({
      parish_id: parishId,
      faithful_id: faithfulId,
      registry_year: Number(registryYear),
      volume_number: volumeNumber,
      page_number: pageNumber,
      act_number: actNumber,
      celebration_date: celebrationDate,
      administering_bishop_or_vicar: bishopOrVicar,
      sponsor_name: sponsorName || null,
    });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t('sacraments.record_confirmation')} maxWidth="lg">
      <form className="space-y-4" onSubmit={handleSubmit}>
        {errorMsg && (
          <div className="p-2.5 bg-red-50 border border-red-200 rounded text-xs text-red-600">
            {errorMsg}
          </div>
        )}

        <Input
          label={t('sacraments.cert_faithful_label', 'Faithful ID / Parishioner ID')}
          value={faithfulId}
          onChange={(e) => setFaithfulId(e.target.value)}
          placeholder="UUID or Faithful ID"
          required
        />

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <Input
            label={t('sacraments.col_year', 'Registry Year')}
            type="number"
            value={registryYear}
            onChange={(e) => setRegistryYear(Number(e.target.value))}
            required
          />
          <Input
            label={t('sacraments.col_volume', 'Volume')}
            value={volumeNumber}
            onChange={(e) => setVolumeNumber(e.target.value)}
            required
          />
          <Input
            label={t('sacraments.col_page', 'Page #')}
            value={pageNumber}
            onChange={(e) => setPageNumber(e.target.value)}
            required
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label={t('sacraments.col_act', 'Act #')}
            value={actNumber}
            onChange={(e) => setActNumber(e.target.value)}
            placeholder="C-2026-001"
            required
          />
          <Input
            label={t('sacraments.col_date', 'Celebration Date')}
            type="date"
            value={celebrationDate}
            onChange={(e) => setCelebrationDate(e.target.value)}
            required
          />
        </div>

        <Input
          label={t('sacraments.col_bishop', 'Administering Bishop or Vicar')}
          value={bishopOrVicar}
          onChange={(e) => setBishopOrVicar(e.target.value)}
          placeholder="S.E. Mgr Antoine Kambanda"
          required
        />

        <Input
          label={t('sacraments.col_sponsor', 'Sponsor (Parrain / Marraine)')}
          value={sponsorName}
          onChange={(e) => setSponsorName(e.target.value)}
          placeholder="Jean Baptiste Karemera"
        />

        <div className="flex justify-end gap-2 pt-4 border-t border-gray-100">
          <Button variant="outline" type="button" onClick={onClose}>
            {t('common.cancel')}
          </Button>
          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? t('common.saving', 'Saving...') : t('common.save', 'Save Act')}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
