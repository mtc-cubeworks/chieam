---
description: setup Nuxt UI AI tooling in Windsurf (MCP + LLMs.txt + Skills)
---

# Nuxt UI Tools Setup (Windsurf)

Use this workflow to accelerate frontend delivery with Nuxt UI-aware AI context.

## 1) Add Nuxt UI MCP server in Windsurf

1. Open **Settings** -> **Windsurf Settings** -> **Cascade**.
2. Click **Manage MCPs** -> **View raw config**.
3. Add this MCP server entry:

```json
{
  "mcpServers": {
    "nuxt-ui": {
      "type": "http",
      "url": "https://ui.nuxt.com/mcp"
    }
  }
}
```

4. Save and restart Cascade session.

## 2) Validate MCP in agent prompts

Use prompts like:

- "Use Nuxt UI MCP tools to inspect `UButton` and apply best-practice props."
- "List Nuxt UI components for table filtering UX and suggest the cleanest option."

If MCP is active, the agent can call Nuxt UI tools (components, docs, examples, templates).

## 3) Add Nuxt UI docs context via LLMs.txt

When prompting Cascade, include one of these references:

- Quick context: `https://ui.nuxt.com/llms.txt`
- Full context: `https://ui.nuxt.com/llms-full.txt`

Use Windsurf `@docs` directly in prompts for targeted retrieval:

```text
@docs https://ui.nuxt.com/llms.txt
```

```text
@docs https://ui.nuxt.com/llms-full.txt
```

Recommended usage in Windsurf prompt:

- "Follow Nuxt UI guidance from https://ui.nuxt.com/llms.txt for this task."
- Use `llms-full` only for deep theming/migration/component edge cases.

## 3.1) Create persistent workspace rules (Windsurf)

1. Open your workspace rules (Windsurf project rules / instructions).
2. Add a persistent rule block like this:

```text
Frontend Nuxt UI Rule:
- Use Nuxt UI MCP tools for component/API/examples before implementation.
- Use @docs https://ui.nuxt.com/llms.txt by default.
- Escalate to @docs https://ui.nuxt.com/llms-full.txt only for complex theming/migration edge cases.
- Prefer semantic tokens and existing app patterns over ad-hoc utility styling.
```

3. Save the rule so all future frontend prompts inherit it.

## 4) Install Nuxt UI Skills (optional but recommended)

Run in terminal:

```bash
npx skills add nuxt/ui
```

If your skills tooling supports agent targeting, use:

```bash
npx skills add nuxt/ui --agent windsurf
```

## 5) Team prompt convention

For frontend tasks, prepend this line:

```text
Use Nuxt UI MCP + https://ui.nuxt.com/llms.txt + Nuxt UI skills conventions.
```

Optional strict variant:

```text
Use @docs https://ui.nuxt.com/llms.txt and Nuxt UI MCP tools first; only use llms-full when needed.
```

## 6) Fast-track pattern for this repo

For each frontend task:

1. Ask agent to fetch component metadata/examples first.
2. Implement with existing project patterns in `frontend/app`.
3. Keep semantic tokens and current design system classes.
4. Validate in both list/detail pages before finalizing.
