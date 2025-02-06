import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import gameReducer from '../../store/gameSlice';
import App from '../../App';
import '@testing-library/jest-dom';

const store = configureStore({
  reducer: { game: gameReducer }
});

describe('App', () => {
  it('switches between chess and go boards', () => {
    render(
      <Provider store={store}>
        <App />
      </Provider>
    );

    // Initially shows chess board
    expect(screen.getByText('Select players and press Start Game to begin')).toBeInTheDocument();

    // Switch to Go
    const goButton = screen.getByText('Go');
    fireEvent.click(goButton);
    expect(screen.getByText('Select players and press Start Game to begin')).toBeInTheDocument();

    // Switch back to Chess
    const chessButton = screen.getByText('Chess');
    fireEvent.click(chessButton);
    expect(screen.getByText('Select players and press Start Game to begin')).toBeInTheDocument();
  });
});
