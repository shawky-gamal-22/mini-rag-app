from abc import ABC, abstractmethod

class LLMInterface(ABC):

    @abstractmethod
    def set_generation_model(self, model_id: str):
        """
        Set the generation model to be used by the LLM.
        
        :param model_id: The identifier of the model to be set.
        """
        pass


    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size: int):
        """
        Set the embedding model to be used by the LLM.
        
        :param model_id: The identifier of the embedding model to be set.
        """
        pass


    @abstractmethod
    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                      temperature: float= None) -> str:
        """
        Generate text based on the provided prompt.
        
        :param prompt: The input text to generate a response for.
        :param kwargs: Additional parameters for text generation.
        :return: The generated text.
        """
        pass


    @abstractmethod
    def embed_text(self, text: str, document_type: str= None) -> list:
        """
        Generate an embedding for the provided text.
        param text: The input text to generate an embedding for.
        param document_type: The type of document for which the embedding is generated.
        :return: The generated embedding as a list.
        """
        pass


    @abstractmethod
    def construct_prompt(self, prompt: str, role: str):
        """
        Construct a prompt for the LLM based on the provided text and role.
        
        :param prompt: The input text to construct a prompt for.
        :param role: The role of the user or system in the conversation.
        :return: The constructed prompt.
        """
        pass
    