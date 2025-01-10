import React, { useState } from 'react';
import './App.css';
import GameTypeSelect from './components/GameControls/GameTypeSelect';
import PlayerSelect from './components/GameControls/PlayerSelect';
import ChessBoard from './components/GameBoard/ChessBoard';
import GoBoard from './components/GameBoard/GoBoard';
import ChessLeaderboard from './components/Leaderboard/ChessLeaderboard';
import GoLeaderboard from './components/Leaderboard/GoLeaderboard';

function App() {
  const [gameType, setGameType] = useState(null);
  const [player1, setPlayer1] = useState(null);
  const [player2, setPlayer2] = useState(null);
  const [showLeaderboard, setShowLeaderboard] = useState(false);

  const aiOptions = [
    { id: 'openai', name: 'OpenAI' },
    { id: 'anthropic', name: 'Anthropic' },
    { id: 'gemini', name: 'Gemini' },
    { id: 'human', name: 'Human Player' }
  ];

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Game Arena</h1>
      </header>

      <main className="app-main">
        {!gameType ? (
          <GameTypeSelect onSelect={setGameType} />
        ) : !player1 || !player2 ? (
          <PlayerSelect 
            aiOptions={aiOptions}
            onSelectPlayer1={setPlayer1}
            onSelectPlayer2={setPlayer2}
            gameType={gameType}
          />
        ) : (
          <div className="game-container">
            {gameType === 'chess' ? (
              <ChessBoard player1={player1} player2={player2} />
            ) : (
              <GoBoard player1={player1} player2={player2} />
            )}
            
            <div className="game-controls">
              <button onClick={() => setShowLeaderboard(!showLeaderboard)}>
                {showLeaderboard ? 'Hide' : 'Show'} Leaderboard
              </button>
              <button onClick={() => {
                setGameType(null);
                setPlayer1(null);
                setPlayer2(null);
              }}>New Game</button>
            </div>

            {showLeaderboard && (
              gameType === 'chess' ? 
                <ChessLeaderboard /> : 
                <GoLeaderboard />
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;