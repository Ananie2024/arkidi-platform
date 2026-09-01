import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { BookOpen } from 'lucide-react';
import { ArchiveBook, domainApi } from '../../core/api/domain';

export const ArchivePage: React.FC = () => {
  const { t } = useTranslation();
  const parishesQuery = useQuery({ queryKey: ['parishes'], queryFn: () => domainApi.listParishes() });
  const parishId = parishesQuery.data?.[0]?.id;
  const booksQuery = useQuery({
    queryKey: ['archive-books', parishId],
    queryFn: () => domainApi.listArchiveBooks(parishId as string),
    enabled: Boolean(parishId),
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
          isLoading={parishesQuery.isLoading || booksQuery.isLoading}
          emptyMessage={parishesQuery.isError || booksQuery.isError ? t('archive.empty_error') : t('archive.empty_none')}
        />
      </Card>
    </div>
  );
};
