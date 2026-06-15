"""
Thin LLM wrapper. Runs in MOCK mode out-of-the-box (no API key needed) so the
walking skeleton works on day one. Fill in a provider when keys are ready.
"""
from app import config


def complete(system: str, user: str) -> str:
    """Return the model's text response for a single-turn prompt."""
    provider = config.LLM_PROVIDER

    if provider == "mock":
        # Deterministic stand-in so the whole pipeline runs before real LLM is wired.
        return (
            "[MOCK LLM] Based on the law passages provided, here is a plain-language "
            "explanation of the user's rights. (Set LLM_PROVIDER + an API key in .env "
            "to use a real model.)"
        )

    if provider == "anthropic":
        # TODO (P1): pip install anthropic; uncomment.
        # import anthropic
        # client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        # msg = client.messages.create(
        #     model=config.LLM_MODEL or "claude-sonnet-4-6",
        #     max_tokens=1024,
        #     system=system,
        #     messages=[{"role": "user", "content": user}],
        # )
        # return msg.content[0].text
        raise NotImplementedError("Wire up Anthropic in llm.py")

    if provider == "openai":
        # TODO (P1): pip install openai; uncomment.
        # from openai import OpenAI
        # client = OpenAI(api_key=config.OPENAI_API_KEY)
        # resp = client.chat.completions.create(
        #     model=config.LLM_MODEL or "gpt-4o",
        #     messages=[{"role": "system", "content": system},
        #               {"role": "user", "content": user}],
        # )
        # return resp.choices[0].message.content
        raise NotImplementedError("Wire up OpenAI in llm.py")

    raise ValueError(f"Unknown LLM_PROVIDER: {provider}")
