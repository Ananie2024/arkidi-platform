import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import { FaithfulDetailPage } from './FaithfulDetailPage';
import { domainApi } from '../../core/api/domain';
import { renderWithProviders } from '../../test/testUtils';
import { faithfulFixture } from '../../test/fixtures';

vi.mock('../../core/api/domain', () => ({
  domainApi: {
    getFaithful: vi.fn(),
  },
}));

const mockedApi = vi.mocked(domainApi);

function renderDetail() {
  return renderWithProviders(<FaithfulDetailPage />, {
    route: `/faithful/${faithfulFixture.id}`,
    path: '/faithful/:faithfulId',
  });
}

describe('FaithfulDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the faithful record from the API payload', async () => {
    mockedApi.getFaithful.mockResolvedValue(faithfulFixture);
    renderDetail();

    expect(
      await screen.findByRole('heading', { name: /mukamana alice/i })
    ).toBeInTheDocument();
    expect(screen.getByText('Registration Number: REG-2026-0001')).toBeInTheDocument();
    expect(screen.getByText('Personal & Contact Details')).toBeInTheDocument();
    expect(screen.getByText('Parish Registration')).toBeInTheDocument();
    expect(screen.getByText('Canonical Status')).toBeInTheDocument();
    expect(screen.getByText('Status: CONFIRMED')).toBeInTheDocument();
    expect(mockedApi.getFaithful).toHaveBeenCalledWith(faithfulFixture.id);
  });

  it('shows the API error message when the record cannot be loaded', async () => {
    mockedApi.getFaithful.mockRejectedValue(new Error('boom'));
    renderDetail();

    expect(
      await screen.findByText(/unable to load the faithful record from the api/i)
    ).toBeInTheDocument();
  });
});
