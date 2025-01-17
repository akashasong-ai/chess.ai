

import { useState, useEffect } from 'react';
import { gameSocket } from '../../services/socket';
import { gameService } from '../../services/api';
import type { GoGameUpdate } from '../../types/go';
import styles from './GoBoard.module.css';

interface GoBoardProps {
  setLeaderboard: (leaderboard: Array<{ player: string; score: number }>) => void;
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
    { id: 'gemini', name: 'Gemini Pro', description: 'Google Gemini Pro' },
    { id: 'perplexity', name: 'Perplexity', description: 'Perplexity AI' }
  ];

  useEffect(() => {
    if (gameId) {
      gameSocket.joinGame(gameId);
      
      const unsubscribe = gameSocket.onGameUpdate<GoGameUpdate>((state) => {
        if (Array.isArray(state.board)) {
          setBoard(state.board);
        }
        if (state.lastMove) {
          setLastMove(state.lastMove);
        }
        
        if (state.gameOver) {
          gameService.getLeaderboard('go').then(setLeaderboard);
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

  const handleNewGame = () => {
    setSelectedWhiteAI('');
    setSelectedBlackAI('');
    setBoard(Array(19).fill(Array(19).fill(0)));
    setIsPlaying(false);
    window.history.pushState({}, '', '/');
  };

  const handleRoundRobinTournament = async () => {
    try {
      const response = await fetch('/api/tournament/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          participants: AI_PLAYERS.map(ai => ai.id)
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to start tournament');
      }
      
      setIsPlaying(true);
      const data = await response.json();
      console.log('Tournament started:', data);
    } catch (error) {
      console.error('Failed to start tournament:', error);
      setIsPlaying(false);
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
              <option 
                key={ai.id} 
                value={ai.id}
                disabled={ai.id === selectedBlackAI}
              >
                {ai.name}
              </option>
            ))}
          </select>
        </div>
        <div className={styles.playerColumn}>
          <h3>Black Player</h3>
          <select value={selectedBlackAI} onChange={(e) => setSelectedBlackAI(e.target.value)}>
            <option value="">Select AI</option>
            {AI_PLAYERS.map(ai => (
              <option 
                key={ai.id} 
                value={ai.id}
                disabled={ai.id === selectedWhiteAI}
              >
                {ai.name}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className={styles.statusBar}>
        {isPlaying 
          ? `Current Turn: ${isPlaying ? (lastMove ? 'Black' : 'White') : ''} Player${lastMove ? ` - Last Move: (${lastMove.x}, ${lastMove.y})` : ''}`
          : 'Select players and press Start Game to begin'}
      </div>
      <div className={styles.gameControls}>
        <button 
          onClick={handleStartGame}
          disabled={!selectedWhiteAI || !selectedBlackAI || isPlaying}
          className={styles.startButton}
        >
          Start Game
        </button>
        <button 
          onClick={handleStopGame}
          disabled={!isPlaying}
          className={styles.stopButton}
        >
          Stop Game
        </button>
        <button 
          onClick={handleNewGame}
          className={styles.newButton}
        >
          New Game
        </button>
        <button 
          onClick={handleRoundRobinTournament}
          className={styles.tournamentButton}
          disabled={isPlaying}
        >
          Round Robin Tournament
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
