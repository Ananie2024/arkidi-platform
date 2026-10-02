import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { domainApi } from '../../core/api/domain';
import { BaptismRecord } from '../../core/types/sacrament.types';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  record: BaptismRecord | null;
}

const editableFields = ['act_number', 'registry_year', 'volume_number', 'page_number', 'celebration_date', 'minister_name', 'godfather_name', 'godmother_name'] as const;

export const AmendmentRequestModal: React.FC<Props> = ({ isOpen, onClose, record }) => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [field, setField] = useState<(typeof editableFields)[number]>('minister_name');
  const [newValue, setNewValue] = useState('');
  const [reason, setReason] = useState('');
  const [error, setError] = useState<string | null>(null);
  const mutation = useMutation({
    mutationFn: domainApi.requestAmendment,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['amendments'] });
      setReason('');
      setNewValue('');
      onClose();
    },
    onError: (failure: unknown) => setError(failure instanceof Error ? failure.message : t('sacraments.amendment_request_error', 'Unable to submit correction request')),
  });

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!record) return;
    setError(null);
    mutation.mutate({
      sacrament_type: 'BAPTISM',
      record_id: record.id,
      amendment_type: 'CLERICAL_ERROR',
      reason,
      field_changes: {
        [field]: {
          old: String(record[field] ?? ''),
          new: field === 'registry_year' ? Number(newValue) : newValue,
        },
      },
    });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t('sacraments.amendment_request_title', 'Request register correction')} maxWidth="lg">
      <form className="space-y-4" onSubmit={submit}>
        {error && <p role="alert" className="rounded border border-red-200 bg-red-50 p-2 text-sm text-red-700">{error}</p>}
        <label className="block text-sm font-medium text-gray-700">
          {t('sacraments.amendment_field', 'Register field')}
          <select value={field} onChange={(event) => setField(event.target.value as (typeof editableFields)[number])} className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
            {editableFields.map((name) => <option key={name} value={name}>{t(`sacraments.field_${name}`, name.replace(/_/g, ' '))}</option>)}
          </select>
        </label>
        <Input label={t('sacraments.amendment_old_value', 'Recorded value')} value={String(record?.[field] ?? '')} readOnly />
        <Input label={t('sacraments.amendment_new_value', 'Correct value')} value={newValue} onChange={(event) => setNewValue(event.target.value)} required />
        <label className="block text-sm font-medium text-gray-700">
          {t('sacraments.amendment_reason', 'Reason and supporting reference')}
          <textarea value={reason} onChange={(event) => setReason(event.target.value)} minLength={5} required rows={3} className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
        </label>
        <p className="text-xs text-gray-500">{t('sacraments.amendment_review_note', 'The request remains pending until reviewed by an authorized priest or chancellor.')}</p>
        <div className="flex justify-end gap-2 border-t border-gray-100 pt-4">
          <Button variant="outline" type="button" onClick={onClose}>{t('common.cancel')}</Button>
          <Button type="submit" disabled={mutation.isPending}>{mutation.isPending ? t('common.saving', 'Saving...') : t('sacraments.amendment_submit', 'Submit for review')}</Button>
        </div>
      </form>
    </Modal>
  );
};
