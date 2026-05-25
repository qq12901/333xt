@echo off
echo ========================================
echo 333交易系统 - GitHub自动上传脚本
echo ========================================
echo.

REM 检查Git是否可用
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Git命令
    echo.
    echo 请确保:
    echo 1. 已安装Git for Windows
    echo 2. 已重启命令提示符/终端
    echo.
    pause
    exit /b 1
)

echo ✅ Git检测成功
echo.

REM 检查是否在正确目录
if not exist "src\main.py" (
    echo ❌ 错误: 请在项目根目录 e:\333xt 下运行此脚本
    pause
    exit /b 1
)

echo ✅ 项目目录正确
echo.

REM 配置Git用户（如果未配置）
echo [1/6] 检查Git配置...
git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo 请输入您的GitHub用户名:
    set /p GIT_NAME=
    echo 请输入您的GitHub邮箱:
    set /p GIT_EMAIL=
    git config --global user.name "%GIT_NAME%"
    git config --global user.email "%GIT_EMAIL%"
    echo ✅ Git用户配置完成
) else (
    echo ✅ Git用户已配置
)
echo.

REM 初始化仓库
echo [2/6] 初始化Git仓库...
if exist ".git" (
    echo ✅ Git仓库已存在
) else (
    git init
    echo ✅ Git仓库初始化完成
)
echo.

REM 添加文件
echo [3/6] 添加项目文件...
git add .
echo ✅ 文件已添加
echo.

REM 提交
echo [4/6] 提交更改...
git commit -m "Initial commit: 333 trading system" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  没有新文件需要提交（或已提交过）
) else (
    echo ✅ 提交完成
)
echo.

REM 检查远程仓库
echo [5/6] 检查远程仓库...
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo ⚠️  需要先在GitHub创建仓库
    echo ========================================
    echo.
    echo 请按以下步骤操作:
    echo.
    echo 1. 访问: https://github.com/new
    echo.
    echo 2. 填写信息:
    echo    - Repository name: 333xt
    echo    - Public/Private: 您选择
    echo    - ⚠️  不要勾选 "Add a README"
    echo    - ⚠️  不要勾选 "Add .gitignore"
    echo    - ⚠️  不要勾选 "Choose a license"
    echo.
    echo 3. 点击 "Create repository"
    echo.
    echo 4. 复制您的仓库URL，粘贴到下面:
    echo    (格式类似: https://github.com/您的用户名/333xt.git)
    echo.
    set /p REPO_URL=请输入您的GitHub仓库URL:
    
    if "%REPO_URL%"=="" (
        echo ❌ URL不能为空
        pause
        exit /b 1
    )
    
    git remote add origin "%REPO_URL%"
    echo ✅ 远程仓库已添加
) else (
    echo ✅ 远程仓库已配置
)
echo.

REM 推送到GitHub
echo [6/6] 推送到GitHub...
echo.
echo 正在推送... 这可能需要一些时间
echo.
git branch -M main
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo ✅ 上传成功！
    echo ========================================
    echo.
    echo 访问您的仓库查看:
    git remote get-url origin
) else (
    echo.
    echo ❌ 推送失败
    echo.
    echo 可能原因:
    echo 1. 仓库URL不正确
    echo 2. GitHub认证失败
    echo 3. 网络问题
    echo.
    echo 建议:
    echo - 检查仓库URL是否正确
    echo - 如果使用HTTPS，可能需要Personal Access Token
    echo - 或者考虑使用SSH Key
    echo.
)

echo.
pause
