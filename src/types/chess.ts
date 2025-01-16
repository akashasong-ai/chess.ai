export type PieceType = 'pawn' | 'rook' | 'knight' | 'bishop' | 'queen' | 'king';
export type PieceColor = 'white' | 'black';

export interface ChessPiece {
  type: PieceType;
  color: PieceColor;
  position: string;
}

export interface ChessMove {
  from: string;
  to: string;
  piece: ChessPiece;
  captured?: ChessPiece;
  promotion?: PieceType;
}

export interface ChessGameState {
  board: Record<string, ChessPiece | null>;
  currentTurn: PieceColor;
  moves: ChessMove[];
  isCheck: boolean;
  isCheckmate: boolean;
  isStalemate: boolean;
  moveCount: number;  // Track number of moves to enforce white's first move
}

export interface LeaderboardEntry {
  id: string;
  name: string;
  wins: number;
  draws: number;
  losses: number;
  winRate: number;
}                            