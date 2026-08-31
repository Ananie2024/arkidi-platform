import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { LiturgyPage } from './LiturgyPage';
import { domainApi } from '../../core/api/domain';
import { renderWithProviders } from '../../test/testUtils';
import { parishFixture, massScheduleFixture } from '../../test/fixtures';

vi.mock('../../core/api/domain', () => ({
  domainApi: {
    listParishes: vi.fn(),
    listMassSchedules: vi.fn(),
  },
}));

const mockedApi = vi.mocked(domainApi);

describe('LiturgyPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the mass schedule for the first parish', async () => {
    mockedApi.listParishes.mockResolvedValue([parishFixture]);
    mockedApi.listMassSchedules.mockResolvedValue([massScheduleFixture]);
    renderWithProviders(<LiturgyPage />);

    expect(
      await screen.findByRole('heading', { name: /mass schedules & intentions/i })
    ).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('2026-03-08')).toBeInTheDocument();
    });
    expect(screen.getByText('09:30')).toBeInTheDocument();
    expect(screen.getByText('KINYARWANDA')).toBeInTheDocument();
    expect(screen.getByText('Abbé Uwimana')).toBeInTheDocument();
    expect(screen.getByText('Second Sunday of Lent')).toBeInTheDocument();
    expect(mockedApi.listMassSchedules).toHaveBeenCalledWith('parish-1');
  });

  it('does not query mass schedules until a parish is known', async () => {
    mockedApi.listParishes.mockResolvedValue([]);
    renderWithProviders(<LiturgyPage />);

    expect(
      await screen.findByText('No mass schedules found for the current parish.')
    ).toBeInTheDocument();
    expect(mockedApi.listMassSchedules).not.toHaveBeenCalled();
  });

  it('shows the API error empty message when the request fails', async () => {
    mockedApi.listParishes.mockRejectedValue(new Error('boom'));
    renderWithProviders(<LiturgyPage />);

    expect(
      await screen.findByText(/unable to load mass schedules from the api/i)
    ).toBeInTheDocument();
  });
});
