import './styles.css';

import PropTypes from 'prop-types';

const GameTypeSelect = ({ onSelect }) => {
    return (
        <div className="game-type-select">
            <h2>Select Game Type</h2>
            <div className="game-options">
                <div 
                    className="game-option chess"
                    onClick={() => onSelect('chess')}
                >
                    <div className="game-icon">♔</div>
                    <h3>Chess</h3>
                    <p>Classic strategy game with AI opponents</p>
                </div>
                <div 
                    className="game-option go"
                    onClick={() => onSelect('go')}
                >
                    <div className="game-icon">⚫</div>
                    <h3>Go</h3>
                    <p>Ancient board game of territory control</p>
                </div>
            </div>
        </div>
    );
};

GameTypeSelect.propTypes = {
    onSelect: PropTypes.func.isRequired
};

export default GameTypeSelect;
