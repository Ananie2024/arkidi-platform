import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { ArchivePage } from './ArchivePage';
import { domainApi } from '../../core/api/domain';
import { renderWithProviders } from '../../test/testUtils';
import { parishFixture, archiveBookFixture } from '../../test/fixtures';

vi.mock('../../core/api/domain', () => ({
  domainApi: {
    listParishes: vi.fn(),
    listArchiveBooks: vi.fn(),
  },
}));

const mockedApi = vi.mocked(domainApi);

describe('ArchivePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the digital archive heading and ledger book rows', async () => {
    mockedApi.listParishes.mockResolvedValue([parishFixture]);
    mockedApi.listArchiveBooks.mockResolvedValue([archiveBookFixture]);
    renderWithProviders(<ArchivePage />);

    expect(
      await screen.findByRole('heading', { name: /digital archive & historic registers/i })
    ).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('Registre des Baptêmes 1920-1935')).toBeInTheDocument();
    });
    expect(screen.getByText('BAPTISM')).toBeInTheDocument();
    expect(screen.getByText('I')).toBeInTheDocument();
    expect(screen.getByText('1920 - 1935')).toBeInTheDocument();
    expect(screen.getByText('Salle A / Étagère 3')).toBeInTheDocument();
    expect(mockedApi.listArchiveBooks).toHaveBeenCalledWith('parish-1');
  });

  it('does not query ledger books until a parish is known', async () => {
    mockedApi.listParishes.mockResolvedValue([]);
    renderWithProviders(<ArchivePage />);

    expect(
      await screen.findByText('No archive books found for the current parish.')
    ).toBeInTheDocument();
    expect(mockedApi.listArchiveBooks).not.toHaveBeenCalled();
  });

  it('shows the API error empty message when the request fails', async () => {
    mockedApi.listParishes.mockRejectedValue(new Error('boom'));
    renderWithProviders(<ArchivePage />);

    expect(
      await screen.findByText(/unable to load archive books from the api/i)
    ).toBeInTheDocument();
  });
});
