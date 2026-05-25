# How to Set Up Specialized Agents in DeerFlow

DeerFlow has **two distinct agent concepts** for specialization:

---

## 1. Custom Agents (Lead Agent Personalities)

A custom agent **replaces the lead agent itself** — giving it a different model, tool set, skills, and personality. Think of it as a "role" the main agent inhabits.

### Create one on disk

Each custom agent lives in `backend/.deer-flow/agents/<name>/` with two files:

**`config.yaml`** — declares the model, tool groups, and skill whitelist:

```yaml
name: data-scientist
description: Expert data analysis assistant with Python and SQL tools
model: claude-sonnet-4-6          # specific model from config.yaml models[]
tool_groups:                       # whitelist tool groups (null = all tools)
  - bash
  - file:read
  - file:write
skills:                            # whitelist skills (null = all enabled)
  - data-analysis
  - deep-research
```

**`SOUL.md`** — personality/behavior instructions injected into the system prompt:

```markdown
## Identity
You are DataScientist, a specialist in statistical analysis and data visualization.
Always prefer Pandas over raw Python. Explain your methodology before writing code.
```

### How it gets wired up

At runtime, when the frontend selects this agent:
1. `load_agent_config(name)` reads the `config.yaml`
2. `agent_config.model` overrides the default model via `_resolve_model_name()`
3. `agent_config.tool_groups` filters which tool groups from `config.yaml` are loaded — only tools matching those groups are included
4. `agent_config.skills` filters which skills appear in the system prompt
5. `load_agent_soul(name)` reads `SOUL.md` and injects it into the prompt

The entry point is `make_lead_agent()` in `backend/packages/harness/deerflow/agents/lead_agent/agent.py:339`.

### Manage via API

```
GET    /api/agents              # list all custom agents
POST   /api/agents              # create a new agent
PUT    /api/agents/{name}       # update config + SOUL.md
DELETE /api/agents/{name}       # delete an agent
```

---

## 2. Custom Subagents (Delegated Background Workers)

Subagents are **spawned by the lead agent at runtime** via the `task` tool. They run isolated, limited-turn sub-conversations and return a result.

### Define in `config.yaml`

Custom subagents go under `subagents.custom_agents`:

```yaml
subagents:
  timeout_seconds: 900          # global default
  max_turns: 120

  custom_agents:
    code-reviewer:
      description: "Reviews code for bugs, security issues, and style violations"
      system_prompt: |
        You are a senior code reviewer. For every file you read:
        1. Identify logic bugs and edge cases
        2. Flag security concerns (OWASP Top 10)
        3. Note style/consistency issues
        Output a structured review with severity levels.
      tools:                    # explicit whitelist — only these tools are available
        - read_file
        - ls
        - grep
      disallowed_tools:         # explicitly denied (task is denied by default)
        - bash
      skills:                   # skill whitelist
        - code-review
      model: claude-opus-4-7    # specific model, or "inherit" for parent's model
      max_turns: 80
      timeout_seconds: 600
```

### Override built-in subagents per-agent

You can also override built-in subagents (`general-purpose`, `bash`) with specific models/skills:

```yaml
subagents:
  agents:
    general-purpose:
      timeout_seconds: 1800
      model: gpt-4              # force GPT-4 for general-purpose subagents
      skills:
        - web-search
        - data-analysis
    bash:
      timeout_seconds: 300
      skills: []                # no skills at all for bash subagent
```

### The `SubagentConfig` dataclass

Each subagent is described by these fields (`backend/packages/harness/deerflow/subagents/config.py`):

| Field | Default | Purpose |
|-------|---------|---------|
| `name` | required | Unique identifier |
| `description` | required | When the lead agent should delegate to this |
| `system_prompt` | required | Behavior instructions |
| `tools` | `None` | Tool name whitelist (`None` = inherit all parent tools) |
| `disallowed_tools` | `["task"]` | Tool name denylist |
| `skills` | `None` | Skill whitelist (`None` = inherit all, `[]` = none) |
| `model` | `"inherit"` | Model name or `"inherit"` for parent's model |
| `max_turns` | `50` | Max conversation turns before force-stop |
| `timeout_seconds` | `900` | Max wall-clock time |

---

## 3. Config Resolution Order

### Models — which model an agent gets

```
Runtime request (frontend selection)
  → Custom agent config.yaml `model` field
    → First model in config.yaml `models[]` list
```

### Tools — which tools an agent gets

1. **Config tools** from `config.yaml` `tools[]` — filtered by `tool_groups` if set
2. **Built-in tools** — `present_file`, `ask_clarification`, plus conditionally `view_image`, `skill_manage`, `task`
3. **MCP tools** — from enabled servers in `extensions_config.json`
4. **ACP agent tools** — if ACP agents configured

For subagents, an additional allowlist/denylist filter is applied on top.

### Skills — which skills appear in the prompt

Controlled by the `skills` field on the agent/subagent config. `None` = inherit all enabled skills. `[]` = no skills. `["name1", "name2"]` = only those.

---

## 4. Quick Start: Practical Example

To create a **code-reviewer** subagent with specific tools and a specific model:

**Step 1** — Add to `config.yaml`:

```yaml
subagents:
  custom_agents:
    code-reviewer:
      description: "Use when code needs review for bugs, security, or style"
      system_prompt: |
        You are a senior code reviewer. Review thoroughly and output:
        - Severity (critical/high/medium/low)
        - File and line reference
        - Explanation and fix suggestion
      tools:
        - read_file
        - ls
        - grep
      model: claude-sonnet-4-6   # must match a name in models[]
      max_turns: 60
```

**Step 2** — Ensure the model exists in `config.yaml` `models[]`:

```yaml
models:
  - name: claude-sonnet-4-6
    use: langchain_anthropic:ChatAnthropic
    model: claude-sonnet-4-6-20250514
    supports_thinking: true
```

**Step 3** — Ensure the tools are defined:

```yaml
tool_groups:
  - name: file:read

tools:
  - name: read_file
    group: file:read
    use: deerflow.sandbox.tools:read_file_tool
  - name: ls
    group: file:read
    use: deerflow.sandbox.tools:ls_tool
  - name: grep
    group: bash
    use: deerflow.sandbox.tools:grep_tool
```

**Step 4** — Restart the backend. The lead agent will now delegate to `code-reviewer` when appropriate.

---

## Key Files Reference

| What | Path |
|------|------|
| Custom agent config + SOUL.md | `backend/.deer-flow/agents/<name>/` |
| Lead agent factory | `backend/packages/harness/deerflow/agents/lead_agent/agent.py` |
| Subagent config dataclass | `backend/packages/harness/deerflow/subagents/config.py` |
| Subagent registry | `backend/packages/harness/deerflow/subagents/registry.py` |
| Subagent executor | `backend/packages/harness/deerflow/subagents/executor.py` |
| Tool assembly | `backend/packages/harness/deerflow/tools/tools.py` |
| Model factory | `backend/packages/harness/deerflow/models/factory.py` |
| Main config | `config.yaml` (template: `config.example.yaml`) |
| Extensions (MCP + skills state) | `extensions_config.json` |
