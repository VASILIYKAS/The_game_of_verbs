import logging
import os
import traceback
from logging.handlers import RotatingFileHandler
from telegram import Bot
from dotenv import load_dotenv
from textwrap import dedent


class LogHandler(logging.Handler):

    def __init__(self):
        super().__init__()

        load_dotenv()

        token = os.environ['SEND_LOG_BOT_TOKEN']
        if not token:
            dedent("""
                Ошибка: Не указан SEND_LOG_BOT_TOKEN.
                Убедитесь, что он задан в переменных окружения.
            """)

        self.bot = Bot(token=token)
        self.chat_id = os.getenv('chat_id')

    def emit(self, record):
        try:
            formatted_record = self.format(record)
            if record.exc_info:
                text = '\n'.join(traceback.format_exception(*record.exc_info))
                formatted_record += f"\nTraceback:\n{text}"

            self.bot.send_message(
                chat_id=self.chat_id,
                text=formatted_record,
                parse_mode=None
            )

        except Exception as e:
            print(f"Ошибка при отправке лога: {e}")


def create_logs_dir(logs_dir):
    os.makedirs(logs_dir, exist_ok=True)


def create_log_file(logs_dir, log_file):
    log_path = os.path.join(logs_dir, log_file)

    log_file = RotatingFileHandler(
        filename=log_path,
        maxBytes=1024*1024,
        backupCount=3,
        encoding='utf-8'
    )

    return log_file


def setup_logger(name, logs_dir, log_file):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    create_logs_dir(logs_dir)
    file_handler = create_log_file(logs_dir, log_file)

    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    telegram_handler = LogHandler()
    telegram_handler.setLevel(logging.ERROR)

    logger.addHandler(file_handler)
    logger.addHandler(telegram_handler)

    return logger