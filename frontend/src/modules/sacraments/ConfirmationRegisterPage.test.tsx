import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { ConfirmationRegisterPage } from './ConfirmationRegisterPage';
import { renderWithProviders } from '../../test/testUtils';

// The confirmation register has no list endpoint wired yet — the page renders
// the canonical column layout with an explicit "endpoint pending" empty state.
describe('ConfirmationRegisterPage', () => {
  it('renders the register heading and canonical columns', () => {
    renderWithProviders(<ConfirmationRegisterPage />);

    expect(
      screen.getByRole('heading', { name: /confirmation register/i })
    ).toBeInTheDocument();
    expect(screen.getByText(/records of the sacrament of confirmation/i)).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: 'Act #' })).toBeInTheDocument();
    expect(
      screen.getByRole('columnheader', { name: /administering bishop \/ vicar/i })
    ).toBeInTheDocument();
    expect(screen.getByText('Record Confirmation')).toBeInTheDocument();
  });

  it('shows the pending-endpoint empty state', () => {
    renderWithProviders(<ConfirmationRegisterPage />);

    expect(screen.getByText(/no register list endpoint is available yet/i)).toBeInTheDocument();
  });
});
