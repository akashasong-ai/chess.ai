import PropTypes from 'prop-types';
import styles from './PlayerSelect.module.css';

const AI_PLAYERS = [
  { id: 'gpt4', name: 'GPT-4' },
  { id: 'claude', name: 'CLAUDE' },
  { id: 'gemini', name: 'GEMINI' },
  { id: 'perplexity', name: 'PERPLEXITY' }
];

const PlayerSelect = ({ gameType, onSelectPlayer1, onSelectPlayer2, selectedPlayer1, selectedPlayer2 }) => {
  return (
    <div className={styles.playerSelect}>
      <h2 className={styles.title}>Select Players</h2>
      <div className={styles.playerColumns}>
        <div className={styles.playerColumn}>
          <h3>{gameType === 'chess' ? 'White' : 'Black'}</h3>
          <select 
            value={selectedPlayer1} 
            onChange={(e) => onSelectPlayer1(e.target.value)}
            className={styles.select}
            aria-label={gameType === 'chess' ? 'White' : 'Black'}
          >
            <option value="">Select AI</option>
            {AI_PLAYERS.map(ai => (
              <option 
                key={ai.id} 
                value={ai.id}
                disabled={ai.id === selectedPlayer2}
              >
                {ai.name}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.playerColumn}>
          <h3>{gameType === 'chess' ? 'Black' : 'White'}</h3>
          <select 
            value={selectedPlayer2} 
            onChange={(e) => onSelectPlayer2(e.target.value)}
            className={styles.select}
            aria-label={gameType === 'chess' ? 'Black' : 'White'}
          >
            <option value="">Select AI</option>
            {AI_PLAYERS.map(ai => (
              <option 
                key={ai.id} 
                value={ai.id}
                disabled={ai.id === selectedPlayer1}
              >
                {ai.name}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};

PlayerSelect.propTypes = {
  gameType: PropTypes.oneOf(['chess', 'go']).isRequired,
  onSelectPlayer1: PropTypes.func.isRequired,
  onSelectPlayer2: PropTypes.func.isRequired,
  selectedPlayer1: PropTypes.string.isRequired,
  selectedPlayer2: PropTypes.string.isRequired
};

export default PlayerSelect;
