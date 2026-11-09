"""day_01 练习：把「脚本」改造成「测试」（GitHub Issues 版）。"""
import requests

BASE_URL = "https://api.github.com/repos/psf/requests/issues"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "pytest-practice",
}


def get_issues(**params):
    """统一入口，避免每个测试重复写参数。"""
    p = {"per_page": 10, "state": "all", **params}
    return requests.get(BASE_URL, params=p, headers=HEADERS, timeout=15)


def test_single_issue():
    """单条查询：用 per_page=1 拿 1 条，验证状态码和字段结构。"""
    r = get_issues(per_page=1)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list), "GitHub issues 接口返回的是列表"
    assert len(data) == 1

    issue = data[0]
    assert isinstance(issue["number"], int)
    assert issue["number"] > 0
    assert isinstance(issue["title"], str)
    assert issue["title"], "title 不能为空"
    assert issue["state"] in {"open", "closed"}


def test_per_page_limit():
    """参数生效：per_page=10 必须返回 10 条。"""
    r = get_issues(per_page=10)
    assert r.status_code == 200
    assert len(r.json()) == 10


def test_pagination_no_duplicate():
    """分页拉全：3 页 x 10 条 = 30 条，且编号不重复。"""
    all_issues = []
    for page in (1, 2, 3):
        r = get_issues(per_page=10, page=page)
        assert r.status_code == 200
        all_issues.extend(r.json())

    assert len(all_issues) == 30
    numbers = [i["number"] for i in all_issues]
    assert len(set(numbers)) == 30, "分页出现了重复数据"


def test_response_time():
    """响应时间：接口测试里最轻量的一层性能断言。"""
    r = get_issues(per_page=1)
    assert r.status_code == 200
    assert r.elapsed.total_seconds() < 5