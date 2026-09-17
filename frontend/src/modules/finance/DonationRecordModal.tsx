import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { domainApi, Donation } from '../../core/api/domain';

interface DonationRecordModalProps {
  isOpen: boolean;
  onClose: () => void;
  parishId: string;
  onDonationRecorded?: (donation: Donation) => void;
}

const DONATION_TYPES = [
  { value: 'TITHE', label: "Tithe / Dîme / Ituro ry'umuryango" },
  { value: 'OFFERTORY', label: 'Sunday Offertory / Amaturo asanzwe' },
  { value: 'CONSTRUCTION_FUND', label: 'Construction Fund / Umusanzu wo kubaka' },
  { value: 'CARITAS_POOR', label: 'Caritas & Poor Fund / Abakene' },
  { value: 'SPECIAL_COLLECTION', label: 'Special Collection / Ikoraniro ryihariye' },
  { value: 'MASS_STIPEND', label: 'Mass Stipend / Igitambo cya Misa' },
];

const PAYMENT_METHODS = [
  { value: 'CASH', label: 'Cash / Amafaranga mu ntoki' },
  { value: 'MOMO', label: 'Mobile Money (MTN / Airtel)' },
  { value: 'BANK_TRANSFER', label: 'Bank Transfer / Virement Bancaire' },
  { value: 'CHECK', label: 'Bank Cheque / Sheki' },
];

export const DonationRecordModal: React.FC<DonationRecordModalProps> = ({
  isOpen,
  onClose,
  parishId,
  onDonationRecorded,
}) => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [donationType, setDonationType] = useState('TITHE');
  const [paymentMethod, setPaymentMethod] = useState('MOMO');
  const [amount, setAmount] = useState('');
  const [donationDate, setDonationDate] = useState(
    new Date().toISOString().split('T')[0]
  );
  const [donorName, setDonorName] = useState('');
  const [referenceId, setReferenceId] = useState('');
  const [notes, setNotes] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => domainApi.createDonation(payload),
    onSuccess: (newDonation) => {
      queryClient.invalidateQueries({ queryKey: ['donations'] });
      queryClient.invalidateQueries({ queryKey: ['financial-summary'] });
      onClose();
      onDonationRecorded?.(newDonation);
    },
    onError: (err: any) => {
      setErrorMsg(err?.response?.data?.message || err.message || 'Failed to record contribution');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    const parsedAmount = parseFloat(amount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      setErrorMsg('Please enter a valid donation amount.');
      return;
    }

    mutation.mutate({
      parish_id: parishId,
      donation_type: donationType,
      payment_method: paymentMethod,
      amount: parsedAmount,
      currency: 'RWF',
      donation_date: donationDate,
      donor_name_override: donorName.trim() || null,
      reference_transaction_id: referenceId.trim() || null,
      notes: notes.trim() || null,
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={t('finance.record', 'Record Donation / Contribution')}
      maxWidth="lg"
    >
      <form className="space-y-4" onSubmit={handleSubmit}>
        {errorMsg && (
          <div className="p-2.5 bg-red-50 border border-red-200 rounded text-xs text-red-600">
            {errorMsg}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              {t('finance.col_type', 'Donation Type')}
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={donationType}
              onChange={(e) => setDonationType(e.target.value)}
              required
            >
              {DONATION_TYPES.map((d) => (
                <option key={d.value} value={d.value}>
                  {d.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              {t('finance.col_payment_method', 'Payment Method')}
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={paymentMethod}
              onChange={(e) => setPaymentMethod(e.target.value)}
              required
            >
              {PAYMENT_METHODS.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <Input
            label={`${t('finance.col_amount', 'Amount')} (RWF)`}
            type="number"
            min="1"
            step="100"
            placeholder="25000"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            required
          />
          <Input
            label={t('finance.col_date', 'Donation Date')}
            type="date"
            value={donationDate}
            onChange={(e) => setDonationDate(e.target.value)}
            required
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <Input
            label={t('finance.col_donor', 'Donor Name / Family Name')}
            placeholder="Mukamana Alice"
            value={donorName}
            onChange={(e) => setDonorName(e.target.value)}
          />
          <Input
            label="Transaction / Reference ID"
            placeholder="MoMo Txn # / Bank Slip Ref"
            value={referenceId}
            onChange={(e) => setReferenceId(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-1">
            Notes / Intentions
          </label>
          <textarea
            rows={2}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-brand-500"
            placeholder="Optional purpose, campaign or receipt notes..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </div>

        <div className="flex justify-end gap-2 pt-4 border-t border-gray-100">
          <Button variant="outline" type="button" onClick={onClose} disabled={mutation.isPending}>
            {t('common.cancel')}
          </Button>
          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? t('common.loading') : t('finance.record')}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
