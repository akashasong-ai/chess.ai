import io from 'socket.io-client';
import type { ChessGameState } from '../types/chess';
import type { GoGameState, GoGameUpdate } from '../types/go';
import type { LeaderboardEntry } from '../types/leaderboard';

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'https://go-board-app-tunnel-mp5ybwn7.devinapps.com';

type GameState = ChessGameState | GoGameState;

interface SocketEvents {
  // Server -> Client events
  gameUpdate: (state: GameState) => void;
  leaderboardUpdate: (data: LeaderboardEntry[]) => void;
  // Client -> Server events
  move: (data: { from?: string; to?: string; x?: number; y?: number; gameId: string }) => void;
  joinGame: (gameId: string) => void;
  leaveGame: () => void;
  getLeaderboard: () => void;
}

class GameSocket {
  socket: ReturnType<typeof io>;

  constructor() {
    console.log('Initializing socket connection to:', SOCKET_URL);
    this.socket = io(SOCKET_URL, {
      transports: ['polling', 'websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      path: '/socket.io/',
      auth: {
        credentials: 'omit'
      },
      autoConnect: true,
      timeout: 20000
    });

    // Add connection event handlers
    this.socket.on('connect', () => {
      console.log('Connected to game server');
    });

    this.socket.on('connect_error', (error: Error) => {
      console.error('Connection error:', error);
    });

    this.socket.on('disconnect', (reason: string) => {
      console.log('Disconnected:', reason);
    });
  }

  joinGame(gameId: string) {
    this.socket.emit('joinGame', gameId);
  }

  leaveGame() {
    this.socket.emit('leaveGame');
  }

  onGameUpdate<T extends ChessGameState | GoGameUpdate>(callback: (state: T) => void) {
    this.socket.on('gameUpdate', callback as (state: any) => void);
    return () => this.socket.off('gameUpdate', callback as (state: any) => void);
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
