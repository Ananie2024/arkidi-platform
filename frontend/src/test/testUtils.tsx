import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

/**
 * Shared test helpers for API-backed page/component tests.
 *
 * Pages fetch through React Query against the mocked `domainApi`, so every
 * test needs a fresh QueryClient (no cross-test cache bleed) and — for
 * pages that read route params — a MemoryRouter with the matching pattern.
 */

export function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0, staleTime: 0 },
      mutations: { retry: false },
    },
  });
}

interface RenderWithProvidersOptions extends Omit<RenderOptions, 'wrapper'> {
  /** Initial history entry, e.g. '/geography/parishes/p-1'. */
  route?: string;
  /** When set, the UI is mounted on this route pattern (enables useParams). */
  path?: string;
}

export function renderWithProviders(
  ui: React.ReactElement,
  { route = '/', path, ...options }: RenderWithProvidersOptions = {}
) {
  const queryClient = createTestQueryClient();

  return render(ui, {
    wrapper: ({ children }) => (
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[route]}>
          {path ? (
            <Routes>
              <Route path={path} element={children} />
            </Routes>
          ) : (
            children
          )}
        </MemoryRouter>
      </QueryClientProvider>
    ),
    ...options,
  });
}
