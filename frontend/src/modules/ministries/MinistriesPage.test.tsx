import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { MinistriesPage } from './MinistriesPage';
import { domainApi } from '../../core/api/domain';
import { renderWithProviders } from '../../test/testUtils';
import { ministryFixture } from '../../test/fixtures';

vi.mock('../../core/api/domain', () => ({
  domainApi: {
    listMinistries: vi.fn(),
  },
}));

const mockedApi = vi.mocked(domainApi);

describe('MinistriesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders ministry rows with the active badge', async () => {
    mockedApi.listMinistries.mockResolvedValue([ministryFixture]);
    renderWithProviders(<MinistriesPage />);

    expect(
      await screen.findByRole('heading', { name: /pastoral ministries & lay apostolate/i })
    ).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('Chorale Sainte Cécile')).toBeInTheDocument();
    });
    expect(screen.getByText('CHOIR')).toBeInTheDocument();
    expect(screen.getByText('Kelly Irakoze')).toBeInTheDocument();
    expect(screen.getByText('Saturdays 15:00')).toBeInTheDocument();
    expect(screen.getByText('Active')).toBeInTheDocument();
  });

  it('renders the inactive badge for dormant ministries', async () => {
    mockedApi.listMinistries.mockResolvedValue([{ ...ministryFixture, is_active: false }]);
    renderWithProviders(<MinistriesPage />);

    await waitFor(() => {
      expect(screen.getByText('Inactive')).toBeInTheDocument();
    });
  });

  it('shows the API error empty message when the request fails', async () => {
    mockedApi.listMinistries.mockRejectedValue(new Error('boom'));
    renderWithProviders(<MinistriesPage />);

    expect(
      await screen.findByText(/unable to load ministries from the api/i)
    ).toBeInTheDocument();
  });
});
