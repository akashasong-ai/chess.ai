import React, { useState, useEffect } from 'react';
import styles from './ChessBoard.module.css';
import { ChessGameState } from '../../types/chess';
import { gameSocket } from '../../services/socket';

interface ChessBoardProps {
  gameId: string;
  playerColor?: 'white' | 'black';
  isSpectator?: boolean;
}

export const ChessBoard: React.FC<ChessBoardProps> = ({
  gameId,
  playerColor = 'white',
  isSpectator = false
}) => {
  const [gameState, setGameState] = useState<ChessGameState | null>(null);
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null);
  const [possibleMoves, setPossibleMoves] = useState<string[]>([]);

  useEffect(() => {
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
    });

    return () => {
      unsubscribe();
      gameSocket.leaveGame();
    };
  }, [gameId]);

  const handleSquareClick = (clickedPosition: string) => {
    if (isSpectator || (gameState && gameState.currentTurn !== playerColor)) {
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

  if (!gameState) {
    return <div>Loading...</div>;
  }

  return (
    <div className={styles.chessBoard}>
      {renderBoard()}
    </div>
  );
}; 