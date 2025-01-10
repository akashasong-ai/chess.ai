import { io, Socket } from 'socket.io-client';
import { GameState } from './api';

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:5000';

export class GameSocket {
  private socket: Socket;
  private gameId: string | null = null;

  constructor() {
    this.socket = io(SOCKET_URL);
    this.setupListeners();
  }

  private setupListeners() {
    this.socket.on('connect', () => {
      console.log('Connected to game server');
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from game server');
    });
  }

  joinGame(gameId: string) {
    this.gameId = gameId;
    this.socket.emit('join_game', { gameId });
  }

  leaveGame() {
    if (this.gameId) {
      this.socket.emit('leave_game', { gameId: this.gameId });
      this.gameId = null;
    }
  }

  onGameUpdate(callback: (state: GameState) => void) {
    this.socket.on('game_update', callback);
  }

  onError(callback: (error: Error) => void) {
    this.socket.on('error', callback);
  }
}

export const gameSocket = new GameSocket(); 