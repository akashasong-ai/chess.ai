from abc import ABC, abstractmethod

class LLMInterface(ABC):
    @abstractmethod
    async def generate_move(self, game_state: str) -> str:
        """
        Generate the next move given the game state.
        :param game_state: The current state of the chessboard in FEN format.
        :return: The generated move in UCI format.
        """
        pass
