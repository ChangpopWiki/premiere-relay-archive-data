import urllib.request
import json
import os
from datetime import datetime, timezone

BASE_URL = 'https://changpop.wiki/premiere-relay-archive'
SECRET_KEY = os.environ['SECRET_KEY']

def fetch_server_mtimes() -> dict:
    url = f"{BASE_URL}/api.php?files_last_modified"
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {SECRET_KEY}'})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode('utf-8'))

def get_local_mtime(path: str) -> datetime | None:
    if not os.path.exists(path):
        return None
    return datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)

def parse_dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace('Z', '+00:00'))

def sync_file(repo_path: str):
    url = f"{BASE_URL}/data/{repo_path}"
    with urllib.request.urlopen(url) as r:
        content = r.read()
    os.makedirs(os.path.dirname(repo_path), exist_ok=True)
    with open(repo_path, 'wb') as f:
        f.write(content)
    print(f"Updated: {repo_path}")

server_mtimes = fetch_server_mtimes()

if not server_mtimes:
    print("서버에 파일 없음")
    exit(0)

for repo_path, server_mtime_str in server_mtimes.items():
    if parse_dt(server_mtime_str) > (get_local_mtime(repo_path) or datetime.min.replace(tzinfo=timezone.utc)):
        sync_file(repo_path)

print("동기화 완료")