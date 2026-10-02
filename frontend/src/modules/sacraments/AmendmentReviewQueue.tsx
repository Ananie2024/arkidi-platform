import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { useAuthContext } from '../../core/auth/AuthContext';
import { domainApi } from '../../core/api/domain';
import { Button } from '../../components/common/Button';

export const AmendmentReviewQueue: React.FC = () => {
  const { t } = useTranslation();
  const { hasRole } = useAuthContext();
  const queryClient = useQueryClient();
  const [reviewNotes, setReviewNotes] = useState<Record<string, string>>({});
  const canReview = hasRole(['PARISH_PRIEST', 'CHANCELLOR']);
  const queue = useQuery({
    queryKey: ['amendments', 'PENDING'],
    queryFn: () => domainApi.listAmendments('PENDING'),
    enabled: canReview,
  });
  const review = useMutation({
    mutationFn: ({ id, action }: { id: string; action: 'APPROVE' | 'REJECT' }) =>
      domainApi.reviewAmendment(id, action, reviewNotes[id] || ''),
    onSuccess: async () => {
      setReviewNotes({});
      await queryClient.invalidateQueries({ queryKey: ['amendments'] });
      await queryClient.invalidateQueries({ queryKey: ['baptisms'] });
    },
  });

  if (!canReview || queue.isError || (queue.data?.length ?? 0) === 0) return null;

  return (
    <section className="space-y-3 rounded-xl border border-amber-200 bg-amber-50 p-4">
      <div>
        <h2 className="font-semibold text-gray-900">{t('sacraments.amendment_queue_title', 'Canonical corrections awaiting review')}</h2>
        <p className="text-xs text-gray-600">{t('sacraments.amendment_queue_help', 'Review each request against its supporting record before deciding.')}</p>
      </div>
      {(queue.data || []).map((item) => (
        <article key={item.id} className="rounded-lg border border-gray-200 bg-white p-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <p className="text-sm font-medium text-gray-900">{item.reason}</p>
              <p className="mt-1 text-xs text-gray-500">{t('sacraments.amendment_record_line', '{{type}} · {{id}}', { type: item.sacrament_type, id: item.record_id })}</p>
              <p className="mt-1 text-xs text-gray-700">{Object.entries(item.field_changes).map(([field, change]) => `${field}: ${change.old} → ${change.new}`).join('; ')}</p>
            </div>
            <div className="flex gap-2">
              <Button size="sm" disabled={review.isPending || !reviewNotes[item.id]?.trim()} onClick={() => review.mutate({ id: item.id, action: 'APPROVE' })}>{t('sacraments.amendment_approve', 'Approve')}</Button>
              <Button size="sm" variant="danger" disabled={review.isPending || !reviewNotes[item.id]?.trim()} onClick={() => review.mutate({ id: item.id, action: 'REJECT' })}>{t('sacraments.amendment_reject', 'Reject')}</Button>
            </div>
          </div>
          <input
            className="mt-3 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            aria-label={t('sacraments.amendment_review_notes', 'Review notes')}
            placeholder={t('sacraments.amendment_review_notes', 'Review notes')}
            value={reviewNotes[item.id] || ''}
            onChange={(event) => setReviewNotes((notes) => ({ ...notes, [item.id]: event.target.value }))}
          />
        </article>
      ))}
    </section>
  );
};
