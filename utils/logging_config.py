import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
    file_level: int = logging.DEBUG
) -> None:
    """
    設置日誌配置

    Args:
        level: 控制台日誌等級，默認INFO
        log_file: 日誌文件名，如果為None則自動生成
        log_dir: 日誌目錄路徑，默認為'logs'
        file_level: 文件日誌等級，默認DEBUG
    """
    # 創建根日誌記錄器
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # 設置為最低級別，讓處理器決定要顯示的級別

    # 清除現有的處理器
    logger.handlers = []

    # 創建格式化器-控制台輸出
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    # 創建格式化器-寫入日誌檔案
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 設置控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 如果指定了日誌文件，設置文件處理器
    if log_file or log_dir:

        # 設置日誌目錄
        log_path = Path(log_dir) if log_dir else Path('logs')
        log_path.mkdir(parents=True, exist_ok=True)

        # 如果沒有指定日誌文件名，生成一個
        if not log_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = f'scraper_{timestamp}.log'

        # 創建文件處理器
        log_file_path = log_path / (log_file or 'app.log')
        file_handler = logging.FileHandler(
            log_file_path,
            encoding='utf-8'
        )

        file_handler.setLevel(file_level)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    獲取指定名稱的日誌記錄器

    Args:
        name: 日誌記錄器名稱

    Returns:
        logging.Logger: 配置好的日誌記錄器
    """
    return logging.getLogger(name)


# 日誌等級映射，方便配置文件使用
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


class LoggerManager:
    """日誌管理器，用於集中管理所有爬蟲的日誌配置"""

    def __init__(self):
        self._loggers = {}

    def get_logger(self, name: str) -> logging.Logger:
        """
        獲取或創建日誌記錄器

        Args:
            name: 日誌記錄器名稱

        Returns:
            logging.Logger: 配置好的日誌記錄器
        """
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        return self._loggers[name]

    def set_level(self, name: str, level: str) -> None:
        """
        設置指定日誌記錄器的等級

        Args:
            name: 日誌記錄器名稱
            level: 日誌等級（'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'）
        """
        logger = self.get_logger(name)
        logger.setLevel(LOG_LEVELS[level.upper()])


# 創建全局日誌管理器實例
logger_manager = LoggerManager()
