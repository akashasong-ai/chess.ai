import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface GameState {
  currentGame: 'chess' | 'go';
  player1: string;
  player2: string;
  error: string | null;
  isLoading: boolean;
}

const initialState: GameState = {
  currentGame: 'chess',
  player1: '',
  player2: '',
  error: null,
  isLoading: false
};

const gameSlice = createSlice({
  name: 'game',
  initialState,
  reducers: {
    setGameType: (state, action: PayloadAction<'chess' | 'go'>) => {
      state.currentGame = action.payload;
    },
    setPlayers: (state, action: PayloadAction<{ player1: string; player2: string }>) => {
      state.player1 = action.payload.player1;
      state.player2 = action.payload.player2;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    }
  }
});

export const { setGameType, setPlayers, setError, setLoading } = gameSlice.actions;
export default gameSlice.reducer;
