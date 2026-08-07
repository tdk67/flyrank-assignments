from abc import ABC, abstractmethod
from typing import Any, List


class BaseTargetStrategy(ABC):

    @property
    @abstractmethod
    def target_name(self) -> str:
        pass

    @abstractmethod
    async def run(self, max_pages: int = 1, output_file: str | None = None, **kwargs) -> List[Any]:
        pass
