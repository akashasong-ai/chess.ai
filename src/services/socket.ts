import io from 'socket.io-client';
import type { ChessGameState } from '../types/chess';
import type { GoGameState, GoGameUpdate } from '../types/go';
import type { LeaderboardEntry } from '../types/leaderboard';

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:5000';
console.log('Using WebSocket URL:', SOCKET_URL);

// Configure Socket.IO to use WebSocket transport
const socketOptions = {
  transports: ['polling', 'websocket'],  // Try polling first, then upgrade
  path: '/socket.io',
  secure: true,
  rejectUnauthorized: false,
  withCredentials: true,
  timeout: 20000,  // Increase timeout for connection upgrade
  autoConnect: false  // Manual connection control
};

type GameState = ChessGameState | GoGameState;

interface TournamentStatus {
  currentMatch: number;
  totalMatches: number;
  matches: Array<{
    white: string;
    black: string;
    result: string | null;
  }>;
  currentGame: {
    white: string;
    black: string;
  };
}

interface SocketEvents {
  // Server -> Client events
  gameUpdate: (state: GameState) => void;
  leaderboardUpdate: (data: LeaderboardEntry[]) => void;
  tournamentUpdate: (data: TournamentStatus) => void;
  validMoves: (moves: string[]) => void;
  connectionStatus: (status: 'connected' | 'connecting' | 'disconnected') => void;
  error: (data: { message: string }) => void;
  // Client -> Server events
  'move': (data: { from?: string; to?: string; x?: number; y?: number; gameId: string }) => void;
  'getValidMoves': (data: { position: string; gameId: string }) => void;
  'joinGame': (gameId: string) => void;
  leaveGame: () => void;
  getLeaderboard: () => void;
}

interface SocketEvents {
  error: (data: { message: string }) => void;
}

class GameSocket {
  socket: ReturnType<typeof io>;

  constructor() {
    console.log('Initializing socket connection to:', SOCKET_URL);
    this.socket = io(SOCKET_URL, {
      ...socketOptions,
      reconnection: true,
      reconnectionAttempts: 3,
      reconnectionDelay: 2000,
      reconnectionDelayMax: 10000
    });

    // Try polling first
    if (this.socket.io?.opts) {
      this.socket.io.opts.transports = ['polling'];
    }
    
    this.socket.on('connect', () => {
      console.log('Connected to game server');
      // Upgrade to WebSocket after successful polling connection
      if (this.socket.io?.opts?.transports && !this.socket.io.opts.transports.includes('websocket')) {
        this.socket.io.opts.transports = ['polling', 'websocket'];
      }
      this.emit('connectionStatus', 'connected');
    });

    this.socket.on('connect_error', (error: Error) => {
      console.error('Connection error:', error);
      this.emit('connectionStatus', 'disconnected');
      
      // If WebSocket fails, fall back to polling only
      if (this.socket.io?.opts?.transports?.includes('websocket')) {
        console.log('WebSocket connection failed, falling back to polling');
        this.socket.io.opts.transports = ['polling'];
        this.socket.connect();
      } else {
        console.error('Both WebSocket and polling failed');
        // Notify user of connection issues
        this.emit('error', {
          message: 'Unable to establish connection. Please try refreshing the page.'
        });
        this.socket.disconnect();
      }
    });

    this.socket.on('disconnect', (reason: string) => {
      console.log('Disconnected:', reason);
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, try to reconnect
        this.socket.connect();
      }
    });

    this.socket.on('reconnect', (attemptNumber: number) => {
      console.log('Reconnected after', attemptNumber, 'attempts');
      // Try upgrading to WebSocket after successful reconnection
      if (this.socket.io?.opts?.transports && !this.socket.io.opts.transports.includes('websocket')) {
        this.socket.io.opts.transports = ['polling', 'websocket'];
      }
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

  onTournamentUpdate(callback: (data: TournamentStatus) => void) {
    this.socket.on('tournamentUpdate', callback);
    return () => this.socket.off('tournamentUpdate', callback);
  }

  onValidMoves(callback: (moves: string[]) => void) {
    this.socket.on('validMoves', callback);
    return () => this.socket.off('validMoves', callback);
  }

  emit(event: keyof SocketEvents, data?: any) {
    this.socket.emit(event, data);
  }
}

export const gameSocket = new GameSocket();
