import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { StatisticsPage } from './StatisticsPage';
import { domainApi } from '../../core/api/domain';
import { renderWithProviders } from '../../test/testUtils';
import { annualReportFixture, annuarioFixture } from '../../test/fixtures';

vi.mock('../../core/api/domain', () => ({
  domainApi: {
    listAnnualReports: vi.fn(),
    getAnnuarioPontificio: vi.fn(),
  },
}));

const mockedApi = vi.mocked(domainApi);

describe('StatisticsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the Annuario KPI cards and parish report rows', async () => {
    mockedApi.getAnnuarioPontificio.mockResolvedValue(annuarioFixture);
    mockedApi.listAnnualReports.mockResolvedValue([annualReportFixture]);
    renderWithProviders(<StatisticsPage />);

    expect(
      await screen.findByRole('heading', { name: /pontifical statistics & reporting/i })
    ).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('27')).toBeInTheDocument();
    });
    expect(screen.getByText('142')).toBeInTheDocument();
    expect(screen.getByText('480,000')).toBeInTheDocument();
    // 61 infant + 9 adult baptisms aggregated by the page
    expect(screen.getByText(70)).toBeInTheDocument();
    expect(screen.getByText(44)).toBeInTheDocument();
    expect(screen.getByText('parish-1')).toBeInTheDocument();
    // Both queries are issued for the current year.
    const currentYear = new Date().getFullYear();
    expect(mockedApi.listAnnualReports).toHaveBeenCalledWith(currentYear);
    expect(mockedApi.getAnnuarioPontificio).toHaveBeenCalledWith(currentYear);
  });

  it('shows placeholder dashes while the annuario has not loaded', async () => {
    mockedApi.getAnnuarioPontificio.mockResolvedValue(annuarioFixture);
    mockedApi.listAnnualReports.mockResolvedValue([]);
    renderWithProviders(<StatisticsPage />);

    expect(
      await screen.findByText(/no parish reports found for/i)
    ).toBeInTheDocument();
  });

  it('shows the API error empty message when the request fails', async () => {
    mockedApi.getAnnuarioPontificio.mockRejectedValue(new Error('boom'));
    mockedApi.listAnnualReports.mockRejectedValue(new Error('boom'));
    renderWithProviders(<StatisticsPage />);

    expect(
      await screen.findByText(/unable to load statistics from the api/i)
    ).toBeInTheDocument();
  });
});
