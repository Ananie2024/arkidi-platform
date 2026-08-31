import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { MatrimonyRegisterPage } from './MatrimonyRegisterPage';
import { renderWithProviders } from '../../test/testUtils';

// The matrimony register has no list endpoint wired yet — the page renders the
// canonical column layout with an explicit "endpoint pending" empty state.
describe('MatrimonyRegisterPage', () => {
  it('renders the register heading and canonical columns', () => {
    renderWithProviders(<MatrimonyRegisterPage />);

    expect(
      screen.getByRole('heading', { name: /canonical marriage register/i })
    ).toBeInTheDocument();
    expect(screen.getByText(/canonical witnesses/i)).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /groom \(umugabo\)/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /bride \(umugore\)/i })).toBeInTheDocument();
    expect(screen.getByText('Record Marriage')).toBeInTheDocument();
  });

  it('shows the pending-endpoint empty state', () => {
    renderWithProviders(<MatrimonyRegisterPage />);

    expect(screen.getByText(/no register list endpoint is available yet/i)).toBeInTheDocument();
  });
});
