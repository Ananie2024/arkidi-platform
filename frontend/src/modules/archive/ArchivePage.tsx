import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { BookOpen, Download, RefreshCw, Search, Upload } from 'lucide-react';
import { ArchiveBook, ScannedPage, domainApi } from '../../core/api/domain';
import { useActiveParish } from '../../core/hooks/useActiveParish';
import { useAuthContext } from '../../core/auth/AuthContext';

function saveBlob(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = name;
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export const ArchivePage: React.FC = () => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { hasRole } = useAuthContext();
  const { activeParishId, isLoading: parishesLoading, isError: parishesError } = useActiveParish();
  const canManageArchive = hasRole(['PARISH_SECRETARY', 'CHANCELLOR', 'ARCHBISHOP']);
  const canReviewDisposition = hasRole(['CHANCELLOR', 'PARISH_PRIEST', 'ARCHBISHOP']);
  const [selectedBook, setSelectedBook] = useState<string | null>(null);
  const [selectedPage, setSelectedPage] = useState<string | null>(null);
  const [showCatalogForm, setShowCatalogForm] = useState(false);
  const [searchInput, setSearchInput] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [dispositionReason, setDispositionReason] = useState('');

  const booksQuery = useQuery({
    queryKey: ['archive-books', activeParishId],
    queryFn: () => domainApi.listArchiveBooks(activeParishId as string),
    enabled: Boolean(activeParishId),
  });
  const pagesQuery = useQuery({
    queryKey: ['archive-pages', selectedBook],
    queryFn: () => domainApi.listArchivePages(selectedBook as string),
    enabled: Boolean(selectedBook),
  });
  const pageDetailQuery = useQuery({
    queryKey: ['archive-page', selectedPage],
    queryFn: () => domainApi.getArchivePage(selectedPage as string),
    enabled: Boolean(selectedPage),
    refetchInterval: (query) => query.state.data?.ocr_metadata?.status === 'queued' ? 3000 : false,
  });
  const searchQuery = useQuery({
    queryKey: ['archive-search', activeParishId, searchTerm],
    queryFn: () => domainApi.searchArchivePages(searchTerm, activeParishId || undefined),
    enabled: Boolean(activeParishId && searchTerm.length >= 2),
  });
  const documentsQuery = useQuery({
    queryKey: ['archive-documents', activeParishId],
    queryFn: () => domainApi.listArchiveDocuments(activeParishId as string),
    enabled: Boolean(activeParishId),
  });

  const refreshArchive = async () => {
    await queryClient.invalidateQueries({ queryKey: ['archive-books', activeParishId] });
    await queryClient.invalidateQueries({ queryKey: ['archive-pages', selectedBook] });
    await queryClient.invalidateQueries({ queryKey: ['archive-page', selectedPage] });
    await queryClient.invalidateQueries({ queryKey: ['archive-search'] });
  };
  const createBook = useMutation({
    mutationFn: domainApi.createArchiveBook,
    onSuccess: async (book: ArchiveBook) => {
      await queryClient.invalidateQueries({ queryKey: ['archive-books', activeParishId] });
      setSelectedBook(book.id);
      setShowCatalogForm(false);
    },
  });
  const uploadPage = useMutation({
    mutationFn: ({ page, file }: { page: number; file: File }) =>
      domainApi.uploadArchivePage(selectedBook as string, page, file),
    onSuccess: async (page: ScannedPage) => {
      await refreshArchive();
      setSelectedPage(page.id);
    },
  });
  const triggerOcr = useMutation({
    mutationFn: domainApi.triggerPageOcr,
    onSuccess: refreshArchive,
  });
  const replaceScan = useMutation({
    mutationFn: ({ id, file }: { id: string; file: File }) => domainApi.replaceArchivePageScan(id, file),
    onSuccess: refreshArchive,
  });
  const reviewPage = useMutation({
    mutationFn: ({ id, status, notes }: { id: string; status: 'REVIEWED' | 'NEEDS_RESCAN'; notes: string }) =>
      domainApi.reviewArchivePage(id, { status, notes }),
    onSuccess: refreshArchive,
  });
  const disposition = useMutation({
    mutationFn: ({ id, action }: { id: string; action: 'DISPOSE' | 'PRESERVE' | 'REOPEN' }) =>
      domainApi.reviewDocumentDisposition(id, action, dispositionReason),
    onSuccess: async () => {
      setDispositionReason('');
      await queryClient.invalidateQueries({ queryKey: ['archive-documents', activeParishId] });
    },
  });

  const handleUpload = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const file = form.get('scan');
    if (file instanceof File && selectedBook) {
      uploadPage.mutate({ page: Number(form.get('page_number')), file });
      event.currentTarget.reset();
    }
  };

  const documents = documentsQuery.data || [];
  const needsDisposition = documents.filter((doc) => doc.disposition_status === 'DUE_FOR_REVIEW');
  const completedDisposition = documents.filter((doc) => ['DISPOSED', 'PRESERVE_INDEFINITELY'].includes(doc.disposition_status || ''));

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('archive.title')}</h1>
          <p className="mt-0.5 text-xs text-gray-500">{t('archive.subtitle')}</p>
        </div>
        {canManageArchive && <Button size="sm" onClick={() => setShowCatalogForm((open) => !open)} disabled={!activeParishId}>
          <BookOpen className="mr-1.5 h-4 w-4" />{t('archive.catalog_button', 'Catalog ledger book')}
        </Button>}
      </div>

      {showCatalogForm && <Card title={t('archive.catalog_button', 'Catalog ledger book')}>
        <form className="grid gap-3 sm:grid-cols-3" onSubmit={(event) => {
          event.preventDefault();
          if (!activeParishId) return;
          const values = new FormData(event.currentTarget);
          createBook.mutate({ parish_id: activeParishId, book_title: values.get('book_title'), sacrament_type: values.get('sacrament_type'), volume_number: values.get('volume_number'), start_year: Number(values.get('start_year')), end_year: Number(values.get('end_year')), shelf_location: values.get('shelf_location') || null });
        }}>
          <input name="book_title" required maxLength={200} placeholder={t('archive.book_title', 'Ledger title')} className="rounded border px-3 py-2 text-sm" />
          <select name="sacrament_type" className="rounded border px-3 py-2 text-sm" defaultValue="BAPTISM">
            {['BAPTISM', 'FIRST_COMMUNION', 'CONFIRMATION', 'MATRIMONY', 'HOLY_ORDERS', 'RELIGIOUS_PROFESSION', 'ANOINTING_OF_THE_SICK', 'CHRISTIAN_FUNERAL'].map((type) => <option key={type} value={type}>{type.split('_').join(' ')}</option>)}
          </select>
          <input name="volume_number" required placeholder={t('archive.col_volume', 'Volume')} className="rounded border px-3 py-2 text-sm" />
          <input name="start_year" required type="number" min="1" placeholder={t('archive.start_year', 'Start year')} className="rounded border px-3 py-2 text-sm" />
          <input name="end_year" required type="number" min="1" placeholder={t('archive.end_year', 'End year')} className="rounded border px-3 py-2 text-sm" />
          <input name="shelf_location" placeholder={t('archive.col_shelf', 'Shelf location')} className="rounded border px-3 py-2 text-sm" />
          {createBook.isError && <p role="alert" className="text-sm text-red-700">{t('archive.catalog_error', 'Unable to catalog this ledger book. Check the volume and year range.')}</p>}
          <div className="flex justify-end gap-2 sm:col-span-3"><Button type="button" variant="outline" onClick={() => setShowCatalogForm(false)}>{t('common.cancel', 'Cancel')}</Button><Button type="submit" disabled={createBook.isPending}>{t('common.save', 'Save')}</Button></div>
        </form>
      </Card>}

      <Card title={t('archive.books_title', 'Cataloged ledger books')}>
        {parishesError && <p role="alert" className="text-sm text-red-700">{t('archive.empty_error')}</p>}
        {booksQuery.isError && <p role="alert" className="text-sm text-red-700">{t('archive.empty_error')}</p>}
        {booksQuery.data?.length === 0 && <p className="text-sm text-gray-500">{t('archive.empty_none')}</p>}
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {(booksQuery.data || []).map((book) => <button key={book.id} type="button" onClick={() => { setSelectedBook(book.id); setSelectedPage(null); }} className={`rounded-lg border p-3 text-left ${selectedBook === book.id ? 'border-brand-500 bg-brand-50' : 'border-gray-200 hover:bg-gray-50'}`}>
            <span className="block font-semibold text-gray-900">{book.book_title}</span>
            <span className="mt-1 block text-xs text-gray-600">{book.sacrament_type.split('_').join(' ')} · {book.volume_number} · {book.start_year}–{book.end_year}</span>
            <span className="mt-1 block text-xs text-gray-500">{book.shelf_location || '—'} · {book.total_scanned_pages ?? 0} pages</span>
          </button>)}
        </div>
        {parishesLoading && <p className="text-sm text-gray-500">{t('common.loading', 'Loading...')}</p>}
      </Card>

      {selectedBook && <Card title={t('archive.pages_title', 'Scanned pages')}>
        {canManageArchive && <form className="mb-4 flex flex-wrap items-end gap-3 border-b pb-4" onSubmit={handleUpload}>
          <label className="text-sm">{t('archive.page_number', 'Page number')}<input name="page_number" type="number" min="1" required className="mt-1 block rounded border px-3 py-2" /></label>
          <label className="text-sm">{t('archive.scan_file', 'Scan image')}<input name="scan" type="file" accept=".tif,.tiff,.png,.jpg,.jpeg,image/tiff,image/png,image/jpeg" required className="mt-1 block max-w-full text-sm" /></label>
          <Button type="submit" disabled={uploadPage.isPending}><Upload className="mr-1 h-4 w-4" />{t('archive.upload_scan', 'Upload scan')}</Button>
          {uploadPage.isError && <p role="alert" className="w-full text-sm text-red-700">{t('archive.upload_error', 'Upload failed. Check the image format, size, and page number.')}</p>}
        </form>}
        {pagesQuery.isError && <p role="alert" className="text-sm text-red-700">{t('archive.pages_error', 'Unable to load scans for this ledger.')}</p>}
        {pagesQuery.data?.length === 0 && <p className="text-sm text-gray-500">{t('archive.pages_empty', 'No scans uploaded for this ledger yet.')}</p>}
        <div className="divide-y">
          {(pagesQuery.data || []).map((page) => <div key={page.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
            <button type="button" className="text-left" onClick={() => setSelectedPage(page.id)}>
              <span className="font-medium">{t('archive.page_number', 'Page')} {page.page_number}</span>
              <span className="ml-3 text-xs text-gray-500">OCR: {page.ocr_metadata?.status || 'queued'} · Review: {page.review_status}</span>
            </button>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={() => domainApi.downloadArchivePage(page.id).then((blob) => saveBlob(blob, `archive-page-${page.page_number}`))}><Download className="mr-1 h-3.5 w-3.5" />{t('archive.download_scan', 'Original')}</Button>
              {canManageArchive && <Button size="sm" variant="outline" onClick={() => triggerOcr.mutate(page.id)} disabled={triggerOcr.isPending}><RefreshCw className="mr-1 h-3.5 w-3.5" />{t('archive.retry_ocr', 'Retry OCR')}</Button>}
            </div>
          </div>)}
        </div>
      </Card>}

      {selectedPage && pageDetailQuery.data && <Card title={`${t('archive.page_number', 'Page')} ${pageDetailQuery.data.page_number}`}>
        <div className="mb-3 flex flex-wrap items-center gap-3 text-sm">
          <span>{t('archive.ocr_status', 'OCR status')}: <strong>{pageDetailQuery.data.ocr_metadata?.status || 'queued'}</strong></span>
          <span>{t('archive.review_status', 'Review status')}: <strong>{pageDetailQuery.data.review_status}</strong></span>
          {pageDetailQuery.data.ocr_metadata?.mean_confidence != null && <span>{t('archive.ocr_confidence', 'OCR confidence')}: {pageDetailQuery.data.ocr_metadata.mean_confidence}%</span>}
          <Button size="sm" variant="outline" onClick={() => domainApi.downloadArchivePage(selectedPage).then((blob) => saveBlob(blob, `archive-page-${pageDetailQuery.data?.page_number}`))}><Download className="mr-1 h-3.5 w-3.5" />{t('archive.download_scan', 'Original image')}</Button>
        </div>
        <pre className="max-h-72 overflow-auto whitespace-pre-wrap rounded bg-gray-50 p-3 text-xs">{pageDetailQuery.data.ocr_raw_text || t('archive.ocr_empty', 'No OCR text is available yet.')}</pre>
        {pageDetailQuery.data.review_notes && <p className="mt-3 text-sm text-gray-600">{t('archive.review_notes', 'Review notes')}: {pageDetailQuery.data.review_notes}</p>}
        {canManageArchive && pageDetailQuery.data.review_status === 'NEEDS_RESCAN' && <form className="mt-4 flex flex-wrap items-end gap-3 rounded border border-amber-200 bg-amber-50 p-3" onSubmit={(event) => {
          event.preventDefault();
          const file = new FormData(event.currentTarget).get('rescan');
          if (file instanceof File) replaceScan.mutate({ id: selectedPage, file });
        }}>
          <label className="text-sm">{t('archive.replace_scan', 'Upload replacement scan')}<input name="rescan" type="file" accept=".tif,.tiff,.png,.jpg,.jpeg,image/tiff,image/png,image/jpeg" required className="mt-1 block text-sm" /></label>
          <Button type="submit" disabled={replaceScan.isPending}><Upload className="mr-1 h-4 w-4" />{t('archive.rescan', 'Upload and reprocess')}</Button>
          {replaceScan.isError && <p role="alert" className="w-full text-sm text-red-700">{t('archive.rescan_error', 'Unable to replace this scan.')}</p>}
        </form>}
        {canManageArchive && <form className="mt-4 grid gap-3 sm:grid-cols-[1fr_auto_auto]" onSubmit={(event) => {
          event.preventDefault();
          const form = new FormData(event.currentTarget);
          const notes = String(form.get('review_notes') || '');
          const submitter = (event.nativeEvent as SubmitEvent).submitter as HTMLButtonElement | null;
          const status = (submitter?.value || 'REVIEWED') as 'REVIEWED' | 'NEEDS_RESCAN';
          reviewPage.mutate({ id: selectedPage, status, notes });
        }}>
          <input name="review_notes" minLength={3} required placeholder={t('archive.review_notes_required', 'Review notes (required)')} className="rounded border px-3 py-2 text-sm" />
          <Button type="submit" name="status" value="NEEDS_RESCAN" variant="outline" disabled={reviewPage.isPending}>{t('archive.needs_rescan', 'Needs rescanning')}</Button>
          <Button type="submit" name="status" value="REVIEWED" disabled={reviewPage.isPending}>{t('archive.mark_reviewed', 'Mark reviewed')}</Button>
          {reviewPage.isError && <p role="alert" className="text-sm text-red-700 sm:col-span-3">{t('archive.review_error', 'Unable to save archive review.')}</p>}
        </form>}
      </Card>}

      <Card title={t('archive.search_title', 'Search archive scans')}>
        <form className="flex gap-2" onSubmit={(event) => { event.preventDefault(); setSearchTerm(searchInput.trim()); }}>
          <input value={searchInput} onChange={(event) => setSearchInput(event.target.value)} minLength={2} placeholder={t('archive.search_placeholder', 'Search book titles and OCR text')} className="min-w-0 flex-1 rounded border px-3 py-2 text-sm" />
          <Button type="submit" disabled={searchInput.trim().length < 2}><Search className="mr-1 h-4 w-4" />{t('common.search', 'Search')}</Button>
        </form>
        {searchQuery.isError && <p role="alert" className="mt-3 text-sm text-red-700">{t('archive.search_error', 'Archive search failed.')}</p>}
        <ul className="mt-3 divide-y">{(searchQuery.data || []).map((page) => <li key={page.id} className="py-2"><button type="button" className="text-sm text-brand-700 hover:underline" onClick={() => { setSelectedBook(page.ledger_book_id); setSelectedPage(page.id); }}>{t('archive.page_number', 'Page')} {page.page_number} · {page.ocr_raw_text?.slice(0, 160) || page.ledger_book_id}</button></li>)}</ul>
      </Card>

      <Card title={t('archive.retention_title', 'Retention review')}>
        <p className="mb-3 text-xs text-gray-600">{t('archive.retention_help', 'Documents marked disposed remain in managed storage. Reopen restores a disposed or preserved item to the review queue.')}</p>
        {documentsQuery.isError && <p role="alert" className="text-sm text-red-700">{t('archive.documents_error', 'Unable to load archived documents.')}</p>}
        {needsDisposition.length === 0 && <p className="text-sm text-gray-500">{t('archive.retention_empty', 'No documents are due for review.')}</p>}
        {needsDisposition.map((doc) => <div key={doc.id} className="flex flex-wrap items-center justify-between gap-3 border-t py-3">
          <div><p className="font-medium">{doc.title}</p><p className="text-xs text-gray-500">{t('archive.flagged_at', 'Flagged')}: {doc.retention_flagged_at ? new Date(doc.retention_flagged_at).toLocaleDateString() : '—'} · {doc.classification}</p></div>
          <div className="flex gap-2"><Button size="sm" variant="outline" onClick={() => domainApi.downloadArchiveDocument(doc.id).then((blob) => saveBlob(blob, doc.title))}><Download className="mr-1 h-3.5 w-3.5" />{t('archive.download_document', 'Download')}</Button>{canReviewDisposition && <><Button size="sm" variant="outline" disabled={disposition.isPending || dispositionReason.trim().length < 5} onClick={() => disposition.mutate({ id: doc.id, action: 'PRESERVE' })}>{t('archive.preserve', 'Preserve')}</Button><Button size="sm" variant="danger" disabled={disposition.isPending || dispositionReason.trim().length < 5} onClick={() => disposition.mutate({ id: doc.id, action: 'DISPOSE' })}>{t('archive.mark_disposed', 'Mark disposed')}</Button></>}</div>
        </div>)}
        {canReviewDisposition && needsDisposition.length > 0 && <label className="mt-2 block text-sm">{t('archive.disposition_reason', 'Disposition reason (required)')}<textarea value={dispositionReason} onChange={(event) => setDispositionReason(event.target.value)} minLength={5} maxLength={2000} className="mt-1 block w-full rounded border px-3 py-2" /></label>}
        {disposition.isError && <p role="alert" className="mt-2 text-sm text-red-700">{t('archive.disposition_error', 'Unable to update document disposition.')}</p>}
        {completedDisposition.length > 0 && <div className="mt-4 border-t pt-3"><h3 className="mb-2 text-sm font-semibold">{t('archive.completed_disposition', 'Completed dispositions')}</h3>{completedDisposition.map((doc) => <div key={doc.id} className="flex items-center justify-between py-2 text-sm"><span>{doc.title} · {doc.disposition_status}</span>{canReviewDisposition && <Button size="sm" variant="outline" disabled={disposition.isPending || dispositionReason.trim().length < 5} onClick={() => disposition.mutate({ id: doc.id, action: 'REOPEN' })}>{t('archive.reopen_review', 'Reopen review')}</Button>}</div>)}</div>}
      </Card>
    </div>
  );
};
