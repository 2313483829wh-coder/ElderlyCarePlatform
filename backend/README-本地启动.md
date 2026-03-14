# 后端本地启动（无需 Docker）

本后端需要 **Python 3.10 或以上**。若你当前 venv 是 Python 3.5，需先安装新版本 Python 并重建环境。

---

## 第一步：安装 Python 3.11

1. 打开 https://www.python.org/downloads/
2. 下载 **Python 3.11.x** 的 Windows 安装包
3. 安装时**务必勾选** “Add Python to PATH”
4. 安装完成后，**新开一个终端**，执行 `py -3.11 --version` 或 `python --version` 确认版本 ≥ 3.10

---

## 第二步：重建虚拟环境并安装依赖

在项目根目录打开 PowerShell 或 CMD，执行：

```powershell
cd A:\vscode\ProjectMune\ElderlyCarePlatform\backend

# 删除旧 venv（Python 3.5 的）
Remove-Item -Recurse -Force venv -ErrorAction SilentlyContinue

# 用 Python 3.11 创建新 venv（若命令是 python 且已是 3.11，可直接 python -m venv venv）
py -3.11 -m venv venv

# 激活并安装依赖
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

若系统里没有 `py -3.11`，可用 `python3 -m venv venv` 或 `C:\Users\你的用户名\AppData\Local\Programs\Python\Python311\python.exe -m venv venv`（路径按实际安装为准）。

---

## 第三步：启动后端

```powershell
# 仍在 backend 目录且已激活 venv 时
python manage.py runserver 8000
```

看到 `Starting development server at http://127.0.0.1:8000/` 后，在浏览器打开前端 http://localhost:5173/ 即可。

---

## 可选：用脚本一键重建 venv

若已安装 Python 3.11 且 `py -3.11` 可用，可在 **backend** 目录执行：

```powershell
.\重建venv并安装.ps1
```

然后执行 `python manage.py runserver 8000` 启动。
