import '@testing-library/jest-dom';
import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

expect.extend(matchers as any);

// Mock socket.io-client
vi.mock('../services/socket', () => ({
  gameSocket: {
    emit: vi.fn(),
    onLeaderboardUpdate: vi.fn(() => vi.fn()),
    onTournamentUpdate: vi.fn(() => vi.fn()),
  }
}));

afterEach(() => {
  cleanup();
});
