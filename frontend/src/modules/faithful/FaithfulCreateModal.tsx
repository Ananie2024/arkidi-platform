import React from 'react';
import { useTranslation } from 'react-i18next';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const FaithfulCreateModal: React.FC<ModalProps> = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t('faithful.create_title')} maxWidth="lg">
      <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); onClose(); }}>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input label={t('faithful.create_last_name')} placeholder="Mugisha" required />
          <Input label={t('faithful.create_first_name')} placeholder="Jean-Baptiste" required />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input label={t('faithful.create_christian_name')} placeholder="Jean-Baptiste" required />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('faithful.create_gender')}</label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm text-sm focus:outline-none focus:ring-brand-500">
              <option value="MALE">{t('faithful.create_male')}</option>
              <option value="FEMALE">{t('faithful.create_female')}</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input label={t('faithful.create_national_id')} placeholder="11990800..." />
          <Input label={t('faithful.create_phone')} placeholder="+250 788 000 000" />
        </div>
        <div className="flex justify-end gap-2 pt-4 border-t border-gray-100">
          <Button variant="outline" type="button" onClick={onClose}>{t('common.cancel')}</Button>
          <Button type="submit">{t('faithful.create_save')}</Button>
        </div>
      </form>
    </Modal>
  );
};
