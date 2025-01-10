import React, { useState, useEffect } from 'react';
import { gameApi } from '../services/api';
import './GoBoard.css';

const GoBoard = () => {
  const [board, setBoard] = useState(Array(19).fill(Array(19).fill(null)));
  const [gameState, setGameState] = useState(null);
  const [isPlayerTurn, setIsPlayerTurn] = useState(true);

  useEffect(() => {
    startNewGame();
  }, []);

  async function startNewGame() {
    try {
      const state = await gameApi.startNewGame('go');
      setGameState(state);
      setBoard(state.board);
    } catch (error) {
      console.error('Failed to start new game:', error);
    }
  }

  async function handleIntersectionClick(row, col) {
    if (!isPlayerTurn) return;

    try {
      const result = await gameApi.makeGoMove({ row, col });
      setBoard(result.board);
      setGameState(result.gameState);
      setIsPlayerTurn(false);

      // AI's turn
      const aiResponse = await waitForAIMove();
      setBoard(aiResponse.board);
      setGameState(aiResponse.gameState);
      setIsPlayerTurn(true);
    } catch (error) {
      console.error('Invalid move:', error);
    }
  }

  async function waitForAIMove() {
    return new Promise((resolve) => {
      setTimeout(async () => {
        const response = await gameApi.getGameState('go');
        resolve(response);
      }, 1000);
    });
  }

  const renderIntersection = (row, col) => {
    const isStarPoint = [3, 9, 15].includes(row) && [3, 9, 15].includes(col);
    
    return (
      <div 
        key={`${row}-${col}`} 
        className={`intersection ${isStarPoint ? 'star-point' : ''}`}
        onClick={() => handleIntersectionClick(row, col)}
      >
        <div className="horizontal-line"></div>
        <div className="vertical-line"></div>
        {board[row][col] && (
          <div className={`stone ${board[row][col]}`}></div>
        )}
      </div>
    );
  };

  return (
    <div className="go-container">
      <div className="go-board">
        {board.map((row, i) => (
          <div key={i} className="row">
            {row.map((_, j) => renderIntersection(i, j))}
          </div>
        ))}
      </div>
      <div className="game-info">
        <button onClick={startNewGame}>New Game</button>
        <div className="status">{gameState?.message || "Your turn"}</div>
      </div>
    </div>
  );
};

export default GoBoard; 