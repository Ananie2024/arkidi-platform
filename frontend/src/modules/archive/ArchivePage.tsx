import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { BookOpen } from 'lucide-react';
import { ArchiveBook, domainApi } from '../../core/api/domain';
import { useActiveParish } from '../../core/hooks/useActiveParish';

export const ArchivePage: React.FC = () => {
  const { t } = useTranslation();
  const { activeParishId, isLoading: parishesLoading, isError: parishesError } = useActiveParish();
  const booksQuery = useQuery({
    queryKey: ['archive-books', activeParishId],
    queryFn: () => domainApi.listArchiveBooks(activeParishId as string),
    enabled: Boolean(activeParishId),
  });

  const columns: Column<ArchiveBook>[] = [
    { header: t('archive.col_ledger'), accessor: 'book_title' },
    { header: t('archive.col_sacrament'), accessor: 'sacrament_type' },
    { header: t('archive.col_volume'), accessor: 'volume_number' },
    { header: t('archive.col_period'), accessor: (row) => `${row.start_year} - ${row.end_year}` },
    { header: t('archive.col_shelf'), accessor: (row) => row.shelf_location || '-' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('archive.title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('archive.subtitle')}</p>
        </div>
        <Button size="sm">
          <BookOpen className="w-4 h-4 mr-1.5" /> {t('archive.catalog_button')}
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          data={booksQuery.data || []}
          isLoading={parishesLoading || booksQuery.isLoading}
          emptyMessage={parishesError || booksQuery.isError ? t('archive.empty_error') : t('archive.empty_none')}
        />
      </Card>
    </div>
  );
};
