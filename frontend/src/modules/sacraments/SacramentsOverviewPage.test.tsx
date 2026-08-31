import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { SacramentsOverviewPage } from './SacramentsOverviewPage';
import { renderWithProviders } from '../../test/testUtils';

// No API calls on this page — it is the canonical registers hub plus the
// QR certificate issuance flow. The modal stub honours `isOpen` so the open
// state transition is what gets asserted.
vi.mock('./CertificateGeneratorModal', () => ({
  CertificateGeneratorModal: ({ isOpen }: { isOpen: boolean }) =>
    isOpen ? <div data-testid="certificate-modal" /> : null,
}));

describe('SacramentsOverviewPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the register hub cards with their links', () => {
    renderWithProviders(<SacramentsOverviewPage />);

    expect(
      screen.getByRole('heading', { name: /canonical sacramental registers/i })
    ).toBeInTheDocument();
    const baptismCard = screen.getByText('Baptism Register').closest('a');
    expect(baptismCard).toHaveAttribute('href', '/sacraments/baptism');
    expect(screen.getByText('Confirmation Register').closest('a')).toHaveAttribute(
      'href',
      '/sacraments/confirmation'
    );
    expect(screen.getByText('Matrimony Register').closest('a')).toHaveAttribute(
      'href',
      '/sacraments/matrimony'
    );
    expect(screen.getByText("Registre des Baptêmes / Igitabo cya Batisimu")).toBeInTheDocument();
  });

  it('opens the QR certificate modal from the header button', () => {
    renderWithProviders(<SacramentsOverviewPage />);

    expect(screen.queryByTestId('certificate-modal')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /issue qr certificate/i }));
    expect(screen.getByTestId('certificate-modal')).toBeInTheDocument();
  });
});
