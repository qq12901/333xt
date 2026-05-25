# 333交易系统 - GitHub自动化上传脚本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "333交易系统 - GitHub自动上传" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Git
Write-Host "[1/7] 检查Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "   ✅ Git已安装: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ 未找到Git，请先安装Git" -ForegroundColor Red
    Read-Host "按Enter退出"
    exit 1
}

# 检查项目目录
Write-Host "[2/7] 检查项目目录..." -ForegroundColor Yellow
if (-not (Test-Path "src\main.py")) {
    Write-Host "   ❌ 请在项目根目录 e:\333xt 下运行此脚本" -ForegroundColor Red
    Read-Host "按Enter退出"
    exit 1
}
Write-Host "   ✅ 项目目录正确" -ForegroundColor Green

# 配置Git用户
Write-Host "[3/7] 配置Git用户..." -ForegroundColor Yellow
$name = git config --global user.name
$email = git config --global user.email

if (-not $name -or -not $email) {
    Write-Host ""
    Write-Host "   首次使用，需要配置Git用户信息" -ForegroundColor Yellow
    $name = Read-Host "   请输入您的GitHub用户名"
    $email = Read-Host "   请输入您的GitHub邮箱"
    git config --global user.name $name
    git config --global user.email $email
    Write-Host "   ✅ Git用户配置完成" -ForegroundColor Green
} else {
    Write-Host "   ✅ Git用户已配置: $name <$email>" -ForegroundColor Green
}

# 初始化Git仓库
Write-Host "[4/7] 初始化Git仓库..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "   ✅ Git仓库已存在" -ForegroundColor Green
} else {
    git init | Out-Null
    Write-Host "   ✅ Git仓库初始化完成" -ForegroundColor Green
}

# 添加文件
Write-Host "[5/7] 添加项目文件..." -ForegroundColor Yellow
git add . | Out-Null
Write-Host "   ✅ 文件已添加" -ForegroundColor Green

# 提交
Write-Host "[6/7] 提交更改..." -ForegroundColor Yellow
git commit -m "Initial commit: 333 trading system" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ 提交完成" -ForegroundColor Green
} else {
    Write-Host "   ⚠️ 没有新文件需要提交（或已提交过）" -ForegroundColor Yellow
}

# 远程仓库
Write-Host "[7/7] 关联GitHub仓库..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "请在GitHub创建仓库后继续" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "请按以下步骤操作：" -ForegroundColor White
Write-Host ""
Write-Host "1. 访问: https://github.com/new" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. 填写：" -ForegroundColor White
Write-Host "   - Repository name: 333xt" -ForegroundColor Green
Write-Host "   - Public/Private: 您选择" -ForegroundColor White
Write-Host "   - ⚠️  不要勾选 Add a README" -ForegroundColor Red
Write-Host "   - ⚠️  不要勾选 Add .gitignore" -ForegroundColor Red
Write-Host "   - ⚠️  不要勾选 Choose a license" -ForegroundColor Red
Write-Host ""
Write-Host "3. 点击 Create repository" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. 复制仓库URL（类似：https://github.com/用户名/333xt.git）" -ForegroundColor White
Write-Host ""

$repoUrl = Read-Host "请粘贴您的GitHub仓库URL"

if (-not $repoUrl) {
    Write-Host "❌ URL不能为空" -ForegroundColor Red
    Read-Host "按Enter退出"
    exit 1
}

# 添加远程仓库
git remote remove origin 2>&1 | Out-Null
git remote add origin $repoUrl
git branch -M main

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "开始推送到GitHub..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ 上传成功！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "访问您的仓库：" -ForegroundColor Yellow
    Write-Host $repoUrl -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ 推送失败" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能原因：" -ForegroundColor Yellow
    Write-Host "1. 仓库URL不正确"
    Write-Host "2. GitHub认证失败"
    Write-Host "3. 网络问题"
    Write-Host ""
    Write-Host "提示：如果使用HTTPS，可能需要用Personal Access Token" -ForegroundColor Yellow
    Write-Host ""
}

Read-Host "按Enter退出"
