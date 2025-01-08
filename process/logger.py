import logging
import os
import sys
from logging.handlers import RotatingFileHandler

class CustomFormatter(logging.Formatter):
    """自定义格式化器，用于控制台输出"""
    def format(self, record):
        # 控制台只输出消息内容，不包含其他信息
        return record.getMessage()

def setup_logger(name='weread_helper'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 确保日志目录存在
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 文件处理器 - 包含完整日志信息
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'weread_helper.log'),
        maxBytes=1024*1024,  # 1MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # 控制台处理器 - 只包含消息内容
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = CustomFormatter()
    console_handler.setFormatter(console_formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 创建全局logger实例
logger = setup_logger()
