import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Pagination } from './Pagination';

describe('Pagination', () => {
  it('renders nothing when there is only one page', () => {
    const { container } = render(
      <Pagination currentPage={1} totalPages={1} onPageChange={() => {}} />
    );

    expect(container).toBeEmptyDOMElement();
  });

  it('renders the page indicator and navigation buttons', () => {
    render(<Pagination currentPage={2} totalPages={5} onPageChange={() => {}} />);

    // "Page 2 of 5" is rendered as a single interpolated i18n string.
    expect(screen.getByText('Page 2 of 5')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /previous/i })).toBeEnabled();
    expect(screen.getByRole('button', { name: /next/i })).toBeEnabled();
  });

  it('navigates to the requested page', () => {
    const onPageChange = vi.fn();
    render(<Pagination currentPage={2} totalPages={5} onPageChange={onPageChange} />);

    fireEvent.click(screen.getByRole('button', { name: /previous/i }));
    expect(onPageChange).toHaveBeenLastCalledWith(1);
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    expect(onPageChange).toHaveBeenLastCalledWith(3);
    expect(onPageChange).toHaveBeenCalledTimes(2);
  });

  it('disables Previous on the first page and Next on the last page', () => {
    const onPageChange = vi.fn();

    const { rerender } = render(
      <Pagination currentPage={1} totalPages={5} onPageChange={onPageChange} />
    );
    expect(screen.getByRole('button', { name: /previous/i })).toBeDisabled();

    rerender(
      <Pagination currentPage={5} totalPages={5} onPageChange={onPageChange} />
    );
    expect(screen.getByRole('button', { name: /next/i })).toBeDisabled();
  });
});
