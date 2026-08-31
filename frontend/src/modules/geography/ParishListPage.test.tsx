import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { ParishListPage } from './ParishListPage';
import { domainApi } from '../../core/api/domain';
import { renderWithProviders } from '../../test/testUtils';
import { parishFixture } from '../../test/fixtures';

vi.mock('../../core/api/domain', () => ({
  domainApi: {
    listParishes: vi.fn(),
  },
}));

const mockedApi = vi.mocked(domainApi);

describe('ParishListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders parish rows returned by the API', async () => {
    mockedApi.listParishes.mockResolvedValue([parishFixture]);
    renderWithProviders(<ParishListPage />);

    await waitFor(() => {
      expect(screen.getByText('Sainte Famille Parish')).toBeInTheDocument();
    });
    expect(screen.getByText('PAR-SF-01')).toBeInTheDocument();
    expect(screen.getByText('Holy Family')).toBeInTheDocument();
    expect(screen.getByText('Nyarugenge')).toBeInTheDocument();
    expect(screen.getByText('Open Parish Details')).toHaveAttribute(
      'href',
      '/geography/parishes/parish-1'
    );
  });

  it('passes the deanery query param through to the API', async () => {
    mockedApi.listParishes.mockResolvedValue([]);
    renderWithProviders(<ParishListPage />, {
      route: '/geography/parishes?deanery=deanery-9',
    });

    await waitFor(() => {
      expect(mockedApi.listParishes).toHaveBeenCalledWith('deanery-9');
    });
    expect(await screen.findByText('No parishes found.')).toBeInTheDocument();
  });

  it('shows the API error empty message when the request fails', async () => {
    mockedApi.listParishes.mockRejectedValue(new Error('boom'));
    renderWithProviders(<ParishListPage />);

    expect(
      await screen.findByText(/unable to load parishes from the api/i)
    ).toBeInTheDocument();
  });
});
