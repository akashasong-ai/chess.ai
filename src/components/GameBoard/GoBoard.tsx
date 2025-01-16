

import { useState, useEffect } from 'react';
import { gameSocket } from '../../services/socket';
import { gameService } from '../../services/api';
import type { GoGameUpdate } from '../../types/go';
import styles from './GoBoard.module.css';

interface GoBoardProps {
  setLeaderboard: (leaderboard: Array<{ id: string; name: string; wins: number; draws: number; losses: number; winRate: number }>) => void;
  gameId?: string;
  isSpectator?: boolean;
}

export const GoBoard: React.FC<GoBoardProps> = ({
  setLeaderboard,
  gameId,
  isSpectator = false
}) => {
  const [board, setBoard] = useState<number[][]>(Array(19).fill(Array(19).fill(0)));
  const [selectedWhiteAI, setSelectedWhiteAI] = useState<string>('');
  const [selectedBlackAI, setSelectedBlackAI] = useState<string>('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [lastMove, setLastMove] = useState<{ x: number; y: number } | null>(null);

  const AI_PLAYERS = [
    { id: 'gpt4', name: 'GPT-4', description: 'OpenAI GPT-4' },
    { id: 'claude2', name: 'Claude 2', description: 'Anthropic Claude 2' },
    { id: 'gemini', name: 'Gemini Pro', description: 'Google Gemini Pro' }
  ];

  useEffect(() => {
    if (gameId) {
      gameSocket.joinGame(gameId);
      
      const unsubscribe = gameSocket.onGameUpdate((state: GoGameUpdate) => {
        if (Array.isArray(state.board)) {
          setBoard(state.board);
        }
        if (state.lastMove) {
          setLastMove(state.lastMove);
        }
        
        if (state.gameOver) {
          gameService.getLeaderboard('go').then(leaderboard => 
            setLeaderboard(leaderboard.map(entry => ({
              id: entry.player,
              name: entry.player,
              wins: Math.floor(entry.score),
              draws: 0,
              losses: 0,
              winRate: entry.score
            })))
          );
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
      const newGameId = await gameService.startGame('go', selectedWhiteAI, selectedBlackAI);
      window.history.pushState({}, '', `/game/${newGameId}`);
    } catch (error) {
      console.error('Failed to start game:', error);
      setIsPlaying(false);
    }
  };

  const handleStopGame = async () => {
    try {
      setIsPlaying(false);
      setBoard(Array(19).fill(Array(19).fill(0)));
      window.history.pushState({}, '', '/');
      const leaderboard = await gameService.getLeaderboard('go');
      setLeaderboard(leaderboard);
    } catch (error) {
      console.error('Failed to stop game:', error);
    }
  };

  const handleIntersectionClick = (x: number, y: number) => {
    if (!isPlaying || isSpectator) return;
    
    gameSocket.emit('move', {
      x,
      y,
      gameId
    });
  };

  const renderIntersection = (x: number, y: number) => {
    const isStarPoint = [3, 9, 15].includes(x) && [3, 9, 15].includes(y);
    const stone = board[x][y];
    const isLastMove = lastMove?.x === x && lastMove?.y === y;

    return (
      <div 
        key={`${x}-${y}`}
        className={`${styles.intersection} ${isStarPoint ? styles.starPoint : ''}`}
        onClick={() => handleIntersectionClick(x, y)}
      >
        {stone > 0 && (
          <div className={`${styles.stone} ${stone === 1 ? styles.black : styles.white} ${isLastMove ? styles.lastMove : ''}`} />
        )}
      </div>
    );
  };

  return (
    <div className={styles.goBoardContainer}>
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
      <div className={styles.goBoard}>
        {Array(19).fill(null).map((_, x) => (
          <div key={x} className={styles.row}>
            {Array(19).fill(null).map((_, y) => renderIntersection(x, y))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default GoBoard;                                                               