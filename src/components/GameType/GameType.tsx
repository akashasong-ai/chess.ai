import React from 'react';
import styles from './GameType.module.css';

interface GameTypeProps {
  selectedGame: 'chess' | 'go' | null;
  onSelectGame: (game: 'chess' | 'go') => void;
}

export const GameType: React.FC<GameTypeProps> = ({ selectedGame, onSelectGame }) => {
  return (
    <div className={styles.gameTypeContainer}>
      <div 
        className={`${styles.gameTypeCard} ${selectedGame === 'chess' ? styles.selected : ''}`}
        onClick={() => onSelectGame('chess')}
      >
        <div className={styles.icon}>♔</div>
        <h3 className={styles.title}>Chess</h3>
        <p className={styles.description}>Classic strategy game with AI opponents</p>
      </div>
      <div 
        className={`${styles.gameTypeCard} ${selectedGame === 'go' ? styles.selected : ''}`}
        onClick={() => onSelectGame('go')}
      >
        <div className={styles.icon}>⚫</div>
        <h3 className={styles.title}>Go</h3>
        <p className={styles.description}>Ancient board game of territory control</p>
      </div>
    </div>
  );
};

export default GameType;
