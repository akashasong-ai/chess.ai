import React, { useState, useEffect } from 'react';
import styles from './ChessBoard.module.css';
import '../types/react';
import type { ChessGameState, ChessPiece, PieceType, PieceColor, ChessMove } from '../../types/chess';
import { gameSocket } from '../../services/socket';
import { gameService } from '../../services/api';
import { AI_PLAYERS } from '../../config/ai';

// Add React types
declare global {
  namespace JSX {
    interface IntrinsicElements {
      div: React.DetailedHTMLProps<React.HTMLAttributes<HTMLDivElement>, HTMLDivElement>;
      select: React.DetailedHTMLProps<React.SelectHTMLAttributes<HTMLSelectElement>, HTMLSelectElement>;
      option: React.DetailedHTMLProps<React.OptionHTMLAttributes<HTMLOptionElement>, HTMLOptionElement>;
      h3: React.DetailedHTMLProps<React.HTMLAttributes<HTMLHeadingElement>, HTMLHeadingElement>;
      button: React.DetailedHTMLProps<React.ButtonHTMLAttributes<HTMLButtonElement>, HTMLButtonElement>;
    }
  }
}

// Add JSX namespace to fix element type errors
// Add React types
declare module 'react' {
  interface HTMLAttributes<T> extends AriaAttributes, DOMAttributes<T> {
    className?: string;
  }
}

declare namespace JSX {
  interface IntrinsicElements {
    div: React.DetailedHTMLProps<React.HTMLAttributes<HTMLDivElement>, HTMLDivElement>;
    select: React.DetailedHTMLProps<React.SelectHTMLAttributes<HTMLSelectElement>, HTMLSelectElement>;
    option: React.DetailedHTMLProps<React.OptionHTMLAttributes<HTMLOptionElement>, HTMLOptionElement>;
    h3: React.DetailedHTMLProps<React.HTMLAttributes<HTMLHeadingElement>, HTMLHeadingElement>;
    button: React.DetailedHTMLProps<React.ButtonHTMLAttributes<HTMLButtonElement>, HTMLButtonElement>;
  }
}

// Component interfaces and types
interface LeaderboardEntry {
  id: string;
  name: string;
  wins: number;
  draws: number;
  losses: number;
  winRate: number;
}

interface ChessBoardProps {
  gameId?: string;
  playerColor?: PieceColor;
  isSpectator?: boolean;
  setLeaderboard: (leaderboard: LeaderboardEntry[]) => void;
}

// Initial board setup
// Initial board setup is handled in the initialization logic below
// Remove duplicate imports and interface

// ChessBoardProps interface is defined above

export const ChessBoard: React.FC<ChessBoardProps> = ({
  setLeaderboard,
  gameId,
  playerColor = 'white',
  isSpectator = false
}) => {
  const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
  const ranks = ['1', '2', '3', '4', '5', '6', '7', '8'];
  
  const initialBoard: Record<string, ChessPiece | null> = {};
  
  // Initialize board with starting positions - white at bottom (ranks 1,2), black at top (ranks 7,8)
  files.forEach(file => {
    ranks.forEach(rank => {
      const position = `${file}${rank}`;
      const rankNum = parseInt(rank);

      // White pieces at bottom (ranks 1,2)
      if (rankNum <= 2) {
        const color: PieceColor = 'white';
        let type: PieceType;
        
        if (rankNum === 2) {
          type = 'pawn';  // White pawns on rank 2
        } else {  // White pieces on rank 1
          switch (file) {
            case 'a': case 'h': type = 'rook'; break;
            case 'b': case 'g': type = 'knight'; break;
            case 'c': case 'f': type = 'bishop'; break;
            case 'd': type = 'queen'; break;
            case 'e': type = 'king'; break;
            default: type = 'pawn';
          }
        }
        initialBoard[position] = { type, color, position };
      }
      // Black pieces at top (ranks 7,8)
      else if (rankNum >= 7) {
        const color: PieceColor = 'black';
        let type: PieceType;
        
        if (rankNum === 7) {
          type = 'pawn';  // Black pawns on rank 7
        } else {  // Black pieces on rank 8
          switch (file) {
            case 'a': case 'h': type = 'rook'; break;
            case 'b': case 'g': type = 'knight'; break;
            case 'c': case 'f': type = 'bishop'; break;
            case 'd': type = 'queen'; break;
            case 'e': type = 'king'; break;
            default: type = 'pawn';
          }
        }
        initialBoard[position] = { type, color, position };
      }
      // Empty squares (ranks 3-6)
      else {
        initialBoard[position] = null;
      }
    });
  });

  const [gameState, setGameState] = useState<ChessGameState>({
    // Initialize with white's turn and moveCount = 0
    board: initialBoard,
    currentTurn: 'white',  // Always start with white's turn
    moves: [],
    isCheck: false,
    moveCount: 0,  // Initialize moveCount to enforce white's first move
    isCheckmate: false,
    isStalemate: false
  });
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null);
  const [possibleMoves, setPossibleMoves] = useState<string[]>([]);
  const [selectedWhiteAI, setSelectedWhiteAI] = useState<string>('');
  const [selectedBlackAI, setSelectedBlackAI] = useState<string>('');
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (gameId) {
      gameSocket.joinGame(gameId);
      
      const unsubscribe = gameSocket.onGameUpdate((state) => {
        const chessState: ChessGameState = {
          board: state.board || {},
          currentTurn: state.currentTurn as 'white' | 'black',
          moves: state.moves || [],
          isCheck: state.isCheck || false,
          isCheckmate: state.isCheckmate || false,
          isStalemate: state.isStalemate || false,
          moveCount: state.moveCount || 0
        };
        setGameState(chessState);
        
        // Update leaderboard if game is finished
        if (state.isCheckmate || state.isStalemate) {
          gameService.getLeaderboard('chess').then(data => {
            // Transform API response to match LeaderboardEntry type
            const transformedData: LeaderboardEntry[] = data.map(item => ({
              id: item.player,
              name: item.player,
              wins: Math.floor(item.score),
              draws: 0,
              losses: 0,
              winRate: item.score
            }));
            setLeaderboard(transformedData);
          });
        }
      });

      return () => {
        unsubscribe();
        gameSocket.leaveGame();
      };
    }
  }, [gameId, setLeaderboard]);

  const handleStartGame = async () => {
    try {
      setIsPlaying(true);
      const newGameId = await gameService.startGame('chess', selectedWhiteAI, selectedBlackAI);
      // Update URL with game ID
      window.history.pushState({}, '', `/game/${newGameId}`);
    } catch (error) {
      console.error('Failed to start game:', error);
      setIsPlaying(false);
    }
  };

  const handleStopGame = async () => {
    try {
      setIsPlaying(false);
      setGameState({
        board: initialBoard,
        currentTurn: 'white',
        moves: [],
        isCheck: false,
        isCheckmate: false,
        isStalemate: false,
        moveCount: 0  // Reset move count when stopping game
      });
      // Remove game ID from URL
      window.history.pushState({}, '', '/');
      // Update leaderboard
      const data = await gameService.getLeaderboard('chess');
      // Transform API response to match LeaderboardEntry type
      const transformedData: LeaderboardEntry[] = data.map(item => ({
        id: item.player,
        name: item.player,
        wins: Math.floor(item.score),
        draws: 0,
        losses: 0,
        winRate: item.score
      }));
      setLeaderboard(transformedData);
    } catch (error) {
      console.error('Failed to stop game:', error);
    }
  };

  const handleSquareClick = (clickedPosition: string) => {
    if (!isPlaying || isSpectator || !gameState) {
      return;
    }

    // Enforce white's first move when moveCount is 0
    if (gameState.moveCount === 0) {
      if (playerColor === 'black') {
        return; // Black cannot move first
      }
      const piece = gameState.board[clickedPosition];
      if (piece?.color !== 'white') {
        return; // Only white pieces can be selected for first move
      }
    }

    // Ensure it's the player's turn
    if (gameState.currentTurn !== playerColor) {
      return;
    }

    const piece = gameState.board[clickedPosition];
    if (piece && piece.color === playerColor) {
      setSelectedSquare(clickedPosition);
      // Calculate possible moves considering moveCount
      const moves = gameState.moves.filter((move: ChessMove) => {
        if (gameState.moveCount === 0) {
          // Only allow white pieces to move first
          const fromPiece = gameState.board[move.from];
          return fromPiece?.color === 'white';
        }
        return move.from === clickedPosition;
      });
      setPossibleMoves(moves.map((move: ChessMove) => move.to));
    }

    if (selectedSquare) {
      if (possibleMoves.includes(clickedPosition)) {
        gameSocket.emit('move', {
          from: selectedSquare,
          to: clickedPosition,
          gameId
        });
        setSelectedSquare(null);
        setPossibleMoves([]);
      } else {
        setSelectedSquare(clickedPosition);
        setPossibleMoves([]);
      }
    } else {
      const piece = gameState?.board[clickedPosition];
      if (piece && piece.color === playerColor) {
        setSelectedSquare(clickedPosition);
        setPossibleMoves([]);
      }
    }
  };

  const renderSquare = (position: string) => {
    const piece = gameState?.board[position];
    const isSelected = position === selectedSquare;
    const isValidMove = possibleMoves.includes(position);

    return (
      <div 
        key={position}
        className={`${styles.square} ${isSelected ? styles.selected : ''} ${isValidMove ? styles.validMove : ''}`}
        onClick={() => handleSquareClick(position)}
      >
        {piece && (
          <div className={`${styles.piece} ${styles[piece.type]} ${styles[piece.color]}`} />
        )}
      </div>
    );
  };

  const renderBoard = () => {
    // Render from rank 8 down to 1 to ensure white pieces are at the bottom
    const ranks = ['8', '7', '6', '5', '4', '3', '2', '1'];
    const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
    
    // No need for reverse() since ranks are already ordered from 8 to 1
    return ranks.map(rank => (
      <div key={rank} className={styles.rank}>
        {files.map(file => renderSquare(`${file}${rank}`))}
      </div>
    ));
  };

  return (
    <div className={styles.chessBoardContainer}>
      <div className={styles.playerSelection}>
        <div className={styles.playerColumn}>
          <h3>White Player</h3>
          <select value={selectedWhiteAI} onChange={(e) => setSelectedWhiteAI(e.target.value)}>
            <option value="">Select AI</option>
            {AI_PLAYERS.map(ai => (
              <option key={ai.id} value={ai.id}>{ai.name}</option>
            ))}
          </select>
        </div>
        <div className={styles.playerColumn}>
          <h3>Black Player</h3>
          <select value={selectedBlackAI} onChange={(e) => setSelectedBlackAI(e.target.value)}>
            <option value="">Select AI</option>
            {AI_PLAYERS.map(ai => (
              <option key={ai.id} value={ai.id}>{ai.name}</option>
            ))}
          </select>
        </div>
      </div>
      <div className={styles.gameControls}>
        <button 
          onClick={isPlaying ? handleStopGame : handleStartGame}
          disabled={!selectedWhiteAI || !selectedBlackAI}
        >
          {isPlaying ? 'Stop Game' : 'Start Game'}
        </button>
      </div>
      <div className={styles.chessBoard}>
        {renderBoard()}
      </div>
    </div>
  );
};                                                                                    