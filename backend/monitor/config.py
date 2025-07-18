import logging

SEND_TIMEOUT = 1  # 每 10 秒執行一次

# Logger
logger = logging.getLogger("monitor")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
