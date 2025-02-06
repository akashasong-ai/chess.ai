import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Tournament } from '../Tournament/Tournament';

describe('Tournament', () => {
  it('starts tournament when button clicked', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        matches: [
          {
            id: '1',
            player1: 'gpt4',
            player2: 'claude',
            status: 'pending'
          }
        ]
      })
    });
    vi.stubGlobal('fetch', mockFetch);

    render(<Tournament gameType="chess" />);
    
    const startButton = screen.getByText('Start Round Robin Tournament');
    fireEvent.click(startButton);

    expect(startButton).toBeDisabled();
    expect(await screen.findByText('GPT-4')).toBeInTheDocument();
    expect(await screen.findByText('CLAUDE')).toBeInTheDocument();
  });

  it('shows error state when tournament fails to start', async () => {
    const mockFetch = vi.fn().mockRejectedValue(new Error('Failed to start tournament'));
    vi.stubGlobal('fetch', mockFetch);

    render(<Tournament gameType="chess" />);
    
    const startButton = screen.getByText('Start Round Robin Tournament');
    fireEvent.click(startButton);

    expect(startButton).not.toBeDisabled();
  });
});
