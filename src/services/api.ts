import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

export interface GameMove {
  from: string;
  to: string;
  piece?: string;
}

export interface GameState {
  board: string[][];
  currentPlayer: string;
  moves: GameMove[];
  status: 'active' | 'finished';
  winner?: string;
}

export const gameService = {
  async startGame(gameType: 'chess' | 'go', player1: string, player2: string): Promise<string> {
    const { data } = await api.post('/game/start', { gameType, player1, player2 });
    return data.gameId;
  },

  async getGameState(gameId: string): Promise<GameState> {
    const { data } = await api.get(`/game/${gameId}`);
    return data;
  },

  async makeMove(gameId: string, move: GameMove): Promise<GameState> {
    const { data } = await api.post(`/game/${gameId}/move`, move);
    return data;
  },

  async getLeaderboard(gameType: 'chess' | 'go'): Promise<any[]> {
    const { data } = await api.get(`/leaderboard/${gameType}`);
    return data;
  },
}; 