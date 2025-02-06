import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { Tournament } from '../Tournament/Tournament';

describe('Tournament', () => {
  it('starts tournament when button clicked', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        success: true,
        tournamentStatus: {
          currentMatch: 1,
          totalMatches: 6,
          matches: [
            {
              white: 'gpt4',
              black: 'claude',
              result: null
            }
          ],
          currentGame: {
            white: 'gpt4',
            black: 'claude'
          }
        }
      })
    });
    vi.stubGlobal('fetch', mockFetch);

    render(<Tournament gameType="chess" />);
    
    const startButton = screen.getByText('Start Round Robin Tournament');
    fireEvent.click(startButton);

    expect(startButton).toBeDisabled();
    const matchStatus = await screen.findByText('Match 1 of 6');
    expect(matchStatus).toBeInTheDocument();
    
    const currentMatch = await screen.findByText('Current Match');
    expect(currentMatch).toBeInTheDocument();
    
    const currentMatchDiv = screen.getByRole('heading', { name: 'Current Match' }).parentElement;
    expect(currentMatchDiv).toHaveTextContent('GPT-4');
    expect(currentMatchDiv).toHaveTextContent('vs');
    expect(currentMatchDiv).toHaveTextContent('CLAUDE');
    
    const matchCard = screen.getByTestId('match-card');
    expect(matchCard).toHaveTextContent('GPT-4');
    expect(matchCard).toHaveTextContent('vs');
    expect(matchCard).toHaveTextContent('CLAUDE');
    expect(matchCard).toHaveTextContent('Pending');
  });

  it('shows error state when tournament fails to start', async () => {
    const mockFetch = vi.fn().mockRejectedValue(new Error('Failed to start tournament'));
    vi.stubGlobal('fetch', mockFetch);

    render(<Tournament gameType="chess" />);
    
    const startButton = screen.getByText('Start Round Robin Tournament');
    await act(async () => {
      fireEvent.click(startButton);
    });

    expect(startButton).not.toBeDisabled();
  });
});
