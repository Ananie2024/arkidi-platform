import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { DashboardPage } from './DashboardPage';
import { domainApi } from '../../core/api/domain';
import { renderWithProviders } from '../../test/testUtils';
import { annuarioFixture, parishFixture, landParcelFixture } from '../../test/fixtures';

// Leaflet cannot render inside jsdom — stub the GIS map so the dashboard's
// query/marker pipeline is what gets exercised.
vi.mock('../../components/map/GisMapViewer', () => ({
  GisMapViewer: () => <div data-testid="gis-map-viewer" />,
}));

vi.mock('../../core/api/domain', () => ({
  domainApi: {
    getAnnuarioPontificio: vi.fn(),
    listParishes: vi.fn(),
    listParcels: vi.fn(),
  },
}));

const mockedApi = vi.mocked(domainApi);

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the KPI cards and quick actions from the API data', async () => {
    mockedApi.getAnnuarioPontificio.mockResolvedValue(annuarioFixture);
    mockedApi.listParishes.mockResolvedValue([parishFixture]);
    mockedApi.listParcels.mockResolvedValue([landParcelFixture]);
    renderWithProviders(<DashboardPage />);

    expect(await screen.findByRole('heading', { name: /arkidi platform/i })).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('Total Faithful')).toBeInTheDocument();
    });
    expect(screen.getByText('480,000')).toBeInTheDocument();
    expect(screen.getByText('3,100')).toBeInTheDocument();
    expect(screen.getByText('142')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument(); // parcel count
    expect(screen.getByText('Archdiocesan GIS Parish & Property Map')).toBeInTheDocument();
    expect(screen.getByTestId('gis-map-viewer')).toBeInTheDocument();
    expect(screen.getByText('Record New Baptism')).toBeInTheDocument();
    expect(screen.getByText('Annuario Pontificio Extracts')).toBeInTheDocument();
  });

  it('shows em-dash placeholders while the annuario query is loading', async () => {
    mockedApi.getAnnuarioPontificio.mockReturnValue(new Promise(() => {}));
    mockedApi.listParishes.mockResolvedValue([parishFixture]);
    mockedApi.listParcels.mockResolvedValue([]);
    renderWithProviders(<DashboardPage />);

    const emDashes = await screen.findAllByText('—');
    expect(emDashes.length).toBeGreaterThanOrEqual(3);
    expect(screen.getByText(/loading parish locations/i)).toBeInTheDocument();
  });
});
