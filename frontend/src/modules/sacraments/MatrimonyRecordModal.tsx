import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { domainApi } from '../../core/api/domain';

interface MatrimonyRecordModalProps {
  isOpen: boolean;
  onClose: () => void;
  parishId: string;
}

export const MatrimonyRecordModal: React.FC<MatrimonyRecordModalProps> = ({
  isOpen,
  onClose,
  parishId,
}) => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const currentYear = new Date().getFullYear();

  const [groomFaithfulId, setGroomFaithfulId] = useState('');
  const [brideFaithfulId, setBrideFaithfulId] = useState('');
  const [registryYear, setRegistryYear] = useState(currentYear);
  const [volumeNumber, setVolumeNumber] = useState('I');
  const [pageNumber, setPageNumber] = useState('1');
  const [actNumber, setActNumber] = useState('');
  const [celebrationDate, setCelebrationDate] = useState(new Date().toISOString().split('T')[0]);
  const [priestCelebrant, setPriestCelebrant] = useState('');
  const [witness1Name, setWitness1Name] = useState('');
  const [witness2Name, setWitness2Name] = useState('');
  const [dispensations, setDispensations] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => domainApi.createMatrimony(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matrimonies'] });
      onClose();
    },
    onError: (err: any) => {
      setErrorMsg(err?.response?.data?.message || err.message || 'Failed to record marriage');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    mutation.mutate({
      parish_id: parishId,
      groom_faithful_id: groomFaithfulId,
      bride_faithful_id: brideFaithfulId,
      registry_year: Number(registryYear),
      volume_number: volumeNumber,
      page_number: pageNumber,
      act_number: actNumber,
      celebration_date: celebrationDate,
      priest_celebrant: priestCelebrant,
      witness_1_name: witness1Name,
      witness_2_name: witness2Name,
      dispensations_or_canonical_notes: dispensations || null,
    });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t('sacraments.record_matrimony')} maxWidth="lg">
      <form className="space-y-4" onSubmit={handleSubmit}>
        {errorMsg && (
          <div className="p-2.5 bg-red-50 border border-red-200 rounded text-xs text-red-600">
            {errorMsg}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label={t('sacraments.col_groom_id', 'Groom Faithful ID (Umugabo)')}
            value={groomFaithfulId}
            onChange={(e) => setGroomFaithfulId(e.target.value)}
            placeholder="UUID of Groom"
            required
          />
          <Input
            label={t('sacraments.col_bride_id', 'Bride Faithful ID (Umugore)')}
            value={brideFaithfulId}
            onChange={(e) => setBrideFaithfulId(e.target.value)}
            placeholder="UUID of Bride"
            required
          />
        </div>

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
            placeholder="M-2026-001"
            required
          />
          <Input
            label={t('sacraments.col_marriage_date', 'Celebration Date')}
            type="date"
            value={celebrationDate}
            onChange={(e) => setCelebrationDate(e.target.value)}
            required
          />
        </div>

        <Input
          label={t('sacraments.col_celebrant_priest', 'Officiating Priest')}
          value={priestCelebrant}
          onChange={(e) => setPriestCelebrant(e.target.value)}
          placeholder="Abbé Jean Uwimana"
          required
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label={t('sacraments.col_witness_1', 'First Witness (Umuhamya wa 1)')}
            value={witness1Name}
            onChange={(e) => setWitness1Name(e.target.value)}
            placeholder="Witness full name"
            required
          />
          <Input
            label={t('sacraments.col_witness_2', 'Second Witness (Umuhamya wa 2)')}
            value={witness2Name}
            onChange={(e) => setWitness2Name(e.target.value)}
            placeholder="Witness full name"
            required
          />
        </div>

        <Input
          label={t('sacraments.col_dispensations', 'Dispensations / Canonical Impediments')}
          value={dispensations}
          onChange={(e) => setDispensations(e.target.value)}
          placeholder="Banns dispensation or canonical notes"
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
