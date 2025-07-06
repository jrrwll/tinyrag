from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from langchain_core.callbacks import BaseCallbackHandler

class CompleteResponseHandler(BaseCallbackHandler):

    def __init__(self):
        self.complete_response = None
        self.structured_response = None

    def on_llm_end(self, response, **kwargs):
        if response.generations:
            generation = response.generations[0][0]
            self.complete_response = generation.model_dump()

            if hasattr(generation, 'text'):
                self.structured_response = generation.text
            elif hasattr(generation, 'message'):
                self.structured_response = generation.message.content
            elif hasattr(generation, 'content'):
                self.structured_response = generation.content
