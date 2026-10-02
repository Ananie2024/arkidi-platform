import React, { useEffect, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Modal } from '../../components/common/Modal';
import { Button } from '../../components/common/Button';
import { domainApi } from '../../core/api/domain';
import { QRCodeSVG } from 'qrcode.react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  parishId?: string | null;
  faithfulId?: string;
  sourceRecordId?: string;
  sacramentType?: 'BAPTISM' | 'CONFIRMATION' | 'MATRIMONY';
}

export const CertificateGeneratorModal: React.FC<ModalProps> = ({ isOpen, onClose, parishId, faithfulId, sourceRecordId, sacramentType }) => {
  const { t } = useTranslation();
  const [type, setType] = useState<'BAPTISM' | 'CONFIRMATION' | 'MATRIMONY'>(sacramentType || 'BAPTISM');
  const [selectedFaithfulId, setSelectedFaithfulId] = useState(faithfulId || '');
  const [selectedRecordId, setSelectedRecordId] = useState(sourceRecordId || '');
  const [error, setError] = useState<string | null>(null);
  const peopleQuery = useQuery({
    queryKey: ['faithful', parishId, 'certificate-select'],
    queryFn: () => domainApi.listFaithful(undefined, parishId || undefined),
    enabled: isOpen && Boolean(parishId),
  });
  const baptismQuery = useQuery({
    queryKey: ['baptisms', parishId, 'certificate-select'],
    queryFn: () => domainApi.listBaptisms(parishId || undefined),
    enabled: isOpen && type === 'BAPTISM' && Boolean(parishId),
  });
  const confirmationQuery = useQuery({
    queryKey: ['confirmations', parishId, 'certificate-select'],
    queryFn: () => domainApi.listConfirmations(parishId || undefined),
    enabled: isOpen && type === 'CONFIRMATION' && Boolean(parishId),
  });
  const matrimonyQuery = useQuery({
    queryKey: ['matrimonies', parishId, 'certificate-select'],
    queryFn: () => domainApi.listMatrimonies(parishId || undefined),
    enabled: isOpen && type === 'MATRIMONY' && Boolean(parishId),
  });
  const availableRecords = type === 'BAPTISM'
    ? (baptismQuery.data || []).filter((record) => record.faithful_id === selectedFaithfulId).map((record) => ({ id: record.id, label: `${record.registry_year} · ${record.volume_number} / ${record.page_number} / ${record.act_number}` }))
    : type === 'CONFIRMATION'
      ? (confirmationQuery.data || []).filter((record) => record.faithful_id === selectedFaithfulId).map((record) => ({ id: record.id, label: `${record.registry_year} · ${record.volume_number} / ${record.page_number} / ${record.act_number}` }))
      : (matrimonyQuery.data || []).filter((record) => record.groom_faithful_id === selectedFaithfulId || record.bride_faithful_id === selectedFaithfulId).map((record) => ({ id: record.id, label: `${record.registry_year} · ${record.volume_number} / ${record.page_number} / ${record.act_number}` }));
  const issueMutation = useMutation({
    mutationFn: domainApi.issueCertificate,
    onError: (reason: unknown) => setError(reason instanceof Error ? reason.message : t('sacraments.certificate_issue_error', 'Unable to issue certificate')),
  });

  useEffect(() => {
    if (isOpen) {
      setType(sacramentType || 'BAPTISM');
      setSelectedFaithfulId(faithfulId || '');
      setSelectedRecordId(sourceRecordId || '');
    }
  }, [faithfulId, isOpen, sacramentType, sourceRecordId]);

  const handleClose = () => {
    issueMutation.reset();
    setError(null);
    onClose();
  };

  const handleGenerate = (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    if (!parishId || !selectedFaithfulId || !selectedRecordId) {
      setError(t('sacraments.select_faithful', 'Select a registered parishioner.'));
      return;
    }
    issueMutation.mutate({ sacrament_type: type, faithful_id: selectedFaithfulId, parish_id: parishId, source_record_id: selectedRecordId });
  };

  const generated = issueMutation.data;
  return (
    <Modal isOpen={isOpen} onClose={handleClose} title={t('sacraments.cert_title')} maxWidth="lg">
      {!generated ? (
        <form className="space-y-4" onSubmit={handleGenerate}>
          {error && <p role="alert" className="rounded border border-red-200 bg-red-50 p-2 text-sm text-red-700">{error}</p>}
          <label className="block text-sm font-medium text-gray-700">
            {t('sacraments.cert_sacrament_type')}
            <select value={type} onChange={(event) => { setType(event.target.value as typeof type); setSelectedRecordId(''); }} disabled={Boolean(sacramentType)} className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
              <option value="BAPTISM">{t('sacraments.cert_baptism_option')}</option>
              <option value="CONFIRMATION">{t('sacraments.cert_confirmation_option')}</option>
              <option value="MATRIMONY">{t('sacraments.cert_matrimony_option')}</option>
            </select>
          </label>
          <label className="block text-sm font-medium text-gray-700">
            {t('sacraments.cert_faithful_label')}
            <select value={selectedFaithfulId} onChange={(event) => { setSelectedFaithfulId(event.target.value); setSelectedRecordId(''); }} required disabled={Boolean(sourceRecordId) || peopleQuery.isLoading || peopleQuery.isError} className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
              <option value="">{t('sacraments.select_faithful', 'Select a registered parishioner')}</option>
              {(peopleQuery.data?.items || []).map((person) => (
                <option key={person.id} value={person.id}>
                  {t('sacraments.faithful_option_short', '{{registration}} · {{name}}', {
                    registration: person.registration_number,
                    name: `${person.last_name}, ${person.first_name}`,
                  })}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm font-medium text-gray-700">
            {t('sacraments.cert_source_record', 'Canonical register entry')}
            <select value={selectedRecordId} onChange={(event) => setSelectedRecordId(event.target.value)} required disabled={Boolean(sourceRecordId) || !selectedFaithfulId || availableRecords.length === 0} className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
              <option value="">{t('sacraments.cert_select_record', 'Select a register entry')}</option>
              {availableRecords.map((record) => <option key={record.id} value={record.id}>{record.label}</option>)}
            </select>
            {selectedFaithfulId && !availableRecords.length && <span className="mt-1 block text-xs text-amber-700">{t('sacraments.cert_no_matching_record', 'No register entry found for this person and sacrament.')}</span>}
          </label>
          {peopleQuery.isError && <p role="alert" className="text-sm text-red-700">{t('faithful.empty_error')}</p>}
          <div className="flex justify-end gap-2 border-t border-gray-100 pt-4">
            <Button variant="outline" type="button" onClick={handleClose}>{t('common.cancel')}</Button>
            <Button type="submit" disabled={issueMutation.isPending || !parishId || !selectedRecordId}>{issueMutation.isPending ? t('common.saving', 'Saving...') : t('sacraments.cert_generate')}</Button>
          </div>
        </form>
      ) : (
        <div className="space-y-4 py-4 text-center">
          <div className="flex justify-center rounded-xl border border-gray-200 bg-gray-50 p-4"><QRCodeSVG value={`${window.location.origin}/verify/${generated.verification_token}`} size={160} /></div>
          <div>
            <div className="text-xs font-medium text-gray-500">{t('sacraments.cert_serial')}</div>
            <div className="font-mono text-base font-bold text-brand-600">{generated.certificate_number}</div>
          </div>
          <p className="text-xs text-gray-500">{t('sacraments.cert_success_body')}</p>
          {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
          <div className="flex justify-center gap-3 pt-2">
            <Button variant="outline" size="sm" onClick={() => { issueMutation.reset(); setSelectedFaithfulId(faithfulId || ''); setSelectedRecordId(sourceRecordId || ''); }}>{t('sacraments.cert_issue_another')}</Button>
            <Button size="sm" onClick={() => domainApi.downloadCertificate(generated.id).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : t('sacraments.certificate_download_error', 'Unable to download PDF')))}>{t('sacraments.cert_download_pdf')}</Button>
            <Button variant="ghost" size="sm" onClick={handleClose}>{t('common.close', 'Close')}</Button>
          </div>
        </div>
      )}
    </Modal>
  );
};
