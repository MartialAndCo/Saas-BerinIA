from abc import ABC, abstractmethod

class AgentBase(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, input_data: dict) -> dict:
        pass
