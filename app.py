#!/usr/bin/env python
"""333交易系统 - 主入口文件 (Streamlit Cloud部署专用)"""
import sys
from pathlib import Path

# 正确设置项目路径 - 兼容各种部署环境
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 导入并运行主应用
from src.web.app import main

if __name__ == "__main__":
    main()
