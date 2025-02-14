// AI player configuration

export interface AIPlayer {
  id: string;
  name: string;
  description: string;
}

export const AI_PLAYERS: AIPlayer[] = [
  { id: 'gpt4', name: 'GPT-4', description: 'OpenAI GPT-4' },
  { id: 'claude2', name: 'Claude 2', description: 'Anthropic Claude 2' },
  { id: 'gemini', name: 'Gemini Pro', description: 'Google Gemini Pro' },
  { id: 'perplexity', name: 'Perplexity', description: 'Perplexity AI' }
];

export const getAIPlayer = (id: string): AIPlayer | undefined => {
  return AI_PLAYERS.find(player => player.id === id);
};

export const getAIPlayers = (): AIPlayer[] => {
  return AI_PLAYERS;
};
