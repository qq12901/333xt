"""
333交易系统 - 后台服务管理器

实现守护进程模式、IPC通信、状态管理等功能
"""
import os
import sys
import time
import json
import signal
import socket
import threading
import traceback
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from pathlib import Path

# 服务状态枚举
class ServiceStatus:
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"

class ServiceManager:
    """后台服务管理器"""
    
    def __init__(self, service_name: str = "trading_system"):
        self.service_name = service_name
        self.status = ServiceStatus.STOPPED
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.error: Optional[Exception] = None
        
        # IPC相关
        self.ipc_socket: Optional[socket.socket] = None
        self.ipc_thread: Optional[threading.Thread] = None
        self.ipc_port = 8888
        self.ipc_running = False
        
        # 配置路径
        self.base_dir = Path(__file__).parent.parent.parent
        self.pid_file = self.base_dir / "run" / f"{service_name}.pid"
        self.log_file = self.base_dir / "logs" / f"{service_name}.log"
        self.status_file = self.base_dir / "run" / f"{service_name}.status"
        
        # 确保目录存在
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
        # 服务回调
        self.on_start: Optional[Callable] = None
        self.on_stop: Optional[Callable] = None
        self.on_tick: Optional[Callable] = None
    
    def _log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
        
        if level in ["ERROR", "CRITICAL"]:
            print(log_line.strip())
    
    def _write_pid(self):
        """写入PID文件"""
        with open(self.pid_file, "w") as f:
            f.write(str(os.getpid()))
    
    def _remove_pid(self):
        """移除PID文件"""
        if self.pid_file.exists():
            self.pid_file.unlink()
    
    def _read_pid(self) -> Optional[int]:
        """读取PID"""
        if self.pid_file.exists():
            with open(self.pid_file, "r") as f:
                try:
                    return int(f.read().strip())
                except:
                    return None
        return None
    
    def _write_status(self, status: str):
        """写入状态文件"""
        status_data = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "pid": os.getpid() if self.status == ServiceStatus.RUNNING else None
        }
        with open(self.status_file, "w", encoding="utf-8") as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)
    
    def _handle_signal(self, signum, frame):
        """处理系统信号"""
        self._log(f"收到信号 {signum}，准备停止服务")
        self.stop()
    
    def is_running(self) -> bool:
        """检查服务是否正在运行"""
        pid = self._read_pid()
        if pid is None:
            return False
        
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            self._remove_pid()
            return False
    
    def _ipc_handler(self):
        """IPC服务器处理循环"""
        while self.ipc_running:
            try:
                conn, addr = self.ipc_socket.accept()
                self._log(f"IPC连接来自 {addr}")
                
                try:
                    data = conn.recv(1024).decode('utf-8')
                    if not data:
                        continue
                    
                    response = self._handle_ipc_command(data)
                    conn.sendall(json.dumps(response).encode('utf-8'))
                except Exception as e:
                    self._log(f"IPC处理错误: {e}", "ERROR")
                finally:
                    conn.close()
            except Exception as e:
                if self.ipc_running:
                    self._log(f"IPC服务器错误: {e}", "ERROR")
                time.sleep(1)
    
    def _handle_ipc_command(self, command: str) -> Dict[str, Any]:
        """处理IPC命令"""
        try:
            cmd = json.loads(command)
            action = cmd.get("action", "")
            
            if action == "status":
                return {
                    "success": True,
                    "data": {
                        "status": self.status,
                        "pid": os.getpid(),
                        "service": self.service_name
                    }
                }
            
            elif action == "stop":
                self.stop()
                return {"success": True, "message": "服务已停止"}
            
            elif action == "restart":
                self.stop()
                time.sleep(2)
                self.start()
                return {"success": True, "message": "服务已重启"}
            
            elif action == "ping":
                return {"success": True, "message": "pong"}
            
            else:
                return {"success": False, "message": f"未知命令: {action}"}
                
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def _start_ipc_server(self):
        """启动IPC服务器"""
        try:
            self.ipc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ipc_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.ipc_socket.bind(('127.0.0.1', self.ipc_port))
            self.ipc_socket.listen(5)
            self.ipc_socket.settimeout(1.0)
            
            self.ipc_running = True
            self.ipc_thread = threading.Thread(target=self._ipc_handler, daemon=True)
            self.ipc_thread.start()
            self._log(f"IPC服务器启动，端口: {self.ipc_port}")
        except Exception as e:
            self._log(f"IPC服务器启动失败: {e}", "ERROR")
    
    def _stop_ipc_server(self):
        """停止IPC服务器"""
        self.ipc_running = False
        if self.ipc_socket:
            try:
                self.ipc_socket.close()
            except:
                pass
        if self.ipc_thread:
            self.ipc_thread.join(timeout=2)
        self._log("IPC服务器已停止")
    
    def _main_loop(self):
        """主循环"""
        self._log("服务主循环启动")
        
        try:
            if self.on_start:
                self.on_start()
            
            while self.running:
                if self.on_tick:
                    try:
                        self.on_tick()
                    except Exception as e:
                        self._log(f"tick回调错误: {e}", "ERROR")
                
                time.sleep(1)
                
        except Exception as e:
            self._log(f"主循环错误: {e}", "CRITICAL")
            traceback.print_exc()
            self.error = e
            self.status = ServiceStatus.ERROR
        
        finally:
            if self.on_stop:
                try:
                    self.on_stop()
                except Exception as e:
                    self._log(f"stop回调错误: {e}", "ERROR")
    
    def start(self, daemon: bool = False):
        """
        启动服务
        
        Args:
            daemon: 是否以守护进程模式运行
        """
        if self.is_running():
            self._log("服务已在运行中")
            return
        
        if daemon:
            self._daemonize()
        
        self._log("启动服务...")
        self.status = ServiceStatus.STARTING
        self._write_status(self.status)
        self._write_pid()
        
        self.running = True
        self.thread = threading.Thread(target=self._main_loop, daemon=False)
        self.thread.start()
        
        # 启动IPC服务器
        self._start_ipc_server()
        
        self.status = ServiceStatus.RUNNING
        self._write_status(self.status)
        self._log("服务启动成功")
        
        # 等待线程结束
        if self.thread:
            self.thread.join()
    
    def _daemonize(self):
        """守护进程化"""
        # 创建子进程
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
        
        # 创建新会话
        os.setsid()
        
        # 再次fork脱离终端
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
        
        # 重定向标准输入输出
        sys.stdout = open('/dev/null', 'w')
        sys.stderr = open('/dev/null', 'w')
        sys.stdin = open('/dev/null', 'r')
        
        # 更改工作目录
        os.chdir('/')
        
        # 设置文件权限掩码
        os.umask(0)
    
    def stop(self):
        """停止服务"""
        if not self.running:
            self._log("服务未运行")
            return
        
        self._log("停止服务...")
        self.status = ServiceStatus.STOPPING
        self._write_status(self.status)
        
        self.running = False
        
        # 停止IPC服务器
        self._stop_ipc_server()
        
        # 等待主线程结束
        if self.thread:
            self.thread.join(timeout=10)
        
        self.status = ServiceStatus.STOPPED
        self._write_status(self.status)
        self._remove_pid()
        self._log("服务停止成功")
    
    def restart(self):
        """重启服务"""
        self.stop()
        time.sleep(2)
        self.start()
    
    @classmethod
    def send_command(cls, action: str, port: int = 8888) -> Dict[str, Any]:
        """
        发送命令到运行中的服务
        
        Args:
            action: 命令动作
            port: IPC端口
            
        Returns:
            响应数据
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', port))
            sock.sendall(json.dumps({"action": action}).encode('utf-8'))
            
            response = sock.recv(1024).decode('utf-8')
            sock.close()
            
            return json.loads(response)
        except ConnectionRefusedError:
            return {"success": False, "message": "服务未运行或IPC端口未开启"}
        except Exception as e:
            return {"success": False, "message": str(e)}
