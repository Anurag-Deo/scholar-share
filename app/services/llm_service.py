from openai import AsyncOpenAI

from app.config.settings import settings


class LLMService:
    def __init__(self):
        # Clients are now created on-demand in get_client
        pass

    def get_client(self, model_type: str = "light"):
        """Get appropriate client based on model type"""
        if model_type == "heavy":
            provider = settings.HEAVY_MODEL_PROVIDER
            model_name = settings.HEAVY_MODEL_NAME
            api_key = settings.HEAVY_MODEL_API_KEY
            base_url = settings.HEAVY_MODEL_BASE_URL
        else:
            provider = settings.LIGHT_MODEL_PROVIDER
            model_name = settings.LIGHT_MODEL_NAME
            api_key = settings.LIGHT_MODEL_API_KEY
            base_url = settings.LIGHT_MODEL_BASE_URL

        if not api_key:
            raise ValueError(
                f"API key for {model_type} model ({provider}) not configured.",
            )

        return AsyncOpenAI(api_key=api_key, base_url=base_url), model_name

    async def generate_completion(
        self,
        messages: list,
        model_type: str = "light",
        temperature: float = 0.7,
        # max_tokens: int = 4000,
    ) -> str:
        """Generate completion using appropriate model"""
        client, model_name = self.get_client(model_type)

        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                # max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            if content is None:
                raise Exception("LLM returned None content")
            return content
        except Exception as e:
            raise Exception(f"LLM generation failed: {e!s}")


llm_service = LLMService()
