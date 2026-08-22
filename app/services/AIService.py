from google import genai
from ..settings import Settings 

setting = Settings()

class AIService:

    def __init__(self):
        self.client = genai.Client(api_key=setting.gemkey)

    async def generate(self, prompt: str) -> str:

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text