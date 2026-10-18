"""ccsearch: 클로드 코드 지난 대화(~/.claude/projects)에서 검색어가 나온 곳을 찾아 보여주고,
그 대화로 돌아가는 방법(클로드 앱 링크 / claude --resume)을 알려준다. 기록은 내 컴퓨터에서만 읽는다."""
import argparse, json, re, sys
from datetime import datetime
from pathlib import Path

ROOT = Path.home() / ".claude" / "projects"
APP_SESSIONS = Path.home() / "Library" / "Application Support" / "Claude" / "claude-code-sessions"
TTY = sys.stdout.isatty()
c = lambda code, s: f"\033[{code}m{s}\033[0m" if TTY else s


def texts(d):
    """한 줄 기록에서 사람이 친 말 / 클로드가 한 말만 꺼낸다(도구 결과·자동 입력 제외)."""
    t = d.get("type")
    m = d.get("message") or {}
    content = m.get("content")
    if t == "user":
        if (d.get("origin") or {}).get("kind") not in ("human", None) or d.get("isMeta"):
            return None
        if isinstance(content, str) and not content.lstrip().startswith("<"):
            return "나", content
    elif t == "assistant" and isinstance(content, list):
        s = " ".join(x.get("text", "") for x in content if isinstance(x, dict) and x.get("type") == "text")
        if s.strip():
            return "클로드", s
    return None


def app_links():
    """클로드 앱 세션 파일에서 내부 세션 번호 → 앱 링크/제목을 만든다(앱을 안 쓰면 비어 있음)."""
    links = {}
    for f in APP_SESSIONS.glob("*/*/local_*.json"):
        try:
            j = json.loads(f.read_text())
            links[j["cliSessionId"]] = (f"claude://claude.ai/epitaxy/{j['sessionId']}", j.get("title") or "")
        except (OSError, ValueError, KeyError):
            pass
    return links


def matching_lines(term):
    """첫 검색어가 든 줄만 빠르게 꺼낸다: 파일을 바이트로 읽고 bytes.find 로 위치만 찾아 그 줄만 자른다.
    스크린샷·도구 결과가 든 거대한 줄과, 사람/클로드 대화가 아닌 줄은 해석 전에 버린다."""
    variants = {term} | ({term.lower(), term.upper(), term.capitalize()} if term.isascii() else set())
    needles = [v.encode() for v in variants]
    for f in ROOT.glob("*/*.jsonl"):
        try:
            data = f.read_bytes()
        except OSError:
            continue
        starts = set()
        for n in needles:
            i = data.find(n)
            while i != -1:
                start = data.rfind(b"\n", 0, i) + 1
                end = data.find(b"\n", i)
                end = len(data) if end == -1 else end
                starts.add((start, end))
                i = data.find(n, end)
        for start, end in starts:
            line = data[start:end]
            if end - start > 300_000 or (b'"type":"user"' not in line and b'"type":"assistant"' not in line):
                continue
            yield f, line.decode("utf-8", "ignore")


def snippet(text, terms, width=140):
    flat = re.sub(r"\s+", " ", text)
    i = min((flat.lower().find(t) for t in terms if flat.lower().find(t) >= 0), default=0)
    start = max(0, i - width // 3)
    s = ("…" if start else "") + flat[start:start + width] + ("…" if start + width < len(flat) else "")
    for t in terms:
        s = re.sub(re.escape(t), lambda m: c("1;33", m.group(0)), s, flags=re.I)
    return s


def main():
    ap = argparse.ArgumentParser(description="클로드 코드 지난 대화 검색")
    ap.add_argument("terms", nargs="+", help="검색어 (여러 개면 모두 들어간 것만)")
    ap.add_argument("--me", action="store_true", help="내가 보낸 메시지만")
    ap.add_argument("-n", type=int, default=15, help="보여줄 개수 (기본 15)")
    a = ap.parse_args()
    terms = [t.lower() for t in a.terms]

    hits = []
    for f, line in matching_lines(a.terms[0]):
        low = line.lower()
        if not all(t in low for t in terms):
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        got = texts(d)
        if not got or (a.me and got[0] != "나"):
            continue
        who, text = got
        if not all(t in text.lower() for t in terms):
            continue
        try:
            when = datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00")).astimezone()
        except (KeyError, ValueError):
            continue
        hits.append((when, who, text, d.get("sessionId") or f.stem, d.get("cwd") or ""))

    if not hits:
        print("못 찾았어요.")
        return
    hits.sort(key=lambda h: h[0], reverse=True)
    links = app_links()
    seen = 0
    print(c("2", f"{len(hits)}개 찾음 (최신순 {min(a.n, len(hits))}개)\n"))
    for when, who, text, sid, cwd in hits[: a.n]:
        seen += 1
        link, title = links.get(sid, (None, ""))
        head = f"{when:%Y-%m-%d %H:%M}  {c('36', who)}  {Path(cwd.split('/.claude/worktrees/')[0]).name}"
        print(f"{c('2', str(seen).rjust(2))}. {head}" + (f"  {c('35', title)}" if title else ""))
        print(f"    {snippet(text, terms)}")
        print(c("2", f"    → {link}" if link else f"    → cd {cwd} && claude --resume {sid}"))
        print()


if __name__ == "__main__":
    main()
