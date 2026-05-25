@echo off
echo ========================================
echo 333交易系统 - Web界面启动
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python检测通过

REM 检查依赖是否安装
echo.
echo 📦 检查依赖...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  依赖未安装，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
    echo ✅ 依赖安装完成
) else (
    echo ✅ 依赖已安装
)

echo.
echo 🚀 启动333交易系统Web界面...
echo.
echo 💡 访问地址: http://localhost:8501
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

streamlit run src/web/app.py

pause
