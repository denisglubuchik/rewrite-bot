from yandex_cloud_ml_sdk import YCloudML

from bot.core.config import settings

sdk = YCloudML(folder_id=settings.YCLOUD_FOLDER_ID, auth=settings.YCLOUD_API_KEY)
model = sdk.models.completions("yandexgpt", model_version="rc")
model.configure(temperature=0.5)

async def send_message_to_model(message: str, prompt: str):
    result = model.run(prompt + message)
    return result.alternatives[0].text
