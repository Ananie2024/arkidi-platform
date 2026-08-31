import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { BaptismRegisterPage } from './BaptismRegisterPage';
import { renderWithProviders } from '../../test/testUtils';

// The baptism register has no list endpoint wired yet — the page renders the
// canonical column layout with an explicit "endpoint pending" empty state.
describe('BaptismRegisterPage', () => {
  it('renders the register heading and canonical columns', () => {
    renderWithProviders(<BaptismRegisterPage />);

    expect(
      screen.getByRole('heading', { name: /baptism canonical register/i })
    ).toBeInTheDocument();
    expect(screen.getByText(/registre des baptêmes/i)).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: 'Act #' })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: 'Book / Vol' })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: 'Minister / Priest' })).toBeInTheDocument();
    expect(screen.getByText('Record Baptism')).toBeInTheDocument();
  });

  it('shows the pending-endpoint empty state', () => {
    renderWithProviders(<BaptismRegisterPage />);

    expect(screen.getByText(/no register list endpoint is available yet/i)).toBeInTheDocument();
  });
});
