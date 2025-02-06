import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import gameReducer from '../../store/gameSlice';
import Leaderboard from '../Leaderboard/Leaderboard';

describe('Leaderboard', () => {
  const mockLeaderboard = [
    { player: 'GPT-4', score: 10 },
    { player: 'CLAUDE', score: 8 },
    { player: 'GEMINI', score: 6 }
  ];

  it('displays leaderboard entries in correct order', () => {
    const store = configureStore({
      reducer: { game: gameReducer }
    });
    render(
      <Provider store={store}>
        <Leaderboard leaderboard={mockLeaderboard} gameType="chess" />
      </Provider>
    );
    
    const rows = screen.getAllByRole('row');
    expect(rows).toHaveLength(4); // header + 3 players
    
    const firstPlace = rows[1];
    expect(firstPlace).toHaveTextContent('GPT-4');
    expect(firstPlace).toHaveTextContent('10');
  });

  it('shows loading state when no data', () => {
    const store = configureStore({
      reducer: { game: gameReducer }
    });
    render(
      <Provider store={store}>
        <Leaderboard leaderboard={[]} gameType="chess" />
      </Provider>
    );
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });
});
