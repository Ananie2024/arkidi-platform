import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor, fireEvent } from '@testing-library/react';
import { FaithfulListPage } from './FaithfulListPage';
import { domainApi } from '../../core/api/domain';
import { renderWithProviders } from '../../test/testUtils';
import { faithfulFixture } from '../../test/fixtures';
import { PaginatedResult } from '../../core/types/common.types';
import { Faithful } from '../../core/types/faithful.types';

vi.mock('../../core/api/domain', () => ({
  domainApi: {
    listFaithful: vi.fn(),
  },
}));

const mockedApi = vi.mocked(domainApi);

const paginated = (items: Faithful[]): PaginatedResult<Faithful> => ({
  items,
  total: items.length,
  page: 1,
  page_size: items.length || 25,
  total_pages: 1,
});

describe('FaithfulListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders faithful rows with canonical status badges', async () => {
    mockedApi.listFaithful.mockResolvedValue(paginated([faithfulFixture]));
    renderWithProviders(<FaithfulListPage />);

    await waitFor(() => {
      expect(screen.getByText('Mukamana Alice')).toBeInTheDocument();
    });
    expect(screen.getByText('REG-2026-0001')).toBeInTheDocument();
    expect(screen.getByText('Christian: Marie')).toBeInTheDocument();
    expect(screen.getByText('Confirmed')).toBeInTheDocument();
    expect(screen.getByText('View Profile →')).toHaveAttribute('href', '/faithful/faithful-1');
    expect(mockedApi.listFaithful).toHaveBeenCalledWith(undefined);
  });

  it('re-queries the API when the search box is used', async () => {
    mockedApi.listFaithful.mockResolvedValue(paginated([]));
    renderWithProviders(<FaithfulListPage />);

    fireEvent.change(
      screen.getByPlaceholderText(/search by name, registration code, or nid/i),
      { target: { value: 'Mukamana' } }
    );

    await waitFor(() => {
      expect(mockedApi.listFaithful).toHaveBeenLastCalledWith('Mukamana');
    });
  });

  it('opens the registration modal from the Register Faithful button', async () => {
    mockedApi.listFaithful.mockResolvedValue(paginated([faithfulFixture]));
    renderWithProviders(<FaithfulListPage />);

    await screen.findByText('Mukamana Alice');
    fireEvent.click(screen.getByRole('button', { name: /register faithful/i }));

    expect(
      await screen.findByText(/register new parishioner \(kwandika umukristu\)/i)
    ).toBeInTheDocument();
  });

  it('shows the API error empty message when the request fails', async () => {
    mockedApi.listFaithful.mockRejectedValue(new Error('boom'));
    renderWithProviders(<FaithfulListPage />);

    expect(
      await screen.findByText(/unable to load faithful records from the api/i)
    ).toBeInTheDocument();
  });
});
