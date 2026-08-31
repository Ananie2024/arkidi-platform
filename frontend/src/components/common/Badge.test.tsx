import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge } from './Badge';

describe('Badge', () => {
  it('renders its content with the neutral variant by default', () => {
    render(<Badge>BAPTIZED</Badge>);

    const badge = screen.getByText('BAPTIZED');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('bg-gray-100', 'text-gray-700');
  });

  it.each([
    ['success', 'bg-emerald-50'],
    ['warning', 'bg-amber-50'],
    ['error', 'bg-red-50'],
    ['info', 'bg-blue-50'],
  ] as const)('applies the %s variant classes', (variant, expectedClass) => {
    render(<Badge variant={variant}>{variant}</Badge>);

    expect(screen.getByText(variant)).toHaveClass(expectedClass);
  });
});
