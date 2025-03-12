import os


async def process_text_file(file_path) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        return text
    finally:
        os.remove(file_path)
