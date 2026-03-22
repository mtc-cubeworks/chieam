# Nuxt UI Tools (Windsurf)

## Default rule for frontend work

- Use Nuxt UI MCP server (`nuxt-ui`) to inspect components, props, slots, examples, and theming before implementing UI changes.
- Use `@docs https://ui.nuxt.com/llms.txt` by default for Nuxt UI best practices.
- Escalate to `@docs https://ui.nuxt.com/llms-full.txt` only for complex theming/migration edge cases.

## Prompt prefix

Use this prefix for UI tasks:

```text
Use Nuxt UI MCP + @docs https://ui.nuxt.com/llms.txt + Nuxt UI skill conventions.
```

## Notes

- Nuxt UI skills are installed in the project (see `frontend/skills-lock.json`).
- MCP server config is stored in Windsurf settings (not committed to repo). See `.windsurf/workflows/nuxt-ui-tools.md`.
