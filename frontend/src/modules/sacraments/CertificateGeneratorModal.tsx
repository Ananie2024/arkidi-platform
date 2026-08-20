import React, { useState } from 'react';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { QRCodeSVG } from 'qrcode.react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CertificateGeneratorModal: React.FC<ModalProps> = ({ isOpen, onClose }) => {
  const [generatedToken, setGeneratedToken] = useState<string | null>(null);

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    setGeneratedToken('CERT-BAP-2026-98124FA');
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Generate Canonical Sacramental Certificate" maxWidth="lg">
      {!generatedToken ? (
        <form className="space-y-4" onSubmit={handleGenerate}>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Sacrament Type</label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-brand-500">
              <option value="BAPTISM">Certificate of Baptism (Extrait d'acte de Baptême)</option>
              <option value="CONFIRMATION">Certificate of Confirmation</option>
              <option value="MATRIMONY">Certificate of Canonical Marriage</option>
            </select>
          </div>
          <Input label="Faithful Registration Number / Name" placeholder="PAR-STF-2026-001" required />
          <Input label="Reason for Issuance" placeholder="Marriage preparation, canonical suitability, etc." />
          <div className="flex justify-end gap-2 pt-4 border-t border-gray-100">
            <Button variant="outline" type="button" onClick={onClose}>Cancel</Button>
            <Button type="submit">Generate Certificate & QR Code</Button>
          </div>
        </form>
      ) : (
        <div className="text-center py-4 space-y-4">
          <div className="flex justify-center p-4 bg-gray-50 rounded-xl border border-gray-200">
            <QRCodeSVG value={`https://arkidi.archidiocesekigali.org/verify/${generatedToken}`} size={160} />
          </div>
          <div>
            <div className="text-xs text-gray-500 font-medium">Certificate Serial Number</div>
            <div className="text-base font-mono font-bold text-brand-600">{generatedToken}</div>
          </div>
          <p className="text-xs text-gray-500">
            QR verification code generated. You can now download or print the official PDF certificate.
          </p>
          <div className="flex justify-center gap-3 pt-2">
            <Button variant="outline" size="sm" onClick={() => setGeneratedToken(null)}>Issue Another</Button>
            <Button size="sm" onClick={onClose}>Download PDF Certificate</Button>
          </div>
        </div>
      )}
    </Modal>
  );
};
