from abc import ABC, abstractmethod

class PLUGIN_TEMPLATE(ABC):
    """Интерфейс плагина — контракт, который обязаны соблюдать все плагины."""

    @abstractmethod
    def _runChecker(self, config: dict) -> None:
        """to start checker calling every N seconds"""
        pass

    @abstractmethod
    def _stopChecker(self, config: dict) -> None:
        """to stop checker calling every N seconds"""
        pass

    @abstractmethod
    def cecker(self, data: list) -> dict:
        """main body of method calculation"""
        pass

    @abstractmethod
    def exo(self) -> None:
        """print privet asset information"""
        """this need to check workability of the class"""
        pass
