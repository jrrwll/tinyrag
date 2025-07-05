from app.core.model.base import LLMPrompt


def process_prompt(prompt: LLMPrompt, input_variables: list) -> LLMPrompt:
    content = prompt.content

    content = content.format(**{var.name: var.value for var in input_variables})
    return LLMPrompt(role=prompt.role, content=content)
