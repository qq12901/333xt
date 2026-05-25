"""
333交易系统 V2.0 - Web界面启动脚本

使用方法：
    python scripts/run_web.py

或使用Streamlit命令：
    streamlit run src/web/app.py
"""
import subprocess
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).parent.parent

# 检查依赖
try:
    import streamlit
except ImportError:
    print("❌ Streamlit未安装，正在安装...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    print("✅ Streamlit安装成功！")

try:
    import plotly
except ImportError:
    print("❌ Plotly未安装，正在安装...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
    print("✅ Plotly安装成功！")

# 启动Streamlit
print("\n" + "="*60)
print("333交易系统 V2.0 - Web可视化控制面板")
print("="*60)
print("\n🚀 正在启动Web界面...")
print(f"📁 项目路径: {project_root}")
print("\n启动后访问: http://localhost:8501")
print("按 Ctrl+C 停止服务")
print("="*60 + "\n")

# 使用streamlit运行
app_path = project_root / "src" / "web" / "app.py"
subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", "8501"])
