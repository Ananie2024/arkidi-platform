import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { domainApi } from '../../core/api/domain';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  parishId: string | null;
}

export const FaithfulCreateModal: React.FC<ModalProps> = ({ isOpen, onClose, parishId }) => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const mutation = useMutation({
    mutationFn: domainApi.createFaithful,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['faithful'] });
      onClose();
    },
    onError: (reason: unknown) => setError(reason instanceof Error ? reason.message : t('faithful.create_error', 'Unable to register parishioner')),
  });

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!parishId) {
      setError(t('faithful.select_parish', 'Choose an active parish before registering a parishioner.'));
      return;
    }
    setError(null);
    const values = new FormData(event.currentTarget);
    mutation.mutate({
      parish_id: parishId,
      registration_number: values.get('registration_number'),
      first_name: values.get('first_name'),
      last_name: values.get('last_name'),
      christian_name: values.get('christian_name'),
      gender: values.get('gender'),
      canonical_status: values.get('canonical_status'),
      national_id: values.get('national_id') || null,
      phone_number: values.get('phone_number') || null,
      date_of_birth: values.get('date_of_birth') || null,
    });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t('faithful.create_title')} maxWidth="lg">
      <form className="space-y-4" onSubmit={handleSubmit}>
        {error && <p role="alert" className="rounded border border-red-200 bg-red-50 p-2 text-sm text-red-700">{error}</p>}
        <Input name="registration_number" label={t('faithful.col_reg_number', 'Registration Number')} required />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Input name="last_name" label={t('faithful.create_last_name')} placeholder="Mugisha" required />
          <Input name="first_name" label={t('faithful.create_first_name')} placeholder="Jean-Baptiste" required />
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Input name="christian_name" label={t('faithful.create_christian_name')} required />
          <label className="block text-sm font-medium text-gray-700">
            {t('faithful.create_gender')}
            <select name="gender" className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" required defaultValue="MALE">
              <option value="MALE">{t('faithful.create_male')}</option>
              <option value="FEMALE">{t('faithful.create_female')}</option>
            </select>
          </label>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Input name="date_of_birth" label={t('faithful.date_of_birth', 'Date of birth')} type="date" />
          <Input name="national_id" label={t('faithful.create_national_id')} />
        </div>
        <label className="block text-sm font-medium text-gray-700">
          {t('faithful.col_canonical_status', 'Canonical status')}
          <select name="canonical_status" className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" required defaultValue="">
            <option value="" disabled>{t('faithful.select_status', 'Select status')}</option>
            <option value="CATECHUMEN">{t('faithful.status_catechumen', 'Catechumen')}</option>
            <option value="BAPTIZED">{t('faithful.status_baptized', 'Baptized')}</option>
            <option value="CONFIRMED">{t('faithful.status_confirmed', 'Confirmed')}</option>
            <option value="CANONICAL_MARRIAGE">{t('faithful.status_canonical_marriage', 'Canonical marriage')}</option>
            <option value="CIVIL_ONLY">{t('faithful.status_civil_only', 'Civil marriage only')}</option>
            <option value="CLERGY_OR_RELIGIOUS">{t('faithful.status_clergy', 'Clergy or religious')}</option>
            <option value="DECEASED">{t('faithful.status_deceased', 'Deceased')}</option>
          </select>
        </label>
        <Input name="phone_number" label={t('faithful.create_phone')} placeholder="+250 788 000 000" />
        <div className="flex justify-end gap-2 border-t border-gray-100 pt-4">
          <Button variant="outline" type="button" onClick={onClose}>{t('common.cancel')}</Button>
          <Button type="submit" disabled={mutation.isPending}>{mutation.isPending ? t('common.saving', 'Saving...') : t('faithful.create_save')}</Button>
        </div>
      </form>
    </Modal>
  );
};
