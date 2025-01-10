import { io, Socket } from 'socket.io-client';
import { GameState } from './api';

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:5000';

interface ServerToClientEvents {
  game_update: (state: GameState) => void;
  error: (error: Error) => void;
}

interface ClientToServerEvents {
  join_game: (data: { gameId: string }) => void;
  leave_game: (data: { gameId: string }) => void;
}

export class GameSocket {
  private socket: Socket<ServerToClientEvents, ClientToServerEvents>;
  private gameId: string | null = null;

  constructor() {
    this.socket = io(SOCKET_URL);
    this.setupListeners();
  }

  private setupListeners(): void {
    this.socket.on('connect', () => {
      console.log('Connected to game server');
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from game server');
    });
  }

  joinGame(gameId: string): void {
    this.gameId = gameId;
    this.socket.emit('join_game', { gameId });
  }

  leaveGame(): void {
    if (this.gameId) {
      this.socket.emit('leave_game', { gameId: this.gameId });
      this.gameId = null;
    }
  }

  onGameUpdate(callback: (state: GameState) => void): void {
    this.socket.on('game_update', callback);
  }

  onError(callback: (error: Error) => void): void {
    this.socket.on('error', callback);
  }

  disconnect(): void {
    this.socket.disconnect();
  }
}

export const gameSocket = new GameSocket(); 