import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor, fireEvent } from '@testing-library/react';
import { LandAssetsPage } from './LandAssetsPage';
import { domainApi } from '../../core/api/domain';
import { renderWithProviders } from '../../test/testUtils';
import { landParcelFixture } from '../../test/fixtures';

// Leaflet/MapContainer is not meaningfully testable inside jsdom — stub the
// GIS viewer so the page's data pipeline is what gets exercised.
vi.mock('../../components/map/GisMapViewer', () => ({
  GisMapViewer: () => <div data-testid="gis-map-viewer" />,
  LAND_USE_COLORS: {},
}));

vi.mock('../../core/api/domain', () => ({
  domainApi: {
    listParcels: vi.fn(),
    listParishes: vi.fn().mockResolvedValue([]),
    listParcelBuildings: vi.fn().mockResolvedValue([]),
  },
}));

const mockedApi = vi.mocked(domainApi);

describe('LandAssetsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the GIS card and parcel registry rows', async () => {
    mockedApi.listParcels.mockResolvedValue([landParcelFixture]);
    renderWithProviders(<LandAssetsPage />);

    expect(
      await screen.findByRole('heading', { name: /land intelligence & real estate gis/i })
    ).toBeInTheDocument();
    expect(screen.getByTestId('gis-map-viewer')).toBeInTheDocument();
    expect(screen.getByText('Archdiocesan Land Parcels (Spatial View)')).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('1/02/07/02/1234')).toBeInTheDocument();
    });
    expect(screen.getByText('Paroisse Sainte Famille Compound')).toBeInTheDocument();
    expect(screen.getByText('CHURCH_COMPOUND')).toBeInTheDocument();
    expect(screen.getByText('Nyarugenge / Nyamirambo')).toBeInTheDocument();
    expect(screen.getAllByText('12,450.5').length).toBeGreaterThanOrEqual(1);
  });

  it('shows the API error empty message when the request fails', async () => {
    mockedApi.listParcels.mockRejectedValue(new Error('boom'));
    renderWithProviders(<LandAssetsPage />);

    expect(
      await screen.findByText(/unable to load parcels from the api/i)
    ).toBeInTheDocument();
  });

  it('opens the registration modal when clicking Register Parcel button', async () => {
    mockedApi.listParcels.mockResolvedValue([landParcelFixture]);
    renderWithProviders(<LandAssetsPage />);

    const registerBtn = await screen.findByRole('button', { name: /register parcel/i });
    fireEvent.click(registerBtn);

    expect(await screen.findByText(/upi/i)).toBeInTheDocument();
  });


  it('opens the detail modal when clicking view action button', async () => {
    mockedApi.listParcels.mockResolvedValue([landParcelFixture]);
    renderWithProviders(<LandAssetsPage />);

    const viewBtn = await screen.findByRole('button', { name: /view paroisse sainte famille compound/i });
    fireEvent.click(viewBtn);

    expect(await screen.findByText(/parcel dossier: paroisse sainte famille compound/i)).toBeInTheDocument();
  });
});


