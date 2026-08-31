import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Table, Column } from './Table';

interface Row {
  id: string;
  name: string;
  code: string;
  note?: string;
}

const columns: Column<Row>[] = [
  { header: 'Name', accessor: 'name' },
  { header: 'Code', accessor: 'code' },
  { header: 'Note', accessor: (row) => row.note || '-' },
];

const rows: Row[] = [
  { id: '1', name: 'Sainte Famille', code: 'PAR-SF-01' },
  { id: '2', name: 'Regina Pacis', code: 'PAR-RP-02', note: 'Mission chapel' },
];

describe('Table', () => {
  it('renders headers and one row per data item', () => {
    render(<Table columns={columns} data={rows} />);

    expect(screen.getByRole('columnheader', { name: 'Name' })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: 'Code' })).toBeInTheDocument();
    expect(screen.getByText('Sainte Famille')).toBeInTheDocument();
    expect(screen.getByText('PAR-RP-02')).toBeInTheDocument();
    // Function accessor falls back to the '-' placeholder for missing values.
    expect(screen.getAllByText('-')).toHaveLength(1);
    expect(screen.getByText('Mission chapel')).toBeInTheDocument();
  });

  it('renders the empty message when data is empty', () => {
    render(<Table columns={columns} data={[]} emptyMessage="Nothing archived yet" />);

    expect(screen.getByText('Nothing archived yet')).toBeInTheDocument();
    expect(screen.queryByRole('table')).toBeInTheDocument();
    expect(screen.queryByText('Sainte Famille')).not.toBeInTheDocument();
  });

  it('renders a loading spinner instead of a table while isLoading', () => {
    const { container } = render(<Table columns={columns} data={rows} isLoading />);

    expect(screen.queryByRole('table')).not.toBeInTheDocument();
    expect(container.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('defaults the empty message when none is supplied', () => {
    render(<Table columns={columns} data={[]} />);

    expect(screen.getByText('No records found')).toBeInTheDocument();
  });
});
