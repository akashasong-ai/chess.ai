import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { StatusBar } from '../StatusBar/StatusBar';
import '@testing-library/jest-dom';

describe('StatusBar', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('displays error message when provided', () => {
    render(<StatusBar error="Test error message" />);
    expect(screen.getByText('Test error message')).toBeInTheDocument();
  });

  it('rotates through status messages when no error', () => {
    render(<StatusBar />);
    
    const initialMessage = screen.getByText(/AI players analyzing positions/);
    expect(initialMessage).toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(5000);
    });

    const nextMessage = screen.getByText(/Calculating optimal moves/);
    expect(nextMessage).toBeInTheDocument();
  });
});
