import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, within } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import gameReducer from '../../store/gameSlice';
import GameTypeSelect from '../GameControls/GameTypeSelect';
import PlayerSelect from '../GameControls/PlayerSelect';

const store = configureStore({
  reducer: { game: gameReducer }
});

const renderWithProvider = (ui: React.ReactElement) => {
  return render(
    <Provider store={store}>
      {ui}
    </Provider>
  );
};

describe('GameTypeSelect', () => {
  it('switches between chess and go', () => {
    const onSelect = vi.fn();
    renderWithProvider(<GameTypeSelect onSelect={onSelect} />);

    const goButton = screen.getByText('Go');
    fireEvent.click(goButton);
    expect(onSelect).toHaveBeenCalledWith('go');

    const chessButton = screen.getByText('Chess');
    fireEvent.click(chessButton);
    expect(onSelect).toHaveBeenCalledWith('chess');
  });
});

describe('PlayerSelect', () => {
  it('prevents selecting same AI for both players in both directions', () => {
    const onSelectPlayer1 = vi.fn();
    const onSelectPlayer2 = vi.fn();
    
    const { rerender } = renderWithProvider(
      <PlayerSelect
        gameType="chess"
        onSelectPlayer1={onSelectPlayer1}
        onSelectPlayer2={onSelectPlayer2}
        selectedPlayer1="gpt4"
        selectedPlayer2=""
      />
    );

    // Check Player 2 can't select GPT-4
    const player2Select = screen.getByRole('combobox', { name: 'Player 2 (Black)' });
    const gpt4OptionInPlayer2 = within(player2Select).getByRole('option', { name: 'GPT-4' });
    expect(gpt4OptionInPlayer2).toBeDisabled();

    // Check Player 1 can't select CLAUDE when Player 2 has it
    rerender(
      <PlayerSelect
        gameType="chess"
        onSelectPlayer1={onSelectPlayer1}
        onSelectPlayer2={onSelectPlayer2}
        selectedPlayer1=""
        selectedPlayer2="claude"
      />
    );

    const player1Select = screen.getByRole('combobox', { name: 'Player 1 (White)' });
    const claudeOptionInPlayer1 = within(player1Select).getByRole('option', { name: 'CLAUDE' });
    expect(claudeOptionInPlayer1).toBeDisabled();
  });

  it('shows correct player colors based on game type', () => {
    const { rerender } = render(
      <PlayerSelect
        gameType="chess"
        onSelectPlayer1={() => {}}
        onSelectPlayer2={() => {}}
        selectedPlayer1=""
        selectedPlayer2=""
      />
    );

    expect(screen.getByText('Player 1 (White)')).toBeInTheDocument();
    expect(screen.getByText('Player 2 (Black)')).toBeInTheDocument();

    rerender(
      <PlayerSelect
        gameType="go"
        onSelectPlayer1={() => {}}
        onSelectPlayer2={() => {}}
        selectedPlayer1=""
        selectedPlayer2=""
      />
    );

    expect(screen.getByText('Player 1 (Black)')).toBeInTheDocument();
    expect(screen.getByText('Player 2 (White)')).toBeInTheDocument();
  });
});
