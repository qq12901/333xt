
@echo off
echo ========================================
echo 333交易系统 - 最后步骤完成！
echo ========================================
echo.
echo ✅ 本地仓库已全部准备好！
echo.
echo 现在只需完成最后一步：
echo.
echo 1. 访问: https://github.com/new
echo.
echo 2. 填写：
echo    - Repository name: 333xt
echo    - Public/Private: 您选择
echo    - ^(不要勾选 Add a README / .gitignore / License)
echo.
echo 3. 点击 Create repository
echo.
echo 4. 复制您的仓库URL
echo.
echo 5. 回来粘贴到下面：
echo.

set /p REPO_URL=请输入您的GitHub仓库URL:
echo.

"C:\Program Files\Git\bin\git.exe" remote add origin %REPO_URL%
echo.
echo 正在推送到GitHub...
echo.

"C:\Program Files\Git\bin\git.exe" push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo ✅ 上传成功！
    echo ========================================
    echo.
    echo 访问您的仓库：
    echo %REPO_URL%
) else (
    echo.
    echo ❌ 推送失败，请检查仓库URL是否正确
)
echo.
pause
