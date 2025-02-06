import { useState } from 'react';
import { ChessBoard } from './components/GameBoard/ChessBoard';
import GoBoard from './components/GameBoard/GoBoard.tsx';
import GameTypeSelect from './components/GameControls/GameTypeSelect';
import PlayerSelect from './components/GameControls/PlayerSelect';
import Leaderboard from './components/Leaderboard';
import StatusBar from './components/StatusBar';
import styles from './App.module.css';

function App() {
  const [gameType, setGameType] = useState('chess');
  const [leaderboard, setLeaderboard] = useState([]);
  const [player1, setPlayer1] = useState('');
  const [player2, setPlayer2] = useState('');
  const [error, setError] = useState('');

  const handleError = (err) => {
    setError(err.message);
    setTimeout(() => setError(''), 5000);
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>AI Game Arena</h1>
      <GameTypeSelect onSelect={setGameType} />
      <div className={styles.gameContainer}>
        <StatusBar error={error} />
        <PlayerSelect 
          gameType={gameType}
          onSelectPlayer1={setPlayer1}
          onSelectPlayer2={setPlayer2}
          selectedPlayer1={player1}
          selectedPlayer2={player2}
        />
        <div className={styles.board}>
          {gameType === 'chess' ? (
            <ChessBoard 
              setLeaderboard={setLeaderboard} 
              onError={handleError}
              player1={player1}
              player2={player2}
            />
          ) : (
            <GoBoard 
              setLeaderboard={setLeaderboard}
              onError={handleError}
              player1={player1}
              player2={player2}
            />
          )}
        </div>
        <Leaderboard leaderboard={leaderboard} gameType={gameType} />
      </div>
    </div>
  );
}

export default App;
