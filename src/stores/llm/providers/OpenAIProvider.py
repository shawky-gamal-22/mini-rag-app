from ..LLMInterface import LLMInterface
from openai import OpenAI

class OpenAIProvider(LLMInterface):

    def __init__(self, api_key: str, api_url: str=None,
                 default_input_max_characters: int=1000,
                 default_output_max_characters: int=1000,
                 default_generation_temperature: float=0.1):
        self.api_key = api_key
        self.api_url = api_url
        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_characters = default_output_max_characters
        self.default_generation_temperature = default_generation_temperature
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(api_key=self.api_key,
                             api_url=self.api_url)
        

    


     
        
        
