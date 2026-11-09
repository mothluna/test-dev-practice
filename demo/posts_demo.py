"""第 1 周案例：拉取 JSONPlaceholder 的 posts，分页、容错、落盘。

演示一条链：
    requests 发请求 -> 异常处理不崩 -> 函数复用 -> 类做组织 -> 文件落盘
"""
import json
import time
from pathlib import Path

import requests


# ---------- 5. 文件读写：把结果从内存挪到磁盘 ----------
def save_json(data, path):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[保存] {p} 共 {len(data)} 条")


# ---------- 4. 类：把"同一个系统的接口"收拢在一起 ----------
class PostsAPI:
    def __init__(self, base_url, timeout=10, retries=3):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        # Session 复用连接，比每次新建快，也能保持 cookie
        self.session = requests.Session()

    # ---------- 2. 异常处理：出错不崩，重试后仍失败才抛 ----------
    def _request(self, path, params=None):
        url = f"{self.base_url}{path}"
        last_error = None

        for attempt in range(1, self.retries + 1):
            try:
                r = self.session.get(url, params=params, timeout=self.timeout)
                r.raise_for_status()          # 4xx/5xx 主动抛 HTTPError
                return r.json()
            except requests.exceptions.Timeout as e:
                last_error = e
                print(f"  [重试 {attempt}/{self.retries}] 超时")
            except requests.exceptions.ConnectionError as e:
                last_error = e
                print(f"  [重试 {attempt}/{self.retries}] 连不上")
            except requests.exceptions.HTTPError as e:
                # HTTP 错误重试通常没用，直接抛
                raise RuntimeError(f"HTTP 错误: {url} -> {e}") from e
            time.sleep(1)

        raise RuntimeError(f"重试 {self.retries} 次仍失败: {url}") from last_error

    # ---------- 3. 函数：一个接口 = 一个方法，参数化 ----------
    def get_posts(self, limit=10, start=0):
        return self._request("/posts", params={"_limit": limit, "_start": start})

    def get_all_posts(self, total=30, page_size=10):
        """翻页拉全：这里就是 D2 练的分页逻辑。"""
        all_posts = []
        for start in range(0, total, page_size):
            page = self.get_posts(limit=page_size, start=start)
            if not page:
                break
            all_posts.extend(page)
            print(f"  [分页] start={start} 累计 {len(all_posts)} 条")
        return all_posts


# ---------- 1. requests：最小的发请求 ----------
def demo_single_request():
    print("\n=== 1) 最小请求 ===")
    r = requests.get("https://jsonplaceholder.typicode.com/posts/1", timeout=10)
    print("状态码:", r.status_code)
    print("响应时间(秒):", round(r.elapsed.total_seconds(), 3))
    print("标题:", r.json()["title"][:40])


if __name__ == "__main__":
    demo_single_request()

    print("\n=== 2) 类 + 分页 + 容错 ===")
    api = PostsAPI("https://jsonplaceholder.typicode.com", timeout=10, retries=3)
    posts = api.get_all_posts(total=30, page_size=10)

    print("\n=== 3) 落盘 ===")
    save_json(posts, "demo/out/posts.json")

    print("\n=== 4) 读回来做校验（这就是数据驱动测试的雏形）===")
    with open("demo/out/posts.json", encoding="utf-8") as f:
        loaded = json.load(f)
    print("读回条数:", len(loaded))
    print("第一条 id:", loaded[0]["id"], "| 最后一条 id:", loaded[-1]["id"])
    assert len(loaded) == 30, "条数不对"
    assert all("title" in p for p in loaded), "字段缺失"
    print("校验通过")
