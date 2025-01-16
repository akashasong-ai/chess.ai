import PropTypes from 'prop-types';
import './styles.css';

const PlayerSelect = ({ aiOptions, onSelectPlayer1, onSelectPlayer2, gameType }) => {
    return (
        <div className="player-select">
            <h2>Select Players for {gameType.toUpperCase()}</h2>
            
            <div className="player-options">
                <div className="player-column">
                    <h3>Player 1 ({gameType === 'chess' ? 'White' : 'Black'})</h3>
                    <div className="ai-options">
                        {aiOptions.map(ai => (
                            <button
                                key={ai.id}
                                className="ai-option"
                                onClick={() => onSelectPlayer1(ai)}
                            >
                                {ai.name}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="player-column">
                    <h3>Player 2 ({gameType === 'chess' ? 'Black' : 'White'})</h3>
                    <div className="ai-options">
                        {aiOptions.map(ai => (
                            <button
                                key={ai.id}
                                className="ai-option"
                                onClick={() => onSelectPlayer2(ai)}
                            >
                                {ai.name}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

PlayerSelect.propTypes = {
  aiOptions: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired
    })
  ).isRequired,
  onSelectPlayer1: PropTypes.func.isRequired,
  onSelectPlayer2: PropTypes.func.isRequired,
  gameType: PropTypes.oneOf(['chess', 'go']).isRequired
};

export default PlayerSelect;
