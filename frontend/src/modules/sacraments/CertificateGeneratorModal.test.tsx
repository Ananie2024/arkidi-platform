import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { CertificateGeneratorModal } from './CertificateGeneratorModal';
import { renderWithProviders } from '../../test/testUtils';

// Real modal (qrcode.react renders inline SVG, which jsdom supports) —
// exercises the two-step issuance flow end to end.
describe('CertificateGeneratorModal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders nothing while closed', () => {
    renderWithProviders(
      <CertificateGeneratorModal isOpen={false} onClose={() => {}} />
    );

    expect(screen.queryByText(/generate canonical sacramental certificate/i)).not.toBeInTheDocument();
  });

  it('renders the issuance form and generates a QR certificate token', () => {
    renderWithProviders(<CertificateGeneratorModal isOpen onClose={() => {}} />);

    expect(
      screen.getByText(/generate canonical sacramental certificate/i)
    ).toBeInTheDocument();
    expect(screen.getByText(/certificate of baptism/i)).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText('PAR-STF-2026-001'), {
      target: { value: 'PAR-STF-2026-001' },
    });
    fireEvent.click(screen.getByRole('button', { name: /generate certificate & qr code/i }));

    expect(screen.getByText('CERT-BAP-2026-98124FA')).toBeInTheDocument();
    expect(screen.getByText(/qr verification code generated/i)).toBeInTheDocument();
  });

  it('calls onClose when Cancel is pressed', () => {
    const onClose = vi.fn();
    renderWithProviders(<CertificateGeneratorModal isOpen onClose={onClose} />);

    fireEvent.click(screen.getByRole('button', { name: 'Cancel' }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
