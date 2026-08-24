import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

// These are lightweight route/integration smoke tests: they render the *real*
// App inside jsdom and assert on the public Login page plus the
// unauthenticated redirect. All HTTP/API calls are made through axios to the
// jsdom default base URL, so AuthProvider simply stores no token and the
// ProtectedRoute bounces to /login. See also vitest.config.ts for the jsdom env.
describe('App routes', () => {
  it('renders the Login page at /login', async () => {
    window.history.pushState({}, '', '/login');
    render(<App />);

    expect(
      await screen.findByRole('heading', { name: /arkidi platform/i })
    ).toBeInTheDocument();
  });

  it('redirects an unauthenticated visitor from / to /login', async () => {
    window.history.pushState({}, '', '/dashboard');
    render(<App />);

    // AuthProvider fires a /auth/me call → 401 (no token) → redirect to /login.
    expect(
      await screen.findByRole('heading', { name: /arkidi platform/i })
    ).toBeInTheDocument();
    expect(window.location.pathname).toBe('/login');
  });
});