import React from 'react';
import './AISelector.css';

export const AI_PLAYERS = [
    { id: 'gpt4', name: 'GPT-4', description: 'OpenAI GPT-4' },
    { id: 'gpt35', name: 'GPT-3.5', description: 'OpenAI GPT-3.5 Turbo' },
    { id: 'claude2', name: 'Claude 2', description: 'Anthropic Claude 2' },
    { id: 'gemini', name: 'Gemini Pro', description: 'Google Gemini Pro' },
    { id: 'perplexity', name: 'Perplexity AI', description: 'Perplexity Llama-3.1' }
];

const AISelector = ({ position, selectedAI, onSelect }) => {
  return (
    <div className="ai-selector">
      <label>{position} Player:</label>
      <select 
        value={selectedAI || ''}
        onChange={(e) => onSelect(e.target.value)}
        className="llm-select"
      >
        <option value="">Select an AI Model</option>
        {AI_PLAYERS.map((llm) => (
          <option key={llm.id} value={llm.id}>
            {llm.name}
          </option>
        ))}
      </select>
      {selectedAI && (
        <div className="llm-description">
          {AI_PLAYERS.find(llm => llm.id === selectedAI)?.description}
        </div>
      )}
    </div>
  );
};

export default AISelector;      