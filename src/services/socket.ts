import io from 'socket.io-client';
import type { ChessGameState } from '../types/chess';
import type { GoGameState, GoGameUpdate } from '../types/go';
import type { LeaderboardEntry } from '../types/leaderboard';

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'https://chess-ai-backend.onrender.com';
console.log('Using WebSocket URL:', SOCKET_URL);

// Configure Socket.IO with improved transport and reconnection settings
type ExtendedSocket = ReturnType<typeof io> & {
  connected: boolean;
  disconnect: () => void;
  on: (event: string, callback: (...args: any[]) => void) => void;
  off: (event: string, callback: (...args: any[]) => void) => void;
  emit: (event: string, ...args: any[]) => void;
  io: {
    engine: {
      transport: {
        name: string;
      };
      on(event: string, callback: () => void): void;
    };
    opts?: {
      transports?: string[];
    };
  };
}

interface SocketOptions {
  transports: string[];
  path: string;
  secure: boolean;
  rejectUnauthorized: boolean;
  withCredentials: boolean;
  timeout: number;
  reconnectionDelayMax: number;
  reconnectionAttempts: number;
  forceNew: boolean;
  upgrade: boolean;
  rememberUpgrade: boolean;
  autoConnect: boolean;
  reconnection: boolean;
  reconnectionDelay: number;
  extraHeaders: {
    'Cache-Control': string;
  };
}

const socketOptions: SocketOptions = {
  transports: ['polling', 'websocket'],
  path: '/socket.io',
  secure: true,
  rejectUnauthorized: false,
  withCredentials: true,
  timeout: 60000,
  reconnectionDelayMax: 30000,
  reconnectionAttempts: 10,
  forceNew: true,
  upgrade: true,
  rememberUpgrade: true,
  autoConnect: true,
  reconnection: true,
  reconnectionDelay: 1000,
  extraHeaders: {
    'Cache-Control': 'no-cache'
  }
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
  private socket!: ExtendedSocket;

  private connect() {
    if (this.socket?.connected) {
      this.socket.disconnect();
    }
    
    this.socket = io(SOCKET_URL, socketOptions) as ExtendedSocket;
    
    // Force transport upgrade after connection
    this.socket.on('connect', () => {
      console.log('Socket connected with transport:', this.socket.io.engine.transport.name);
      
      if (this.socket.io.engine.transport.name === 'polling') {
        this.socket.io.engine.on('upgrade', () => {
          console.log('Transport upgraded to:', this.socket.io.engine.transport.name);
        });
      }
    });

    this.setupEventHandlers();
  }

  constructor() {
    console.log('Initializing socket connection to:', SOCKET_URL);
    this.connect();
  }

  joinGame(gameId: string) {
    this.socket.emit('joinGame', gameId);
  }

  leaveGame() {
    this.socket.emit('leaveGame');
  }

  onGameUpdate<T extends ChessGameState | GoGameUpdate>(callback: (state: T) => void) {
    this.socket.on('gameUpdate', (state: T) => {
      console.log('Received game update:', state);
      callback(state);
    });
    return () => this.socket.off('gameUpdate', callback as (state: any) => void);
  }

  onLeaderboardUpdate(callback: (data: LeaderboardEntry[]) => void) {
    this.socket.on('leaderboardUpdate', (data: LeaderboardEntry[]) => {
      console.log('Received leaderboard update:', data);
      callback(data);
    });
    return () => this.socket.off('leaderboardUpdate', callback);
  }

  onTournamentUpdate(callback: (data: TournamentStatus) => void) {
    this.socket.on('tournamentUpdate', (data: TournamentStatus) => {
      console.log('Received tournament update:', data);
      callback(data);
    });
    return () => this.socket.off('tournamentUpdate', callback);
  }

  onValidMoves(callback: (moves: string[]) => void) {
    this.socket.on('validMoves', (moves: string[]) => {
      console.log('Received valid moves:', moves);
      callback(moves);
    });
    return () => this.socket.off('validMoves', callback);
  }

  private setupEventHandlers() {
    let retryCount = 0;
    const maxRetries = 3;
    const maxBackoffDelay = 30000; // 30 seconds max delay

    this.socket.on('connect', () => {
      console.log('Socket connected with transport:', this.socket.io.engine.transport.name);
      this.emit('connectionStatus', 'connected');
      retryCount = 0;
      
      if (this.socket.io.engine.transport.name === 'polling') {
        this.socket.io.engine.on('upgrade', () => {
          console.log('Transport upgraded to:', this.socket.io.engine.transport.name);
        });
      }
    });

    this.socket.on('connect_error', (error: Error) => {
      console.error('Connection error:', error);
      this.emit('connectionStatus', 'disconnected');
      this.emit('error', { message: `Connection error: ${error.message}` });
      retryCount++;
      
      if (retryCount <= maxRetries) {
        console.log(`Retrying connection (${retryCount}/${maxRetries})`);
        const backoffDelay = Math.min(1000 * Math.pow(2, retryCount - 1), maxBackoffDelay);
        
        // Try polling if WebSocket fails
        if (this.socket.io?.opts?.transports?.includes('websocket')) {
          console.log('Falling back to polling transport');
          this.socket.io.opts.transports = ['polling'];
        }
        
        setTimeout(() => {
          console.log(`Attempting reconnection after ${backoffDelay}ms delay`);
          this.connect();
        }, backoffDelay);
      } else {
        console.error('Max reconnection attempts reached');
        this.emit('error', { message: 'Connection failed after multiple attempts. Please refresh the page or try again later.' });
        this.socket.disconnect();
      }
    });

    this.socket.on('error', (error: Error) => {
      console.error('Socket error:', error);
      this.emit('error', { message: `Socket error: ${error.message}` });
    });

    this.socket.on('disconnect', (reason: string) => {
      console.log('Disconnected:', reason);
      this.emit('connectionStatus', 'disconnected');
      
      if (reason === 'io server disconnect' || reason === 'transport close') {
        console.log('Attempting to reconnect...');
        this.connect();
      }
    });

    this.socket.on('game_error', (error: { message: string }) => {
      console.error('Game error:', error);
      this.emit('error', { message: `Game error: ${error.message}` });
    });

    this.socket.on('reconnect', (attemptNumber: number) => {
      console.log('Reconnected after', attemptNumber, 'attempts');
      retryCount = 0;
    });
  }

  emit(event: keyof SocketEvents, data?: any) {
    console.log(`Emitting ${event}:`, data);
    
    if (!this.socket?.connected) {
      console.error('Socket not connected. Attempting reconnection...');
      this.connect();
      return;
    }

    this.socket.emit(event, data, (response: any) => {
      console.log(`Response from ${event}:`, response);
      if (response?.error) {
        console.error(`Error in ${event}:`, response.error);
        this.emit('error', { message: `Game error: ${response.error}` });
      }
    });
  }
}

export const gameSocket = new GameSocket();
