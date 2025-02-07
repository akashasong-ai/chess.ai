import io from 'socket.io-client';
import type { ChessGameState } from '../types/chess';
import type { GoGameState, GoGameUpdate } from '../types/go';
import type { LeaderboardEntry } from '../types/leaderboard';

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'https://ai-arena-backend.onrender.com';
console.log('Using WebSocket URL:', SOCKET_URL);

// Configure Socket.IO with improved transport and reconnection settings
const socketOptions = {
  transports: ['polling', 'websocket'],  // Start with polling, upgrade to websocket
  path: '/socket.io',
  secure: true,
  rejectUnauthorized: false,
  withCredentials: true,
  timeout: 20000,  // Increase timeout for slow connections
  reconnectionDelayMax: 10000,  // Maximum delay between reconnection attempts
  reconnectionAttempts: 5  // Increase max reconnection attempts
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

class GameSocket {
  socket: ReturnType<typeof io>;

  constructor() {
    console.log('Initializing socket connection to:', SOCKET_URL);
    this.socket = io(SOCKET_URL, {
      ...socketOptions,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 10000,
      autoConnect: true,
      forceNew: true
    });

    let retryCount = 0;
    const maxRetries = 3;

    // Add connection event handlers
    this.socket.on('connect', () => {
      console.log('Connected to game server');
      this.emit('connectionStatus', 'connected');
    });

    this.socket.on('connect_error', (error: Error) => {
      console.error('Connection error:', error);
      this.emit('connectionStatus', 'disconnected');
      retryCount++;
      
      if (retryCount <= maxRetries) {
        console.log(`Retrying connection (${retryCount}/${maxRetries})`);
        const backoffDelay = Math.min(1000 * Math.pow(2, retryCount - 1), 10000);
        
        // Try polling if WebSocket fails
        if (this.socket.io?.opts?.transports?.includes('websocket')) {
          console.log('Falling back to polling transport');
          this.socket.io.opts.transports = ['polling'];
        }
        
        // Attempt reconnection with exponential backoff
        setTimeout(() => {
          console.log(`Attempting reconnection after ${backoffDelay}ms delay`);
          this.socket.connect();
        }, backoffDelay);
      } else {
        console.error('Max reconnection attempts reached');
        this.emit('error', { message: 'Connection failed after multiple attempts. Please refresh the page or try again later.' });
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
      retryCount = 0; // Reset retry count on successful reconnection
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
