from datetime import timedelta, datetime

from yandex_cloud_ml_sdk import YCloudML
from typing import Dict

from bot.core.config import LLMSettings
from bot.services.users import UserThreadsService
from llm.llm_utils import update_assistant_in_config

assistant_instruction = """
Ты - профессиональный копирайтер/редактор. 
У тебя есть две задачи:
1) Делать рерайт текста - переписывать данный
текст, сохраняя его смысл, но используя другие слова и структуру.
Текст должен выглядеть оригинальным и естественным. 
2)Делать саммари текста - сокращать данный
текст, сохраняя ключевые идеи и мысли. Представляй результат в виде
краткого, но информативного изложения. Cокращай текст насколько возможно 
до 3-4 предложений, сохраняя его основную суть и ключевые факты.
Упрощай сложные фразы, убирай лишние детали, но не теряй смысл

Также ты можешь менять стиль и тональность текста по запросу пользователя и учитывать цели, с которыми
пользователь обращается к тебе.
"""


class LLMCaller:
    def __init__(self, settings: LLMSettings):
        self.sdk = YCloudML(folder_id=settings.YCLOUD_FOLDER_ID, auth=settings.YCLOUD_API_KEY)
        self.model = self.sdk.models.completions(settings.MODEL_NAME, model_version=settings.MODEL_VERSION)
        self.model.configure(temperature=settings.TEMPERATURE)

        try:
            self.assistant = self.sdk.assistants.get(settings.ASSISTANT_ID)
        except Exception:
            self.assistant = self.sdk.assistants.create(
                self.model,
                ttl_days=7,
                expiration_policy="since_last_active",
                instruction=assistant_instruction
            )
            update_assistant_in_config(self.assistant.id)

        # Предопределенные промпты
        self.prompts = {
            "rewrite": "Сделай рерайт текста:\n",
            "summary": "Сделай саммари текста:\n"
        }

    async def create_user_thread(self, user_id: int, ttl_days: int = 1) -> str:
        thread = await UserThreadsService.get_user_thread(user_id)
        thread_expired = thread.created + timedelta(days=ttl_days) < datetime.now() if thread else False
        if not thread or thread_expired:
            thread_name = f"User_{user_id}_Thread"
            new_thread = self.sdk.threads.create(
                name=thread_name,
                ttl_days=ttl_days,
                expiration_policy="static"
            )
            #todo тред может существовать но быть истечен
            thread = await UserThreadsService.create_user_thread(new_thread.id, user_id)
        return thread.thread_id

    async def process_text(self, user_id: int, text: str, operation_type: str,
                           custom_params: Dict[str, str] = None) -> str:
        # Ensure user has a thread
        thread_id = await self.create_user_thread(user_id)
        thread = self.sdk.threads.get(thread_id)

        # Get the base prompt
        prompt = self.prompts.get(operation_type, self.prompts["rewrite"])

        # Add custom parameters if provided
        if custom_params:
            for param_name, param_value in custom_params.items():
                if param_name == "tone":
                    prompt += f"Тональность текста: {param_value}. "
                elif param_name == "style":
                    prompt += f"Стиль текста: {param_value}. "
                elif param_name == "user_goals":
                    prompt += f"Цель использования: {param_value}. "

        # Combine prompt with the text
        full_prompt = prompt + text

        # Add to thread and run
        thread.write(full_prompt)
        run = self.assistant.run(thread)
        result = run.wait()

        return result.text

    async def rewrite_text(self, user_id: int, text: str, custom_params: Dict[str, str] = None) -> str:
        return await self.process_text(user_id, text, "rewrite", custom_params)

    async def summarize_text(self, user_id: int, text: str, custom_params: Dict[str, str] = None) -> str:
        return await self.process_text(user_id, text, "summary", custom_params)
