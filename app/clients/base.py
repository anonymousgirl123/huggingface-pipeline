from abc import ABC, abstractmethod


from app.core.schemas import LLMRequest, LLMResponse



class LLMClient(ABC):

    @abstractmethod

    def generate(self, req: LLMRequest) -> LLMResponse:

        pass