import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || window.location.origin;

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  withCredentials: false
});

export type GameType = 'chess' | 'go';
export type GameStatus = 'active' | 'finished';

export interface GameMove {
  from: string;
  to: string;
  piece?: string;
}

export interface GameState {
  board: string[][] | Record<string, any> | number[][];
  currentPlayer: string;
  moves?: GameMove[];
  status: GameStatus;
  winner?: string;
}

export const gameService = {
  async startGame(_gameType: GameType, player1: string, player2: string): Promise<string> {
    const { data } = await api.post<{ success: boolean; gameId?: string }>('/api/game/start', {
      whiteAI: player1,
      blackAI: player2
    });
    if (!data.success || !data.gameId) {
      throw new Error('Failed to start game');
    }
    return data.gameId;
  },

  async getGameState(_gameId: string): Promise<GameState> {
    const { data } = await api.get<GameState>('/api/game/state');
    return data;
  },

  async makeMove(gameId: string, move: GameMove): Promise<GameState> {
    const { data } = await api.post<GameState>('/api/game/move', { gameId, move });
    return data;
  },

  async getLeaderboard(_gameType: GameType): Promise<Array<{ player: string; score: number }>> {
    const { data } = await api.get<Array<{ player: string; score: number }>>('/api/leaderboard');
    return data;
  },
};                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        