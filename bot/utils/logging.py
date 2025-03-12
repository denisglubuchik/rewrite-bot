# bot/utils/logging.py

import logging


def setup_logging_base_config():
    """
    Настраивает базовую конфигурацию логирования.
    """

    # Настройка базового конфигурации логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler()  # Вывод логов в консоль
        ]
    )