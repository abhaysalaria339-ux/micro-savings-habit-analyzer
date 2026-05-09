from abc import ABC, abstractmethod
from typing import Generic, TypeVar

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class MLModelContract(ABC, Generic[InputT, OutputT]):
    @abstractmethod
    def predict(self, features: InputT) -> OutputT:
        raise NotImplementedError
