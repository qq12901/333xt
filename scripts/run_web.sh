#!/bin/bash

echo "========================================"
echo "333交易系统 - Web界面启动"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

echo "✅ Python检测通过"

# 检查依赖是否安装
echo ""
echo "📦 检查依赖..."
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "⚠️  依赖未安装，正在安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖已安装"
fi

echo ""
echo "🚀 启动333交易系统Web界面..."
echo ""
echo "💡 访问地址: http://localhost:8501"
echo ""
echo "按 Ctrl+C 停止服务"
echo "========================================"
echo ""

streamlit run src/web/app.py
