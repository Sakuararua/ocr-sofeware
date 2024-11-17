import logging

# 配置日志记录
logging.basicConfig(
    filename='ocr_process.log',
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_error(message):
    logging.error(message)
