import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { FinancePage } from './FinancePage';
import { domainApi } from '../../core/api/domain';
import { renderWithProviders } from '../../test/testUtils';
import { parishFixture, donationFixture } from '../../test/fixtures';

vi.mock('../../core/api/domain', () => ({
  domainApi: {
    listParishes: vi.fn(),
    listDonations: vi.fn(),
  },
}));

const mockedApi = vi.mocked(domainApi);

describe('FinancePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads the first parish and renders its donation ledger', async () => {
    mockedApi.listParishes.mockResolvedValue([parishFixture]);
    mockedApi.listDonations.mockResolvedValue([donationFixture]);
    renderWithProviders(<FinancePage />);

    expect(
      await screen.findByRole('heading', { name: /parish & archdiocesan finance/i })
    ).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('RC-2026-0042')).toBeInTheDocument();
    });
    expect(screen.getByText('TITHE')).toBeInTheDocument();
    expect(screen.getByText('Mukamana Alice')).toBeInTheDocument();
    expect(screen.getByText('25,000 RWF')).toBeInTheDocument();
    expect(screen.getByText('MOMO')).toBeInTheDocument();
    expect(screen.getByText('Recorded')).toBeInTheDocument();
    // The donation query is scoped to the first parish of the directory.
    expect(mockedApi.listDonations).toHaveBeenCalledWith('parish-1');
  });

  it('does not query donations until a parish is known', async () => {
    mockedApi.listParishes.mockResolvedValue([]);
    renderWithProviders(<FinancePage />);

    expect(await screen.findByText('No donations found for the current parish.')).toBeInTheDocument();
    expect(mockedApi.listDonations).not.toHaveBeenCalled();
  });

  it('shows the API error empty message when the request fails', async () => {
    mockedApi.listParishes.mockRejectedValue(new Error('boom'));
    renderWithProviders(<FinancePage />);

    expect(
      await screen.findByText(/unable to load donations from the api/i)
    ).toBeInTheDocument();
  });
});
