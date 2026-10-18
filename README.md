<p align="center"><img src="mascot.png" width="140"></p>

# ccsearch

"그거 클로드랑 언제 얘기했더라…" 할 때 쓰는 거.

클로드 코드 **지난 대화 전체**에서 검색어가 나온 곳을 찾아주고, 그 채팅으로 바로 돌아가는 방법까지 알려줌.

```
$ ccsearch 초견 노래
4개 찾음 (최신순 4개)

 1. 2026-10-15 17:39  클로드  x-growth  X에 개발기 올리기
    **초견 노래방**을 만들어 웹에 배포했고, X·스레드에 올린 뒤…
    → claude://claude.ai/epitaxy/local_3aea9d2f-…   ← 누르면 클로드 앱에서 그 채팅 열림
```

- 검색어 여러 개 → 다 들어간 것만
- `--me` → 내가 보낸 메시지만
- `-n 30` → 30개까지
- 클로드 앱(데스크톱) 채팅이면 앱 링크, 터미널 채팅이면 `claude --resume` 명령을 보여줌
- 7GB 기록 전체를 5~8초에 훑음 (M4 맥북 에어 기준)

## 실행

[uv](https://docs.astral.sh/uv/) 있으면 설치 없이:

```bash
uvx --from git+https://github.com/hesong0222-dev/ccsearch ccsearch 검색어
```

계속 쓸 거면:

```bash
uv tool install git+https://github.com/hesong0222-dev/ccsearch
ccsearch 검색어
```

## 개인정보

`~/.claude/projects` 기록을 내 컴퓨터에서만 읽음. 어디로도 안 보냄. 의존성 없음 (파이썬 기본 라이브러리만).

---

MIT · 만든 사람 [개발새발자](https://x.com/ComAsNas) · 같이 보면 좋은 것: [클로드 생활기록부](https://github.com/hesong0222-dev/claude-saenggibu)
