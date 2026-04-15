# Claude Code Extensibility Guide

Claude Code harness를 개발하거나 배포할 때 필요한 모든 확장 메커니즘을 정리한 문서입니다.

---

## 목차

1. [전체 아키텍처](#1-전체-아키텍처)
2. [Skills (Slash Commands)](#2-skills-slash-commands)
3. [Subagents](#3-subagents)
4. [Hooks](#4-hooks)
5. [MCP Servers](#5-mcp-servers)
6. [CLAUDE.md (시스템 프롬프트)](#6-claudemd-시스템-프롬프트)
7. [Settings](#7-settings)
8. [Rules](#8-rules)
9. [Plugins (패키징 & 배포)](#9-plugins-패키징--배포)
10. [배포 체크리스트](#10-배포-체크리스트)

---

## 1. 전체 아키텍처

```
~/.claude/                          ← 사용자 전역 (모든 프로젝트)
├── CLAUDE.md
├── settings.json
├── rules/
├── skills/
├── agents/
└── plugins/

project-root/                       ← 프로젝트 스코프 (git committed)
├── CLAUDE.md                       ← 자동 로드
├── CLAUDE.local.md                 ← gitignored, 개인 오버라이드
├── .claude/
│   ├── settings.json               ← 프로젝트 설정
│   ├── settings.local.json         ← gitignored, 개인 설정
│   ├── .env                        ← 환경변수 (선택)
│   ├── commands/                   ← 레거시 slash commands
│   │   └── my-command.md
│   ├── skills/                     ← 신규 skill 포맷 (권장)
│   │   └── my-skill/
│   │       └── SKILL.md
│   ├── agents/                     ← 서브에이전트
│   │   └── my-agent.md
│   └── rules/                      ← 경로별 규칙
│       └── my-rule.md
└── .cursor/                        ← Cursor IDE 지원 (선택)
```

### 스코프 우선순위 (높은 순)

```
Managed Policy > Project (.claude/) > Local (.local) > User (~/.claude/)
```

- 배열: 병합 (중복 제거)
- 객체: 딥 병합
- 문자열: 덮어쓰기

---

## 2. Skills (Slash Commands)

사용자가 `/skill-name` 으로 호출하는 재사용 가능한 워크플로우입니다.

### 2.1 파일 위치

| 스코프 | 경로 | 로딩 |
|--------|------|------|
| 프로젝트 (레거시) | `.claude/commands/<name>.md` | 자동, `/name` 으로 호출 |
| 프로젝트 (신규) | `.claude/skills/<name>/SKILL.md` | 자동, `/name` 으로 호출 |
| 사용자 전역 | `~/.claude/skills/<name>/SKILL.md` | 모든 프로젝트에서 사용 |
| 플러그인 | `<plugin>/skills/<name>/SKILL.md` | `/plugin-name:skill-name` |

### 2.2 레거시 포맷 (.claude/commands/)

단일 `.md` 파일. 현재 이 repo에서 사용 중인 포맷입니다.

```markdown
이 skill의 한 줄 설명.

User input: $ARGUMENTS

## Instructions

### 1. 첫 번째 단계
- 상세 설명

### 2. 두 번째 단계
- 상세 설명

## Output
- 출력 사양
```

**파일명이 곧 커맨드명**: `stat-rct.md` → `/stat-rct`

### 2.3 신규 SKILL.md 포맷

디렉토리 기반. 보조 파일 포함 가능.

```
.claude/skills/stat-rct/
├── SKILL.md              # 메인 (frontmatter + 본문)
├── formulas.md           # 보조 참조 파일
└── templates/
    └── sap-template.py   # Python 템플릿
```

**SKILL.md 구조**:

```yaml
---
name: stat-rct
description: "RCT 통계분석: ITT, ANCOVA, MMRM, multiplicity"
argument-hint: "[endpoint-type] [design-details]"
allowed-tools: "Bash(python *) Read Write Edit"
model: opus
---

# RCT Statistical Analysis

User input: $ARGUMENTS

## Instructions
...

보조 파일 참조: @./formulas.md
```

### 2.4 Frontmatter 옵션 (SKILL.md 전용)

| 필드 | 타입 | 설명 |
|------|------|------|
| `name` | string | 표시 이름 (kebab-case, 최대 64자) |
| `description` | string | 자동 호출 매칭에 사용 (250자 이내 권장) |
| `argument-hint` | string | 자동완성 힌트 |
| `disable-model-invocation` | bool | `true`: 사용자만 호출 가능 (Claude 자동호출 불가) |
| `user-invocable` | bool | `false`: Claude만 호출 가능 (사용자에게 안 보임) |
| `allowed-tools` | string | 사전 승인 도구 (승인 팝업 없이 실행) |
| `model` | string | 모델 오버라이드 (`opus`, `sonnet`, `haiku`) |
| `effort` | string | 추론 노력 (`low`, `medium`, `high`, `max`) |
| `context` | string | `fork`: 별도 서브에이전트에서 실행 |
| `agent` | string | 서브에이전트 타입 지정 |
| `paths` | string | glob 패턴 — 매칭 파일 작업 시에만 자동 트리거 |
| `hooks` | object | Skill 전용 hook 정의 |

### 2.5 변수 치환

| 변수 | 용도 |
|------|------|
| `$ARGUMENTS` | 사용자 입력 전체 |
| `$0`, `$1`, `$N` | N번째 인자 (0-indexed) |
| `${CLAUDE_SESSION_ID}` | 현재 세션 ID |
| `${CLAUDE_SKILL_DIR}` | SKILL.md가 있는 디렉토리 경로 |

**동적 컨텍스트 주입** (Shell 전처리):

```markdown
현재 브랜치: !`git branch --show-current`

최근 커밋:
```!
git log --oneline -5
```  ← 실행 결과가 Claude 입력에 주입됨
```

### 2.6 주의사항

- description은 250자 이내로. 스킬 리스팅에서 잘릴 수 있음
- 전체 스킬 description 합계는 컨텍스트의 1% (약 8,000자). `SLASH_COMMAND_TOOL_CHAR_BUDGET` 환경변수로 조정 가능
- 스킬 본문은 **호출 시에만** 로드됨 (description만 항상 컨텍스트에)
- Compaction 후 최대 25,000 토큰까지 유지 (최초 5,000 토큰/스킬)

---

## 3. Subagents

독립 컨텍스트 윈도우에서 실행되는 전문 에이전트입니다.

### 3.1 파일 위치

| 스코프 | 경로 |
|--------|------|
| 프로젝트 | `.claude/agents/<name>.md` |
| 사용자 전역 | `~/.claude/agents/<name>.md` |
| 플러그인 | `<plugin>/agents/<name>.md` |

### 3.2 파일 포맷

```yaml
---
name: statistician
description: "임상 생물통계학자. SAP 작성, 분석 코드 생성, 결과 해석"
model: opus
effort: high
maxTurns: 20
tools: "Bash Read Grep Write Edit"
disallowedTools: ""
skills: "stat-rct stat-survival"
memory: true
---

# Statistician Agent

당신은 임상 생물통계학자입니다.

## 역할
- 통계 분석 계획(SAP) 작성
- R/Python 분석 코드 생성
- 결과의 임상적 해석

## 원칙
- 항상 가정 검증 후 검정 적용
- p-value뿐 아니라 효과 크기 + 95% CI 보고
- LOCF 사용 금지, MMRM 또는 MI 사용
```

### 3.3 Frontmatter 옵션

| 필드 | 타입 | 설명 |
|------|------|------|
| `name` | string | 에이전트 이름 |
| `description` | string | Claude가 위임 결정에 사용 |
| `model` | string | `opus`, `sonnet`, `haiku` |
| `effort` | string | `low`, `medium`, `high`, `max` |
| `maxTurns` | int | 최대 대화 턴 수 |
| `tools` | string | 허용 도구 화이트리스트 |
| `disallowedTools` | string | 금지 도구 |
| `skills` | string | 시작 시 전체 내용 주입할 스킬 |
| `memory` | bool | 자동 메모리 활성화 |
| `isolation` | string | `worktree`: 별도 git worktree에서 실행 |

### 3.4 동작 방식

1. Claude가 task를 description과 매칭하여 자동 위임 (또는 수동 `/agents`)
2. 별도 컨텍스트 윈도우에서 실행 — 메인 대화 오염 방지
3. 완료 후 요약 결과만 메인 대화에 반환
4. 여러 서브에이전트 **병렬 실행** 가능

### 3.5 플러그인 에이전트 제한

플러그인에서 제공하는 에이전트는 다음 필드 사용 불가:
- `hooks`
- `mcpServers`
- `permissionMode`
- `isolation`은 `worktree`만 허용

---

## 4. Hooks

도구 호출 전후, 세션 시작/종료 등 이벤트에 자동 실행되는 자동화입니다.

### 4.1 설정 위치

| 위치 | 스코프 | 공유 가능 |
|------|--------|----------|
| `.claude/settings.json` | 프로젝트 | O (git commit) |
| `.claude/settings.local.json` | 프로젝트-개인 | X (gitignored) |
| `~/.claude/settings.json` | 사용자 전역 | X |
| `<plugin>/hooks/hooks.json` | 플러그인 | O |
| Skill/Agent frontmatter `hooks` | 해당 컴포넌트 활성 시 | O |

### 4.2 Hook 이벤트 목록

**세션**:
- `SessionStart` — 시작, 재개, 초기화, compaction
- `SessionEnd` — 종료

**턴 단위**:
- `UserPromptSubmit` — Claude 처리 전 (입력 변형 가능)
- `Stop` — Claude 응답 완료
- `StopFailure` — API 오류로 턴 종료

**도구 호출**:
- `PreToolUse` — 실행 전 (**차단 가능**)
- `PostToolUse` — 성공 후
- `PostToolUseFailure` — 실패 후
- `PermissionRequest` — 권한 대화상자 표시
- `PermissionDenied` — 도구 거부됨

**파일/환경**:
- `FileChanged` — 감시 파일 변경
- `CwdChanged` — 작업 디렉토리 변경
- `ConfigChange` — 설정/스킬 파일 변경
- `InstructionsLoaded` — CLAUDE.md 로드됨

**서브에이전트/태스크**:
- `SubagentStart`, `SubagentStop`
- `TaskCreated`, `TaskCompleted`

**기타**:
- `Notification`, `TeammateIdle`
- `PreCompact`, `PostCompact`
- `WorktreeCreate`, `WorktreeRemove`
- `Elicitation`, `ElicitationResult`

### 4.3 Hook 설정 스키마

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "if": "Bash(git *)",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/script.sh",
            "timeout": 600,
            "statusMessage": "검증 중...",
            "once": false
          }
        ]
      }
    ]
  }
}
```

### 4.4 Hook 타입

| 타입 | 용도 | 입출력 |
|------|------|--------|
| `command` | Shell 스크립트 실행 | stdin=JSON, stdout/exit code |
| `http` | HTTP POST 엔드포인트 | Request body=JSON, Response body=JSON |
| `prompt` | 단일턴 LLM 판단 | `{"ok": true/false, "reason": "..."}` |
| `agent` | 다턴 검증 에이전트 | 서브에이전트 생성, `{"ok": true/false}` |

### 4.5 Matcher 패턴

```json
{"matcher": ""}                     // 빈 문자열 = 모든 도구
{"matcher": "Bash"}                 // 정확히 "Bash"
{"matcher": "Edit|Write"}           // OR (파이프)
{"matcher": "^Notebook"}            // 정규식
{"matcher": "mcp__pubmed__.*"}      // MCP 도구 패턴
{"if": "Bash(git *)"}              // 도구(인자) 패턴
{"if": "Edit(*.ts)"}               // 특정 파일 패턴
```

### 4.6 Exit Code 규칙 (command 타입)

| Exit Code | 의미 | 동작 |
|-----------|------|------|
| **0** | 성공 | stdout가 Claude 컨텍스트에 추가됨 |
| **2** | 차단 | stderr가 Claude에 피드백됨, 도구 실행 중단 |
| **기타** | 비차단 오류 | 실행 계속, stderr는 디버그 로그로 |

### 4.7 JSON 출력 (Exit 0 + 유효 JSON)

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask|defer",
    "permissionDecisionReason": "설명"
  }
}
```

### 4.8 환경변수

```bash
$CLAUDE_PROJECT_DIR          # 프로젝트 루트
$CLAUDE_ENV_FILE             # SessionStart: export 문 작성할 파일
$CLAUDE_PLUGIN_ROOT          # 플러그인 설치 디렉토리
$CLAUDE_PLUGIN_DATA          # 플러그인 영구 데이터 디렉토리
```

### 4.9 예시: 통계 코드 작성 시 가정 검증 알림

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "if": "Write(*.py)",
        "hooks": [
          {
            "type": "command",
            "command": "echo '[Reminder] 통계 코드에 가정 검증(normality, PH assumption 등)을 포함하세요.'"
          }
        ]
      }
    ]
  }
}
```

### 4.10 주의사항

- `PostToolUse`는 도구 실행 **이후**이므로 되돌릴 수 없음
- Shell 프로파일(~/.zshrc)의 무조건 echo가 JSON 파싱을 깨뜨릴 수 있음
- `deny` 권한 규칙은 hook의 `"allow"` 반환으로 우회 불가
- Hook timeout 기본값 10분, `timeout` 필드로 조정

---

## 5. MCP Servers

외부 도구/서비스를 Claude에 연결하는 Model Context Protocol 서버입니다.

### 5.1 설정 위치

| 위치 | 스코프 |
|------|--------|
| `.claude/settings.json` → `mcpServers` | 프로젝트 |
| `.claude/.mcp.json` | 프로젝트 (독립 파일) |
| `~/.claude/settings.json` → `mcpServers` | 사용자 전역 |
| `<plugin>/.mcp.json` 또는 `plugin.json` | 플러그인 |

### 5.2 설정 스키마

```json
{
  "mcpServers": {
    "pubmed": {
      "command": "npx",
      "args": ["-y", "pubmed-mcp-server"],
      "env": {
        "NCBI_API_KEY": "${NCBI_API_KEY}"
      },
      "cwd": "/optional/working/dir",
      "disabled": false,
      "timeout": 30000,
      "transport": "stdio"
    }
  }
}
```

### 5.3 환경변수 해석

```json
{"env": {"API_KEY": "${MY_API_KEY}"}}
```

해석 순서:
1. 사용자 Shell 환경
2. `.claude/.env` 파일
3. 세션 환경

### 5.4 도구 호출 규칙

MCP 도구 이름 포맷: `mcp__<서버명>__<도구명>`

예: `mcp__pubmed__search_articles`

permissions에서 패턴 매칭 가능:
```json
{"allow": ["mcp__pubmed__*"]}
```

### 5.5 팀 공유

- `.claude/settings.json`에 서버 설정을 커밋
- API 키는 `${ENV_VAR}` 형태로 — 각 사용자가 로컬에서 설정
- `.claude/.env` 파일에 비밀이 아닌 환경변수 저장 가능

---

## 6. CLAUDE.md (시스템 프롬프트)

프로젝트의 "성격"을 정의하는 핵심 파일입니다. Claude Code 세션 시작 시 자동으로 로드됩니다.

### 6.1 파일 위치 & 로딩 순서

| 위치 | 스코프 | 로딩 |
|------|--------|------|
| `./CLAUDE.md` 또는 `.claude/CLAUDE.md` | 프로젝트 | cwd부터 상위로 탐색 |
| `./CLAUDE.local.md` | 프로젝트-개인 | gitignored |
| `~/.claude/CLAUDE.md` | 사용자 전역 | 모든 프로젝트 |
| 하위 디렉토리 `CLAUDE.md` | 경로 종속 | 해당 파일 읽을 때 on-demand |
| Managed policy | 조직 전체 | 제외 불가 |

### 6.2 @import 문법

```markdown
# 프로젝트 지침

@./README.md
@package.json
@~/.claude/shared-conventions.md
```

- 상대 경로: import하는 파일 기준으로 해석
- 최대 5단계 재귀
- 순환 참조 감지됨

### 6.3 작성 지침

- **200줄 이내** 권장 (compaction 후 재주입됨)
- 구체적이고 간결하게 — 길수록 준수율 저하
- HTML 주석 (`<!-- ... -->`)은 컨텍스트에서 제거됨
- 코드 블록 내 HTML 주석은 유지됨

### 6.4 CLAUDE.md vs 자동 메모리

| | CLAUDE.md | Auto Memory |
|---|-----------|-------------|
| 작성자 | 사람 | Claude |
| 내용 | 프로젝트 지침/규칙 | 학습한 내용 |
| 범위 | 모든 세션 | 해당 머신 로컬 |
| 공유 | git committed | 불가 |
| 용도 | 빌드 명령, 코딩 규칙, 아키텍처 | 패턴 발견, 디버깅 인사이트 |

### 6.5 제외 설정

```json
// .claude/settings.local.json
{
  "claudeMdExcludes": [
    "**/monorepo/CLAUDE.md",
    "/absolute/path/.claude/rules/**"
  ]
}
```

Managed policy CLAUDE.md는 제외 불가.

---

## 7. Settings

### 7.1 파일 위치

| 파일 | 스코프 | 공유 |
|------|--------|------|
| `.claude/settings.json` | 프로젝트 | O (committed) |
| `.claude/settings.local.json` | 프로젝트-개인 | X (gitignored) |
| `~/.claude/settings.json` | 사용자 전역 | X |

### 7.2 전체 스키마

```json
{
  "model": "claude-opus-4-6",
  "effort": "high",

  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(python *)",
      "Read",
      "mcp__pubmed__*"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Write(/sensitive/*)"
    ]
  },

  "hooks": {
    "PreToolUse": [],
    "PostToolUse": [],
    "SessionStart": []
  },

  "mcpServers": {
    "server-name": {}
  },

  "autoMemoryEnabled": true,
  "claudeMdExcludes": [],
  "disableAllHooks": false,

  "env": {
    "NODE_ENV": "development"
  }
}
```

### 7.3 권한 모델

```json
{
  "permissions": {
    "allow": ["Bash(git *)", "Read", "Grep", "Glob"],
    "deny": ["Bash(rm *)"]
  }
}
```

- 순서대로 평가, 첫 매치가 적용
- `deny`는 항상 hook의 `allow` 반환보다 우선
- 대소문자 구분: `Bash` ≠ `bash`

---

## 8. Rules

경로별 규칙 파일. 특정 파일 작업 시에만 활성화됩니다.

### 8.1 파일 위치

```
.claude/rules/
├── code-style.md           # paths 없음 → 항상 로드
├── testing.md
└── backend/
    └── api-design.md       # 재귀 탐색됨
```

사용자 전역: `~/.claude/rules/`

### 8.2 Frontmatter (선택)

```yaml
---
paths:
  - "src/**/*.ts"
  - "*.config.js"
---

# TypeScript 코딩 규칙

이 규칙은 매칭 파일 작업 시에만 로드됩니다.
```

- `paths` 없으면: 세션 시작 시 무조건 로드 (CLAUDE.md처럼)
- `paths` 있으면: 매칭 파일 읽을 때 on-demand 로드
- Glob 패턴 사용 (`**/*.ts`, `src/**`, `*.{ts,tsx}`)

### 8.3 Symlink 지원

```bash
ln -s ~/shared-rules .claude/rules/shared
```

심볼릭 링크가 런타임에 해석됨. 순환 링크 감지됨.

---

## 9. Plugins (패키징 & 배포)

여러 skill + agent + hook + MCP를 하나의 패키지로 묶어 배포합니다.

### 9.1 디렉토리 구조

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json             # 매니페스트 (선택 — 없으면 자동 탐색)
├── skills/                     # 스킬 디렉토리 (루트에 위치!)
│   └── stat-rct/
│       └── SKILL.md
├── agents/                     # 에이전트 디렉토리
│   └── statistician.md
├── hooks/
│   └── hooks.json
├── .mcp.json                   # MCP 서버 설정
├── bin/                        # PATH에 추가될 실행 파일
│   └── my-tool
├── settings.json               # 기본 설정
└── LICENSE
```

**중요**: `skills/`, `agents/`, `hooks/`는 반드시 **플러그인 루트**에 위치. `.claude-plugin/` 안에 넣으면 안 됩니다.

### 9.2 plugin.json 매니페스트

```json
{
  "name": "clinical-research-harness",
  "version": "1.0.0",
  "description": "20 slash commands for clinical research: study design to manuscript",
  "author": {
    "name": "VUNO RnD",
    "url": "https://github.com/vuno-rnd"
  },
  "repository": "https://github.com/vuno-rnd/clinical-research-harness",
  "license": "Apache-2.0",
  "keywords": ["clinical-research", "biostatistics", "study-design"],

  "skills": "./skills/",
  "agents": "./agents/",
  "hooks": "./hooks/hooks.json",

  "mcpServers": {
    "pubmed": {
      "command": "npx",
      "args": ["-y", "pubmed-mcp-server"],
      "env": {"NCBI_API_KEY": "${NCBI_API_KEY}"}
    }
  },

  "userConfig": {
    "ncbi_api_key": {
      "description": "NCBI API Key for PubMed access (free at ncbi.nlm.nih.gov)",
      "sensitive": true
    }
  }
}
```

### 9.3 userConfig (사용자 설정값)

```json
{
  "userConfig": {
    "api_endpoint": {
      "description": "API 엔드포인트",
      "sensitive": false
    },
    "api_token": {
      "description": "인증 토큰",
      "sensitive": true
    }
  }
}
```

- `sensitive: false` → `settings.json`의 `pluginConfigs`에 저장
- `sensitive: true` → 시스템 키체인에 저장
- 환경변수로 노출: `CLAUDE_PLUGIN_OPTION_<KEY>`
- 스킬/에이전트에서: `${user_config.KEY}`

### 9.4 설치 & 관리

```bash
# 로컬 개발
claude --plugin-dir ./my-plugin

# 설치 (마켓플레이스에서)
claude plugin install clinical-research-harness --scope project

# 관리
claude plugin enable <name>
claude plugin disable <name>
claude plugin update <name>
claude plugin uninstall <name> [--keep-data]
```

### 9.5 스킬 네임스페이싱

플러그인 스킬은 네임스페이스됨:
```
/clinical-research-harness:stat-rct
/clinical-research-harness:sample-size
```

### 9.6 영구 데이터 디렉토리

```
~/.claude/plugins/data/{sanitized-id}/
```

- 플러그인 업데이트 후에도 유지
- `${CLAUDE_PLUGIN_DATA}` 환경변수로 접근
- `--keep-data` 없이 삭제하면 데이터도 삭제

### 9.7 주의사항

- 매니페스트가 없으면 기본 위치에서 자동 탐색
- 플러그인 외부 경로 참조 불가 (`../` 차단)
- **버전 범프 필수** — 캐싱으로 인해 버전 안 올리면 변경 반영 안 됨
- 플러그인 에이전트는 `hooks`, `mcpServers`, `permissionMode` 필드 사용 불가

---

## 10. 배포 체크리스트

### Git Repo로 배포 (현재 방식)

사용자가 `git clone` 후 `claude` 실행하면 바로 동작.

- [x] `CLAUDE.md` — 시스템 프롬프트
- [x] `.claude/commands/*.md` — 20개 스킬
- [x] `.claude/settings.json` — MCP + hooks (API 키는 `${ENV_VAR}`)
- [x] `AGENTS.md` — 상세 방법론 레퍼런스
- [x] `subagents/*.md` — 전문 에이전트
- [x] `.gitignore` — `.local` 파일 제외
- [x] `README.md` — 설치/사용법
- [x] `LICENSE`

### Plugin으로 전환 시 추가 작업

현재 repo를 플러그인으로 전환하려면:

1. `.claude/commands/*.md` → `skills/<name>/SKILL.md` 로 마이그레이션
2. `subagents/*.md` → `agents/*.md` 로 이동
3. `.claude-plugin/plugin.json` 매니페스트 작성
4. `hooks/hooks.json` 으로 hook 설정 분리
5. `.mcp.json` 으로 MCP 설정 분리
6. `userConfig`에 `ncbi_api_key` 추가
7. 버전 번호 부여 (semver)
8. 마켓플레이스 제출 또는 npm/GitHub 패키지로 배포

### 마이그레이션 예시

**Before** (레거시 command):
```
.claude/commands/stat-rct.md
```

**After** (plugin skill):
```
skills/stat-rct/SKILL.md
skills/stat-rct/templates/sap_template.py
skills/stat-rct/reference/formulas.md
```

---

## 참고 자료

- [Claude Code 공식 문서](https://docs.anthropic.com/en/docs/claude-code)
- [Skills 가이드](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Hooks 레퍼런스](https://docs.anthropic.com/en/docs/claude-code/hooks)
- [MCP 설정](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Plugins 레퍼런스](https://docs.anthropic.com/en/docs/claude-code/plugins)
- [Settings 가이드](https://docs.anthropic.com/en/docs/claude-code/settings)
