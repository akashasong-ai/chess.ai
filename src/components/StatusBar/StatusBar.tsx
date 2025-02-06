import { useState, useEffect } from 'react';
import styles from './StatusBar.module.css';

const STATUS_MESSAGES = [
  'AI players analyzing positions...',
  'Calculating optimal moves...',
  'Evaluating board state...',
  'Processing game strategy...',
  'Waiting for AI response...',
  'Analyzing game progress...',
  'Computing next move...'
];

export const StatusBar = ({ error }: { error?: string }) => {
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % STATUS_MESSAGES.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className={styles.statusBar}>
      {error || STATUS_MESSAGES[messageIndex]}
    </div>
  );
};

export default StatusBar;
