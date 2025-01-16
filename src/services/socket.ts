import io from 'socket.io-client';
import type { ChessGameState } from '../types/chess';
import type { LeaderboardEntry } from '../types/leaderboard';

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:5001';

interface SocketEvents {
  // Server -> Client events
  gameUpdate: (state: ChessGameState) => void;
  leaderboardUpdate: (data: LeaderboardEntry[]) => void;
  // Client -> Server events
  move: (data: { from: string; to: string; gameId: string }) => void;
  joinGame: (gameId: string) => void;
  leaveGame: () => void;
  getLeaderboard: () => void;
}

class GameSocket {
  socket: ReturnType<typeof io>;

  constructor() {
    this.socket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    });
  }

  joinGame(gameId: string) {
    this.socket.emit('joinGame', gameId);
  }

  leaveGame() {
    this.socket.emit('leaveGame');
  }

  onGameUpdate(callback: (state: ChessGameState) => void) {
    this.socket.on('gameUpdate', callback);
    return () => this.socket.off('gameUpdate', callback);
  }

  onLeaderboardUpdate(callback: (data: LeaderboardEntry[]) => void) {
    this.socket.on('leaderboardUpdate', callback);
    return () => this.socket.off('leaderboardUpdate', callback);
  }

  emit(event: keyof SocketEvents, data?: any) {
    this.socket.emit(event, data);
  }
}

export const gameSocket = new GameSocket();         