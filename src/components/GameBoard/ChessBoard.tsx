import React, { useState, useEffect } from 'react';
import styles from './ChessBoard.module.css';
import { ChessGameState, ChessPiece, PieceType, PieceColor } from '../../types/chess';
import { gameSocket } from '../../services/socket';
import { gameService } from '../../services/api';
import { AI_PLAYERS } from '../../config/ai';

interface ChessBoardProps {
  setLeaderboard: (leaderboard: Array<{ id: string; name: string; wins: number; draws: number; losses: number; winRate: number }>) => void;
  gameId?: string;
  playerColor?: 'white' | 'black';
  isSpectator?: boolean;
}

export const ChessBoard: React.FC<ChessBoardProps> = ({
  setLeaderboard,
  gameId,
  playerColor = 'white',
  isSpectator = false
}) => {
  const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
  const ranks = ['1', '2', '3', '4', '5', '6', '7', '8'];
  
  const initialBoard: Record<string, ChessPiece> = {};
  
  // Initialize board with starting positions
  files.forEach(file => {
    ranks.forEach(rank => {
      const position = `${file}${rank}`;

      if (rank === '1' || rank === '2') {
        const color: PieceColor = 'white';
        let type: PieceType;
        if (rank === '2') {
          type = 'pawn';
        } else {
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
      else if (rank === '7' || rank === '8') {
        const color: PieceColor = 'black';
        let type: PieceType;
        if (rank === '7') {
          type = 'pawn';
        } else {
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
      else {
        initialBoard[position] = null;
      }
    });
  });

  const [gameState, setGameState] = useState<ChessGameState>({
    board: initialBoard,
    currentTurn: 'white',
    moves: [],
    isCheck: false,
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
          isStalemate: state.isStalemate || false
        };
        setGameState(chessState);
        
        // Update leaderboard if game is finished
        if (state.isCheckmate || state.isStalemate) {
          gameService.getLeaderboard('chess').then(setLeaderboard);
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
        isStalemate: false
      });
      // Remove game ID from URL
      window.history.pushState({}, '', '/');
      // Update leaderboard
      const leaderboard = await gameService.getLeaderboard('chess');
      setLeaderboard(leaderboard);
    } catch (error) {
      console.error('Failed to stop game:', error);
    }
  };

  const handleSquareClick = (clickedPosition: string) => {
    if (!isPlaying || isSpectator || (gameState && gameState.currentTurn !== playerColor)) {
      return;
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
    const ranks = ['8', '7', '6', '5', '4', '3', '2', '1'];
    const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
    
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