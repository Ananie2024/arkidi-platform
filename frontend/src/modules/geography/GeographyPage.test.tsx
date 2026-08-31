import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { GeographyPage } from './GeographyPage';
import { domainApi } from '../../core/api/domain';
import { renderWithProviders } from '../../test/testUtils';
import { deaneryFixture } from '../../test/fixtures';

// The page fetches through the shared domain API layer — mock it wholesale so
// the tests exercise the real query/render pipeline without a live backend.
vi.mock('../../core/api/domain', () => ({
  domainApi: {
    listDeaneries: vi.fn(),
  },
}));

const mockedApi = vi.mocked(domainApi);

describe('GeographyPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the deanery directory heading', async () => {
    mockedApi.listDeaneries.mockResolvedValue([deaneryFixture]);
    renderWithProviders(<GeographyPage />);

    expect(
      await screen.findByRole('heading', { name: /ecclesiastical hierarchy & deaneries/i })
    ).toBeInTheDocument();
  });

  it('renders deanery rows returned by the API', async () => {
    mockedApi.listDeaneries.mockResolvedValue([deaneryFixture]);
    renderWithProviders(<GeographyPage />);

    await waitFor(() => {
      expect(screen.getByText('Deanery of Kigali Centre')).toBeInTheDocument();
    });
    expect(screen.getByText('DOY-KGL-01')).toBeInTheDocument();
    expect(screen.getByText('Fr. Jean Mutangana')).toBeInTheDocument();
    expect(screen.getByText('View Parishes →')).toHaveAttribute(
      'href',
      '/geography/parishes?deanery=deanery-1'
    );
  });

  it('shows the API error empty message when the request fails', async () => {
    mockedApi.listDeaneries.mockRejectedValue(new Error('boom'));
    renderWithProviders(<GeographyPage />);

    expect(
      await screen.findByText(/unable to load deaneries from the api/i)
    ).toBeInTheDocument();
  });

  it('shows the empty message when no deaneries exist', async () => {
    mockedApi.listDeaneries.mockResolvedValue([]);
    renderWithProviders(<GeographyPage />);

    expect(await screen.findByText('No deaneries found.')).toBeInTheDocument();
  });
});
