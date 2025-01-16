export type StoneColor = 'black' | 'white';

export interface GoGameState {
  board: number[][];
  currentPlayer: StoneColor;
  lastMove?: { x: number; y: number };
  capturedBlack: number;
  capturedWhite: number;
  gameOver?: boolean;
  winner?: StoneColor;
}

export interface GoMove {
  x: number;
  y: number;
  color: StoneColor;
}

export interface GoGameUpdate {
  board: number[][];
  lastMove?: { x: number; y: number };
  gameOver?: boolean;
  winner?: StoneColor;
}
