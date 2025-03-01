import exceptions
import model

import typing
import ujson
import http

class Backend:
    @classmethod
    def setup(cls, bot: model.Bakerbot) -> None:
        cls.base = "https://api-inference.huggingface.co"
        cls.session = bot.session
        cls.token = bot.secrets.get("hugging-token", None)

    @classmethod
    def name(cls) -> str:
        return "Hugging Face API"

    @classmethod
    async def post(cls, endpoint: str, **kwargs: dict) -> dict:
        """Send a HTTP POST request to the Hugging Face Inference API."""
        async with cls.session.post(f"{cls.base}/{endpoint}", **kwargs) as response:
            data = await response.read()

            if response.status != http.HTTPStatus.OK:
                try: formatted = ujson.loads(data)
                except ValueError: formatted = {}
                error = formatted.get("error", None)
                raise exceptions.HTTPUnexpected(response.status, error)

            return ujson.loads(data)

    @classmethod
    async def generate(cls, model: typing.Any, query: str) -> str:
        """Generate text using the Hugging Face API."""
        if cls.token is None:
            raise model.SecretNotFound("hugging-token not found in secrets.json.")

        headers = {"Authorization": f"Bearer {cls.token}"}

        payload = {
            "inputs": query,
            "options": {
                "use_cache": False,
                "wait_for_model": True
            },
            "parameters": {
                "max_length": model.maximum,
                "temperature": model.temperature,
                "return_full_text": model.remove_input,
                "repetition_penalty": model.repetition_penalty
            }
        }

        endpoint = f"models/{model.identifier}"
        data = await cls.post(endpoint, json=payload, headers=headers)
        return data[0]["generated_text"]

def setup(bot: model.Bakerbot) -> None:
    Backend.setup(bot)
