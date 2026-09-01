import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { QRCodeSVG } from 'qrcode.react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CertificateGeneratorModal: React.FC<ModalProps> = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const [generatedToken, setGeneratedToken] = useState<string | null>(null);

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    setGeneratedToken('CERT-BAP-2026-98124FA');
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t('sacraments.cert_title')} maxWidth="lg">
      {!generatedToken ? (
        <form className="space-y-4" onSubmit={handleGenerate}>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('sacraments.cert_sacrament_type')}</label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-brand-500">
              <option value="BAPTISM">{t('sacraments.cert_baptism_option')}</option>
              <option value="CONFIRMATION">{t('sacraments.cert_confirmation_option')}</option>
              <option value="MATRIMONY">{t('sacraments.cert_matrimony_option')}</option>
            </select>
          </div>
          <Input label={t('sacraments.cert_faithful_label')} placeholder="PAR-STF-2026-001" required />
          <Input label={t('sacraments.cert_reason_label')} placeholder="Marriage preparation, canonical suitability, etc." />
          <div className="flex justify-end gap-2 pt-4 border-t border-gray-100">
            <Button variant="outline" type="button" onClick={onClose}>{t('common.cancel')}</Button>
            <Button type="submit">{t('sacraments.cert_generate')}</Button>
          </div>
        </form>
      ) : (
        <div className="text-center py-4 space-y-4">
          <div className="flex justify-center p-4 bg-gray-50 rounded-xl border border-gray-200">
            <QRCodeSVG value={`https://arkidi.archidiocesekigali.org/verify/${generatedToken}`} size={160} />
          </div>
          <div>
            <div className="text-xs text-gray-500 font-medium">{t('sacraments.cert_serial')}</div>
            <div className="text-base font-mono font-bold text-brand-600">{generatedToken}</div>
          </div>
          <p className="text-xs text-gray-500">
            {t('sacraments.cert_success_body')}
          </p>
          <div className="flex justify-center gap-3 pt-2">
            <Button variant="outline" size="sm" onClick={() => setGeneratedToken(null)}>{t('sacraments.cert_issue_another')}</Button>
            <Button size="sm" onClick={onClose}>{t('sacraments.cert_download_pdf')}</Button>
          </div>
        </div>
      )}
    </Modal>
  );
};
