"""
333交易系统 - 交易日志系统

实现完整的交易日志记录功能
"""
import sys
from pathlib import Path
if __name__ != "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
import json
from datetime import datetime
from typing import Optional
from config.settings import LOGS_DIR


class TradingLogger:
    """交易日志记录器"""
    
    def __init__(self, name: str = "333_trading"):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """设置日志处理器"""
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            log_file = LOGS_DIR / f"trading_{datetime.now().strftime('%Y%m%d')}.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs) -> None:
        """记录信息日志"""
        self.logger.info(self._format_message(message, **kwargs))
    
    def warning(self, message: str, **kwargs) -> None:
        """记录警告日志"""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message: str, **kwargs) -> None:
        """记录错误日志"""
        self.logger.error(self._format_message(message, **kwargs))
    
    def debug(self, message: str, **kwargs) -> None:
        """记录调试日志"""
        self.logger.debug(self._format_message(message, **kwargs))
    
    def _format_message(self, message: str, **kwargs) -> str:
        """格式化日志消息"""
        if kwargs:
            extra_info = json.dumps(kwargs, ensure_ascii=False)
            return f"{message} | {extra_info}"
        return message
    
    def log_signal(self, signal: dict) -> None:
        """记录交易信号"""
        self.info(f"信号触发: {signal.get('signal_name', '未知')}", signal=signal)
    
    def log_trade(self, trade: dict) -> None:
        """记录交易执行"""
        self.info(
            f"交易执行: {trade.get('action_name', '未知')} "
            f"{trade.get('symbol', '')} "
            f"价格:{trade.get('price', 0)} "
            f"数量:{trade.get('quantity', 0)}",
            trade=trade
        )
    
    def log_position(self, position: dict) -> None:
        """记录持仓变化"""
        self.info(f"持仓变化: {position}", position=position)
    
    def log_system(self, event: str, details: Optional[dict] = None) -> None:
        """记录系统事件"""
        self.info(f"系统事件: {event}", event=event, details=details or {})
    
    def log_error_with_trace(self, error: Exception, context: Optional[dict] = None) -> None:
        """记录错误及追踪"""
        self.error(
            f"错误发生: {str(error)}",
            error_type=type(error).__name__,
            error_message=str(error),
            context=context or {}
        )
        self.logger.exception(error)


class SignalLogger:
    """信号日志记录器"""
    
    def __init__(self, log_dir: Optional[Path] = None):
        """
        初始化信号日志记录器
        
        Args:
            log_dir: 日志目录
        """
        self.log_dir = log_dir or LOGS_DIR / "signals"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.signal_log_file = self.log_dir / f"signals_{datetime.now().strftime('%Y%m%d')}.jsonl"
    
    def log_signal(self, signal_data: dict) -> None:
        """
        记录信号到JSONL文件
        
        Args:
            signal_data: 信号数据
        """
        signal_data['logged_at'] = datetime.now().isoformat()
        
        with open(self.signal_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(signal_data, ensure_ascii=False) + '\n')
    
    def log_trade(self, trade_data: dict) -> None:
        """
        记录交易到JSONL文件
        
        Args:
            trade_data: 交易数据
        """
        trade_data['logged_at'] = datetime.now().isoformat()
        
        trade_log_file = self.log_dir / f"trades_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        with open(trade_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(trade_data, ensure_ascii=False) + '\n')
    
    def log_system_event(self, event_type: str, event_data: dict) -> None:
        """
        记录系统事件
        
        Args:
            event_type: 事件类型
            event_data: 事件数据
        """
        event_data['event_type'] = event_type
        event_data['logged_at'] = datetime.now().isoformat()
        
        system_log_file = self.log_dir / f"system_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        with open(system_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event_data, ensure_ascii=False) + '\n')
