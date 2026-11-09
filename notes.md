# 踩坑记录

## 1. pytest 报「空套件 / collected 0 items」

- **现象**：文件命名是 `test_01.py`，pytest 却显示 `collected 0 items`，退出码 5
- **原因**：文件里只有模块级代码和 `if __name__ == "__main__"` 块，没有任何 `test_` 开头的函数。
  pytest 是 **import** 模块而不是运行脚本，此时 `__name__` 不等于 `"__main__"`，所以那个块根本不执行
- **解法**：函数名改成 `test_xxx`；用 `assert` 代替 `print`；入口逻辑不需要写

## 2. PyCharm 里 import requests 报 ModuleNotFoundError

- **现象**：明明在设置里选了根目录的 `.venv` 解释器，一运行还是找不到包
- **原因**：`demo` 目录下有 `pyproject.toml` + `uv.lock`，PyCharm 把它当成**独立的 uv 项目**，
  自动用 `uv run` 启动了它自己那个空的 `.venv`。项目级解释器设置在这种情况下不生效
- **解法**：删掉子目录里的 `pyproject.toml`、`uv.lock`、`.venv`、`.idea`，重启 PyCharm，
  统一使用根目录的 `E:\workspace\.venv`
- **识别方法**：看运行命令，出现 `uv.exe run` 或路径里有子目录的 `.venv` 就是这个问题

## 3. git add 提示 LF will be replaced by CRLF

- **现象**：每次 `git add` 新文件都刷这条警告

- **原因**：Windows 上 `core.autocrlf=true`，提交时把 CRLF 转成 LF 存储，检出时再转回来。
  这是 Git 的跨平台设计，**不是错误**
  
- **解法**：加 `.gitattributes`，写 `* text=auto eol=lf`，统一用 LF，警告消失

  今天完成了git闭环
