import React from 'react';
import { useTranslation } from 'react-i18next';
import { Modal } from '../../components/common/Modal';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Donation } from '../../core/api/domain';
import { Printer, CheckCircle2, Building, ShieldCheck } from 'lucide-react';

interface DonationReceiptModalProps {
  isOpen: boolean;
  onClose: () => void;
  donation: Donation | null;
  parishName?: string;
}

const TYPE_NAMES: Record<string, string> = {
  TITHE: "Tithe / Dîme / Ituro ry'umuryango",
  OFFERTORY: 'Sunday Offertory / Amaturo asanzwe',
  CONSTRUCTION_FUND: 'Church Construction / Umusanzu wo kubaka',
  CARITAS_POOR: 'Caritas & Poor / Abakene',
  SPECIAL_COLLECTION: 'Special Collection / Ikoraniro ryihariye',
  MASS_STIPEND: 'Mass Stipend / Igitambo cya Misa',
};

export const DonationReceiptModal: React.FC<DonationReceiptModalProps> = ({
  isOpen,
  onClose,
  donation,
  parishName = 'Archdiocese of Kigali Parish',
}) => {
  const { t } = useTranslation();

  if (!donation) return null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Canonical Contribution Receipt"
      maxWidth="md"
    >
      <div className="space-y-6">
        {/* Printable Receipt Paper Card */}
        <div className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm relative overflow-hidden font-sans">
          {/* Header watermark/seal */}
          <div className="absolute top-2 right-2 opacity-5 pointer-events-none">
            <Building className="w-36 h-36 text-gray-900" />
          </div>

          {/* Official Letterhead */}
          <div className="text-center pb-4 border-b-2 border-gray-100">
            <p className="text-[10px] tracking-widest font-bold text-gray-500 uppercase">
              Archidiocèse de Kigali • Archdiocese of Kigali
            </p>
            <h2 className="text-sm font-bold text-brand-700 uppercase mt-0.5">
              {parishName}
            </h2>
            <p className="text-[11px] font-semibold text-gray-600 mt-1 uppercase tracking-wider">
              Official Contribution Receipt / Inyemezabwishyu
            </p>
          </div>

          {/* Receipt Meta (Number + Date) */}
          <div className="flex items-center justify-between py-3 border-b border-gray-100 text-xs">
            <div>
              <span className="text-gray-500 block text-[10px] uppercase font-semibold">Receipt Number</span>
              <span className="font-mono font-bold text-gray-900 text-sm">
                {donation.receipt_number}
              </span>
            </div>
            <div className="text-right">
              <span className="text-gray-500 block text-[10px] uppercase font-semibold">Date</span>
              <span className="font-semibold text-gray-900">
                {donation.donation_date}
              </span>
            </div>
          </div>

          {/* Main Amount Callout */}
          <div className="my-5 p-4 bg-gray-50 rounded-lg text-center border border-gray-200">
            <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold block">
              Amount Received
            </span>
            <div className="text-2xl sm:text-3xl font-black text-brand-800 mt-1">
              {donation.amount.toLocaleString()} <span className="text-lg font-bold">{donation.currency}</span>
            </div>
            <div className="mt-1 flex items-center justify-center gap-1 text-[11px] text-green-700 font-medium">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Payment Verified & Cleared</span>
            </div>
          </div>

          {/* Key-Value Details */}
          <div className="space-y-2.5 text-xs">
            <div className="flex justify-between py-1 border-b border-gray-50">
              <span className="text-gray-500">Contribution Type:</span>
              <span className="font-bold text-gray-900">
                {TYPE_NAMES[donation.donation_type] || donation.donation_type}
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-gray-50">
              <span className="text-gray-500">Received From (Donor):</span>
              <span className="font-bold text-gray-900">
                {donation.donor_name_override || 'Parishioner (Faithful)'}
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-gray-50">
              <span className="text-gray-500">Payment Method:</span>
              <Badge variant="neutral">{donation.payment_method}</Badge>
            </div>
            {donation.reference_transaction_id && (
              <div className="flex justify-between py-1 border-b border-gray-50">
                <span className="text-gray-500">Transaction Reference:</span>
                <span className="font-mono text-gray-800 text-[11px]">{donation.reference_transaction_id}</span>
              </div>
            )}
            {donation.notes && (
              <div className="pt-1">
                <span className="text-gray-500 block text-[11px]">Notes / Purpose:</span>
                <p className="text-gray-700 italic text-[11px] mt-0.5">{donation.notes}</p>
              </div>
            )}
          </div>

          {/* Official Signoff */}
          <div className="mt-8 pt-4 border-t border-dashed border-gray-300 flex items-center justify-between text-[10px] text-gray-500">
            <div className="flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-brand-600" />
              <span>Arkidi Canonical Registry Verification</span>
            </div>
            <div className="text-right">
              <p className="font-semibold text-gray-700">Parish Administration</p>
              <p className="italic">Authorized Electronic Signature</p>
            </div>
          </div>
        </div>

        {/* Modal Buttons */}
        <div className="flex items-center justify-between pt-2">
          <Button variant="outline" size="sm" onClick={onClose}>
            {t('common.cancel', 'Close')}
          </Button>
          <Button size="sm" onClick={handlePrint}>
            <Printer className="w-4 h-4 mr-1.5" />
            Print Official Receipt
          </Button>
        </div>
      </div>
    </Modal>
  );
};
