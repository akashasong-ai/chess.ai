import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

export type GameType = 'chess' | 'go';
export type GameStatus = 'active' | 'finished';

export interface GameMove {
  from: string;
  to: string;
  piece?: string;
}

export interface GameState {
  board: string[][];
  currentPlayer: string;
  moves: GameMove[];
  status: GameStatus;
  winner?: string;
}

export const gameService = {
  async startGame(gameType: GameType, player1: string, player2: string): Promise<string> {
    const { data } = await api.post<{ gameId: string }>('/game/start', { gameType, player1, player2 });
    return data.gameId;
  },

  async getGameState(gameId: string): Promise<GameState> {
    const { data } = await api.get<GameState>(`/game/${gameId}`);
    return data;
  },

  async makeMove(gameId: string, move: GameMove): Promise<GameState> {
    const { data } = await api.post<GameState>(`/game/${gameId}/move`, move);
    return data;
  },

  async getLeaderboard(gameType: GameType): Promise<Array<{ player: string; score: number }>> {
    const { data } = await api.get<Array<{ player: string; score: number }>>(`/leaderboard/${gameType}`);
    return data;
  },
}; 