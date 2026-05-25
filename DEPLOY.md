# 🚀 333交易系统部署指南

## 在线部署（推荐）

### Streamlit Community Cloud（免费）

这是最简单的方式，您可以在2分钟内获得一个永久的在线访问地址！

#### 步骤 1: 准备GitHub仓库

确保您的代码已经推送到GitHub：

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/您的用户名/333-trading-system.git
git push -u origin main
```

#### 步骤 2: 部署到Streamlit Cloud

1. 访问: https://share.streamlit.io/deploy
2. 登录您的GitHub账号
3. 填写部署信息：
   - **Repository**: 选择您的333交易系统仓库
   - **Branch**: `main`
   - **Main file path**: `src/web/app.py`
4. 点击 **Deploy!** 按钮
5. 等待1-2分钟，部署完成！

#### 步骤 3: 获得在线地址

部署成功后，您会获得一个类似这样的地址：
```
https://your-username-333-trading-system.streamlit.app
```

您可以分享这个地址给任何人访问！

---

## 本地部署

### Windows

双击运行：
```
scripts\run_web.bat
```

### Linux/Mac

```bash
chmod +x scripts/run_web.sh
bash scripts/run_web.sh
```

### 手动启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
streamlit run src/web/app.py
```

访问地址：http://localhost:8501

---

## 其他部署选项

### Docker部署

创建 `Dockerfile`：
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "src/web/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

构建并运行：
```bash
docker build -t 333-trading-system .
docker run -p 8501:8501 333-trading-system
```

### 云服务器部署

1. 购买云服务器（阿里云、腾讯云、AWS等）
2. SSH连接到服务器
3. 安装Python和依赖
4. 使用systemd或supervisor管理进程
5. 配置Nginx反向代理（可选）

---

## 常见问题

### Q: Streamlit Cloud部署失败怎么办？
A: 检查以下几点：
- 确保requirements.txt文件存在
- 确保入口文件路径正确（src/web/app.py）
- 查看部署日志中的错误信息

### Q: 可以自定义域名吗？
A: Streamlit Cloud支持自定义域名，在设置中配置即可。

### Q: 在线版本的数据安全吗？
A: Streamlit Cloud是安全的，但建议不要在在线版本中使用真实资金。

### Q: 可以多人同时使用吗？
A: 可以！Streamlit支持多人同时访问，每个用户有独立的会话。

---

## 维护

### 更新在线版本

当您更新代码后：
1. 推送到GitHub
2. Streamlit Cloud会自动检测并重新部署
3. 通常只需几秒钟即可完成更新

### 监控

- Streamlit Cloud提供详细的日志
- 可以查看访问统计
- 设置环境变量和密钥

---

## 下一步

部署成功后，您可以：
- 📱 在手机上访问
- 🔗 分享给朋友体验
- 📊 进行策略回测
- 🎯 实时监控市场

祝您使用愉快！🎉
