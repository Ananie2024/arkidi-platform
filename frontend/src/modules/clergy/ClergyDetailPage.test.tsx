import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import { ClergyDetailPage } from './ClergyDetailPage';
import { domainApi } from '../../core/api/domain';
import { renderWithProviders } from '../../test/testUtils';
import { priestFixture } from '../../test/fixtures';

vi.mock('../../core/api/domain', () => ({
  domainApi: {
    getPriest: vi.fn(),
  },
}));

const mockedApi = vi.mocked(domainApi);

function renderDetail() {
  return renderWithProviders(<ClergyDetailPage />, {
    route: `/clergy/${priestFixture.id}`,
    path: '/clergy/:clergyId',
  });
}

describe('ClergyDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the clergy dossier from the API payload', async () => {
    mockedApi.getPriest.mockResolvedValue(priestFixture);
    renderDetail();

    expect(
      await screen.findByRole('heading', { name: /abbé uwimana jean/i })
    ).toBeInTheDocument();
    expect(screen.getByText('Biographical & Ordination Data')).toBeInTheDocument();
    expect(screen.getByText('Current Assignment')).toBeInTheDocument();
    expect(screen.getByText('Msgr. Antoine Kambanda')).toBeInTheDocument();
    expect(screen.getByText('Ordained in 2003; served in three parishes.')).toBeInTheDocument();
    expect(screen.getByText('ACTIVE_DUTY')).toBeInTheDocument();
    expect(mockedApi.getPriest).toHaveBeenCalledWith(priestFixture.id);
  });

  it('shows the API error message when the record cannot be loaded', async () => {
    mockedApi.getPriest.mockRejectedValue(new Error('boom'));
    renderDetail();

    expect(
      await screen.findByText(/unable to load the clergy record from the api/i)
    ).toBeInTheDocument();
  });
});
