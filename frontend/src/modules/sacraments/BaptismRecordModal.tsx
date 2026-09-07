import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { domainApi } from '../../core/api/domain';

interface BaptismRecordModalProps {
  isOpen: boolean;
  onClose: () => void;
  parishId: string;
}

export const BaptismRecordModal: React.FC<BaptismRecordModalProps> = ({
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
  const [ministerName, setMinisterName] = useState('');
  const [godfatherName, setGodfatherName] = useState('');
  const [godmotherName, setGodmotherName] = useState('');
  const [marginalNotes, setMarginalNotes] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => domainApi.createBaptism(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['baptisms'] });
      onClose();
    },
    onError: (err: any) => {
      setErrorMsg(err?.response?.data?.message || err.message || 'Failed to record baptism');
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
      minister_name: ministerName,
      godfather_name: godfatherName || null,
      godmother_name: godmotherName || null,
      marginal_notes: marginalNotes || null,
    });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t('sacraments.record_baptism')} maxWidth="lg">
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
            placeholder="B-2026-001"
            required
          />
          <Input
            label={t('sacraments.col_celebration_date', 'Celebration Date')}
            type="date"
            value={celebrationDate}
            onChange={(e) => setCelebrationDate(e.target.value)}
            required
          />
        </div>

        <Input
          label={t('sacraments.col_minister', 'Minister / Celebrant Priest')}
          value={ministerName}
          onChange={(e) => setMinisterName(e.target.value)}
          placeholder="Abbé Jean Uwimana"
          required
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label={t('sacraments.col_godfather', 'Godfather (Parrain)')}
            value={godfatherName}
            onChange={(e) => setGodfatherName(e.target.value)}
          />
          <Input
            label={t('sacraments.col_godmother', 'Godmother (Marraine)')}
            value={godmotherName}
            onChange={(e) => setGodmotherName(e.target.value)}
          />
        </div>

        <Input
          label={t('sacraments.col_marginal_notes', 'Marginal Notes (Adnotatio Marginalis)')}
          value={marginalNotes}
          onChange={(e) => setMarginalNotes(e.target.value)}
          placeholder="Subsequent confirmation or marriage reference"
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
