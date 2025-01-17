import { useState } from 'react';
import PropTypes from 'prop-types';
import styles from './GameTypeSelect.module.css';

const GameTypeSelect = ({ onSelect }) => {
    const [activeGame, setActiveGame] = useState('chess');

    const handleGameSelect = (game) => {
        setActiveGame(game);
        onSelect(game);
    };

    return (
        <div className={styles.gameTypeSelect}>
            <div className={styles.gameOptions}>
                <button 
                    className={`${styles.gameOption} ${activeGame === 'chess' ? styles.active : ''}`}
                    onClick={() => handleGameSelect('chess')}
                >
                    <span className={styles.gameIcon}>♔</span>
                    Chess
                </button>
                <button 
                    className={`${styles.gameOption} ${activeGame === 'go' ? styles.active : ''}`}
                    onClick={() => handleGameSelect('go')}
                >
                    <span className={styles.gameIcon}>⚫</span>
                    Go
                </button>
            </div>
        </div>
    );
};

GameTypeSelect.propTypes = {
    onSelect: PropTypes.func.isRequired
};

export default GameTypeSelect;
