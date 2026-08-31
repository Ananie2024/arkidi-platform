import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { ClergyListPage } from './ClergyListPage';
import { domainApi } from '../../core/api/domain';
import { renderWithProviders } from '../../test/testUtils';
import { priestFixture } from '../../test/fixtures';

vi.mock('../../core/api/domain', () => ({
  domainApi: {
    listPriests: vi.fn(),
  },
}));

const mockedApi = vi.mocked(domainApi);

describe('ClergyListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the clergy roster heading and rows', async () => {
    mockedApi.listPriests.mockResolvedValue([priestFixture]);
    renderWithProviders(<ClergyListPage />);

    expect(
      await screen.findByRole('heading', { name: /clergy & religious roster/i })
    ).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('Uwimana Jean')).toBeInTheDocument();
    });
    expect(screen.getByText('Abbé')).toBeInTheDocument();
    expect(screen.getByText('Parish Priest')).toBeInTheDocument();
    expect(screen.getByText('ACTIVE_DUTY')).toBeInTheDocument();
    expect(screen.getByText('View Dossier →')).toHaveAttribute('href', '/clergy/priest-1');
  });

  it('renders a neutral badge for non-active clergy status', async () => {
    mockedApi.listPriests.mockResolvedValue([{ ...priestFixture, status: 'RETIRED' }]);
    renderWithProviders(<ClergyListPage />);

    await waitFor(() => {
      expect(screen.getByText('RETIRED')).toBeInTheDocument();
    });
  });

  it('shows the API error empty message when the request fails', async () => {
    mockedApi.listPriests.mockRejectedValue(new Error('boom'));
    renderWithProviders(<ClergyListPage />);

    expect(
      await screen.findByText(/unable to load clergy records from the api/i)
    ).toBeInTheDocument();
  });
});
