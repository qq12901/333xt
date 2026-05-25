"""
333交易系统 - 多数据源管理器（调整优先级）

实现多数据源管理和自动切换功能，提供数据源优先级配置、自动容错切换、详细日志记录
"""
import logging
from typing import List, Optional, Type, List as TypeList
from .base import DataSource
from .eastmoney import EastMoneyDataSource
from .sina import SinaDataSource
from .tencent import TencentDataSource
from ..models.kline import Kline, KlineData


class MultiDataSourceManager(DataSource):
    """多数据源管理器"""

    def __init__(self, symbol: str, priority: Optional[List[Type[DataSource]]] = None):
        """
        初始化多数据源管理器

        Args:
            symbol: 交易标的代码
            priority: 数据源优先级列表，默认顺序为腾讯财经 > 东方财富 > 新浪财经
        """
        super().__init__(symbol)

        # 调整默认优先级：腾讯 > 东方财富 > 新浪
        if priority is None:
            self._data_source_classes = [
                TencentDataSource,
                EastMoneyDataSource,
                SinaDataSource
            ]
        else:
            self._data_source_classes = priority

        # 初始化数据源实例
        self._data_sources: List[DataSource] = []
        for ds_class in self._data_source_classes:
            try:
                self._data_sources.append(ds_class(symbol))
            except Exception as e:
                print(f"初始化数据源 {ds_class.__name__} 失败: {e}")

        # 当前使用的数据源索引
        self._current_index = 0

        # 设置日志记录器
        self.logger = logging.getLogger(__name__)
        self._setup_logger()

        # 初始化时选择第一个可用的数据源
        self._select_first_available()

    def _setup_logger(self) -> None:
        """设置日志记录器"""
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def _select_first_available(self) -> None:
        """选择第一个可用的数据源"""
        for i, ds in enumerate(self._data_sources):
            try:
                if ds.is_available():
                    self._current_index = i
                    self.logger.info(f"选择数据源: {self._data_source_classes[i].__name__}")
                    return
            except Exception as e:
                self.logger.warning(f"检查数据源 {self._data_source_classes[i].__name__} 失败: {e}")
                continue

        # 如果没有可用的数据源，使用第一个
        self._current_index = 0
        self.logger.warning(f"没有找到可用的数据源，使用默认数据源: {self._data_source_classes[0].__name__}")

    @property
    def current_data_source(self) -> DataSource:
        """获取当前使用的数据源"""
        return self._data_sources[self._current_index]

    @property
    def current_data_source_name(self) -> str:
        """获取当前使用的数据源名称"""
        return self._data_source_classes[self._current_index].__name__

    def _switch_to_next_available(self) -> bool:
        """
        切换到下一个可用的数据源

        Returns:
            是否成功切换
        """
        original_index = self._current_index

        for i in range(len(self._data_sources)):
            next_index = (self._current_index + 1 + i) % len(self._data_sources)
            try:
                if self._data_sources[next_index].is_available():
                    old_name = self._data_source_classes[self._current_index].__name__
                    new_name = self._data_source_classes[next_index].__name__
                    self._current_index = next_index
                    self.logger.warning(f"数据源切换: {old_name} -> {new_name}")
                    return True
            except Exception as e:
                self.logger.warning(f"检查数据源 {self._data_source_classes[next_index].__name__} 失败: {e}")
                continue

        self.logger.error("所有数据源切换失败，没有可用的数据源")
        return False

    def _execute_with_retry(self, method_name: str, *args, max_retries: int = 3, **kwargs):
        """
        执行方法并在失败时自动切换数据源重试（带指数退避）

        Args:
            method_name: 要执行的方法名
            *args: 位置参数
            max_retries: 每个数据源最大重试次数
            **kwargs: 关键字参数

        Returns:
            方法执行结果
        """
        import time

        last_exception = None
        attempt_count = 0

        for data_source_attempt in range(len(self._data_sources)):
            try:
                ds = self.current_data_source
                method = getattr(ds, method_name)

                # 对当前数据源尝试max_retries次
                for retry in range(max_retries):
                    try:
                        result = method(*args, **kwargs)
                        if retry > 0:
                            self.logger.info(f"重试成功（第{retry+1}次尝试）")
                        return result
                    except Exception as retry_error:
                        attempt_count += 1
                        if retry < max_retries - 1:
                            wait_time = (2 ** retry) * 0.5  # 指数退避：0.5s, 1s, 2s
                            self.logger.warning(
                                f"数据源 {self.current_data_source_name} "
                                f"方法 {method_name} 第{retry+1}次重试失败: {retry_error}, "
                                f"{wait_time}秒后重试..."
                            )
                            time.sleep(wait_time)
                        else:
                            raise retry_error

            except Exception as e:
                last_exception = e
                self.logger.error(
                    f"数据源 {self.current_data_source_name} 执行 {method_name} 失败: {e}",
                    exc_info=True
                )
                if not self._switch_to_next_available():
                    break

        error_msg = f"所有数据源执行失败（总共尝试{attempt_count}次）: {last_exception}"
        self.logger.error(error_msg)
        raise last_exception or Exception(error_msg)

    def fetch_klines(self, count: int = 100) -> List[Kline]:
        """
        获取K线数据，支持自动切换数据源

        Args:
            count: 获取数量

        Returns:
            K线数据列表
        """
        try:
            klines = self._execute_with_retry("fetch_klines", count)
            self.update_cache(klines)
            return klines
        except Exception as e:
            self.logger.error(f"获取K线数据失败，所有数据源都不可用: {e}")
            return []

    def fetch_history(self, start_time: int, end_time: int) -> List[Kline]:
        """
        获取历史K线数据，支持自动切换数据源

        Args:
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）

        Returns:
            K线数据列表
        """
        try:
            klines = self._execute_with_retry("fetch_history", start_time, end_time)
            self.update_cache(klines)
            return klines
        except Exception as e:
            self.logger.error(f"获取历史K线数据失败，所有数据源都不可用: {e}")
            return []

    def get_realtime_quote(self) -> Optional[dict]:
        """
        获取实时行情，支持自动切换数据源

        Returns:
            实时行情数据
        """
        try:
            return self._execute_with_retry("get_realtime_quote")
        except Exception as e:
            self.logger.error(f"获取实时行情失败，所有数据源都不可用: {e}")
            return None

    def is_available(self) -> bool:
        """
        检查是否有可用的数据源

        Returns:
            是否有可用的数据源
        """
        for ds in self._data_sources:
            try:
                if ds.is_available():
                    return True
            except Exception:
                continue
        return False

    def get_cached_klines(self) -> KlineData:
        """
        获取缓存的K线数据，使用当前数据源的缓存

        Returns:
            K线数据集合
        """
        return self.current_data_source.get_cached_klines()

    def clear_cache(self) -> None:
        """清空所有数据源的缓存"""
        for ds in self._data_sources:
            ds.clear_cache()
        super().clear_cache()

    def get_data_source_health_status(self) -> dict:
        """
        获取所有数据源的健康状态

        Returns:
            健康状态字典
        """
        health_status = {
            "current_source": self.current_data_source_name,
            "all_sources": [],
            "healthy_count": 0,
            "total_count": len(self._data_sources)
        }

        for i, ds in enumerate(self._data_sources):
            source_name = self._data_source_classes[i].__name__
            try:
                is_available = ds.is_available()
                health_status["all_sources"].append({
                    "name": source_name,
                    "available": is_available,
                    "current": (i == self._current_index)
                })
                if is_available:
                    health_status["healthy_count"] += 1
            except Exception as e:
                health_status["all_sources"].append({
                    "name": source_name,
                    "available": False,
                    "error": str(e),
                    "current": (i == self._current_index)
                })

        return health_status
