import React from 'react';
import './styles.css';
import { AI_PLAYERS } from '../../components/AISelector';

const PlayerSelect = ({ onSelectPlayer1, onSelectPlayer2, gameType }) => {
    return (
        <div className="player-select">
            <h2>Select Players for {gameType.toUpperCase()}</h2>
            
            <div className="player-options">
                <div className="player-column">
                    <h3>Player 1 ({gameType === 'chess' ? 'White' : 'Black'})</h3>
                    <div className="ai-options">
                        {AI_PLAYERS.map(ai => (
                            <button
                                key={ai.id}
                                className="ai-option"
                                onClick={() => onSelectPlayer1(ai)}
                            >
                                <div className="ai-name">{ai.name}</div>
                                <div className="ai-description">{ai.description}</div>
                            </button>
                        ))}
                    </div>
                </div>

                <div className="player-column">
                    <h3>Player 2 ({gameType === 'chess' ? 'Black' : 'White'})</h3>
                    <div className="ai-options">
                        {AI_PLAYERS.map(ai => (
                            <button
                                key={ai.id}
                                className="ai-option"
                                onClick={() => onSelectPlayer2(ai)}
                            >
                                <div className="ai-name">{ai.name}</div>
                                <div className="ai-description">{ai.description}</div>
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PlayerSelect;
