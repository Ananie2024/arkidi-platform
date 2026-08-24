import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { BookOpen } from 'lucide-react';
import { ArchiveBook, domainApi } from '../../core/api/domain';

export const ArchivePage: React.FC = () => {
  const parishesQuery = useQuery({ queryKey: ['parishes'], queryFn: () => domainApi.listParishes() });
  const parishId = parishesQuery.data?.[0]?.id;
  const booksQuery = useQuery({
    queryKey: ['archive-books', parishId],
    queryFn: () => domainApi.listArchiveBooks(parishId as string),
    enabled: Boolean(parishId),
  });

  const columns: Column<ArchiveBook>[] = [
    { header: 'Ledger Book', accessor: 'book_title' },
    { header: 'Sacrament', accessor: 'sacrament_type' },
    { header: 'Volume', accessor: 'volume_number' },
    { header: 'Period', accessor: (row) => `${row.start_year} - ${row.end_year}` },
    { header: 'Shelf Location', accessor: (row) => row.shelf_location || '-' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Digital Archive & Historic Registers</h1>
          <p className="text-xs text-gray-500 mt-0.5">Scanned sacramental registry books, OCR indexing and certificate verification</p>
        </div>
        <Button size="sm">
          <BookOpen className="w-4 h-4 mr-1.5" /> Catalog Ledger Book
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          data={booksQuery.data || []}
          isLoading={parishesQuery.isLoading || booksQuery.isLoading}
          emptyMessage={parishesQuery.isError || booksQuery.isError ? 'Unable to load archive books from the API.' : 'No archive books found for the current parish.'}
        />
      </Card>
    </div>
  );
};
