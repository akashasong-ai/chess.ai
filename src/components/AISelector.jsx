import PropTypes from 'prop-types';
import './AISelector.css';
import { AI_PLAYERS } from '../config/ai';

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

AISelector.propTypes = {
  position: PropTypes.string.isRequired,
  selectedAI: PropTypes.string,
  onSelect: PropTypes.func.isRequired
};

export default AISelector;        