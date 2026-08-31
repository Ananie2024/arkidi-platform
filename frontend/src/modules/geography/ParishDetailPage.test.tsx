import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import { ParishDetailPage } from './ParishDetailPage';
import { domainApi } from '../../core/api/domain';
import { renderWithProviders } from '../../test/testUtils';
import { parishFixture } from '../../test/fixtures';

vi.mock('../../core/api/domain', () => ({
  domainApi: {
    getParish: vi.fn(),
  },
}));

const mockedApi = vi.mocked(domainApi);

function renderDetail() {
  return renderWithProviders(<ParishDetailPage />, {
    route: `/geography/parishes/${parishFixture.id}`,
    path: '/geography/parishes/:parishId',
  });
}

describe('ParishDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the parish dossier from the API payload', async () => {
    mockedApi.getParish.mockResolvedValue(parishFixture);
    renderDetail();

    expect(
      await screen.findByRole('heading', { name: /sainte famille parish/i })
    ).toBeInTheDocument();
    expect(screen.getByText('Code: PAR-SF-01')).toBeInTheDocument();
    expect(screen.getByText('Holy Family')).toBeInTheDocument();
    expect(screen.getByText('Parish Information')).toBeInTheDocument();
    expect(screen.getByText('Geolocation')).toBeInTheDocument();
    expect(screen.getByText('Registration')).toBeInTheDocument();
    expect(screen.getByText('-1.9536')).toBeInTheDocument();
    expect(screen.getByText('Active Parish')).toBeInTheDocument();
    // The route param is forwarded to the API call.
    expect(mockedApi.getParish).toHaveBeenCalledWith(parishFixture.id);
  });

  it('renders fallback dashes for missing optional fields', async () => {
    mockedApi.getParish.mockResolvedValue({
      ...parishFixture,
      patron_saint: null,
      phone: null,
      email: null,
      address: null,
    });
    renderDetail();

    await screen.findByRole('heading', { name: /sainte famille parish/i });
    const dashes = screen.getAllByText('-');
    expect(dashes.length).toBeGreaterThanOrEqual(4);
  });

  it('shows the API error message when the parish cannot be loaded', async () => {
    mockedApi.getParish.mockRejectedValue(new Error('boom'));
    renderDetail();

    expect(
      await screen.findByText(/unable to load parish details from the api/i)
    ).toBeInTheDocument();
  });
});
