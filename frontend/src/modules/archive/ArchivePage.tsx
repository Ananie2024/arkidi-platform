import React from 'react';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { BookOpen } from 'lucide-react';

interface ArchiveBookItem {
  id: string;
  book_title: string;
  sacrament_type: string;
  volume_number: string;
  start_year: number;
  end_year: number;
  shelf_location: string;
}

export const ArchivePage: React.FC = () => {
  const dummyBooks: ArchiveBookItem[] = [
    {
      id: '1',
      book_title: 'Registre des Baptêmes - Sainte Famille',
      sacrament_type: 'BAPTISM',
      volume_number: 'Vol 12',
      start_year: 1990,
      end_year: 2000,
      shelf_location: 'Salle des Archives, Étagère B2',
    },
    {
      id: '2',
      book_title: 'Registre des Mariages - Saint Michel',
      sacrament_type: 'MATRIMONY',
      volume_number: 'Vol 5',
      start_year: 1995,
      end_year: 2005,
      shelf_location: 'Salle des Archives, Étagère C1',
    },
  ];

  const columns: Column<ArchiveBookItem>[] = [
    { header: 'Ledger Book', accessor: 'book_title' },
    { header: 'Sacrament', accessor: 'sacrament_type' },
    { header: 'Volume', accessor: 'volume_number' },
    { header: 'Period', accessor: (row) => `${row.start_year} - ${row.end_year}` },
    { header: 'Shelf Location', accessor: 'shelf_location' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Digital Archive & Historic Registers</h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Scanned sacramental registry books, OCR indexing and certificate verification
          </p>
        </div>
        <Button size="sm">
          <BookOpen className="w-4 h-4 mr-1.5" /> Catalog Ledger Book
        </Button>
      </div>

      <Card>
        <Table columns={columns} data={dummyBooks} />
      </Card>
    </div>
  );
};
