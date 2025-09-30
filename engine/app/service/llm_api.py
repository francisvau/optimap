from google import genai
from google.genai import types
from groq import AsyncGroq
from openai import AsyncOpenAI

from app.config import DEEPSEEK_API_KEY, GEM_API_KEY, GROQ_API_KEY, OPENAI_API_KEY
from app.model.model import BaseModelType


async def get_model_output(
    system_prompt: str, user_prompt: str, base_model: BaseModelType = BaseModelType.groq
) -> str:
    jsonata_expression: str | None = ""
    match base_model:
        case BaseModelType.groq:
            jsonata_expression = await get_groq_output(system_prompt, user_prompt)
        case BaseModelType.gemini:
            jsonata_expression = await get_gemini_output(system_prompt, user_prompt)
        case BaseModelType.deepseek:
            jsonata_expression = await get_deepseek_output(system_prompt, user_prompt)
        case BaseModelType.openai:
            jsonata_expression = await get_openai_output(system_prompt, user_prompt)
        case _:
            raise ValueError(f"Unsupported base model: {base_model}")

    if jsonata_expression is None:
        raise ValueError("No JSONata expression returned from the model.")

    jsonata_expression = jsonata_expression.strip(" \n\r\t`")

    if jsonata_expression.startswith("jsonata"):
        jsonata_expression = jsonata_expression[len("jsonata") :]

    return jsonata_expression.strip()


async def get_gemini_output(system_prompt: str, user_prompt: str) -> str | None:
    client = genai.Client(api_key=GEM_API_KEY)
    response = await client.aio.models.generate_content(
        model="gemini-2.0-flash",
        contents=[user_prompt],
        config=types.GenerateContentConfig(
            temperature=0.0, system_instruction=system_prompt
        ),
    )
    return response.text


async def get_deepseek_output(system_prompt: str, user_prompt: str) -> str:
    client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        stream=False,
        temperature=0.0,
    )
    return str(response.choices[0].message.content)


async def get_openai_output(system_prompt: str, user_prompt: str) -> str:
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    response = await client.responses.create(
        model="gpt-4.1",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        stream=False,
        temperature=0.0,
    )

    return str(response.output_text)


async def get_groq_output(system_prompt: str, user_prompt: str) -> str:
    client = AsyncGroq(
        api_key=GROQ_API_KEY,
    )

    response = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model="llama-3.3-70b-versatile",
        stream=False,
        temperature=0.0,
    )
    return str(response.choices[0].message.content)
