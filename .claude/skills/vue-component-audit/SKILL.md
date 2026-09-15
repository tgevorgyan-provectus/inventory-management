---
name: vue-component-audit
description: Analyze Vue 3 components for reactivity bugs, performance problems, missed reuse, and missing error/loading states, then apply the fixes. Use when asked to audit, analyze, optimize, or review a .vue file or the whole client.
---

# Vue Component Audit

Audit one or more `.vue` files against the four categories below, then **apply
the fixes** and report what changed.

## Scope

Default target is `client/src/views/*.vue` and `client/src/components/*.vue`.
If the user names a file, audit only that file.

## Procedure

1. **Read before judging.** Read each target file in full. Never report a
   finding you have not seen in the source — a grep hit is a candidate, not a
   finding.
2. **Check the four categories** (below).
3. **Apply fixes**, surgically: touch only the lines the finding requires.
   Match surrounding style. Do not refactor adjacent code, do not reformat, do
   not "improve" things that are not broken.
4. **Verify**: run `npx vite build` in `client/`. It must succeed. If a fix
   breaks the build, revert that fix and report it as unfixed.
5. **Report** as a table: file, line, category, what changed.

## Category 1 — Reactivity correctness

| Pattern | Fix |
|---|---|
| `v-for` with `:key="index"` | Use a stable unique field (`sku`, `id`, `month`) |
| Direct prop mutation (`props.x.y = …`) | Emit an event to the parent instead |
| `new Date(x).getMonth()` with no guard | Validate with `!isNaN(date.getTime())` first |
| Destructured props in `setup()` | Keep `props.x` access so reactivity survives |

## Category 2 — Performance

| Pattern | Fix |
|---|---|
| Filter/sort/reduce in a method called from the template | Move to `computed` (cached until deps change) |
| `v-if` on a frequently toggled block | `v-show` (toggles CSS, no DOM churn) |
| Watcher firing an API call per keystroke | Debounce it |

Do **not** flag a method that performs an action (a click handler, a fetch).
Only flag derived *data* computed on every render.

## Category 3 — Code reuse

Report, and fix only when the fix is contained:

- The same logic in 2+ views → extract to `client/src/composables/`.
- Repeated markup blocks → suggest a component.
- Hardcoded UI strings where an i18n key already exists in
  `client/src/locales/en.js` → swap in `t('...')`.

Extracting a composable touches multiple files. If the extraction would exceed
a surgical diff, **report it instead of doing it**, and say why.

## Category 4 — Error and loading states

| Pattern | Fix |
|---|---|
| `await` with no `try/catch` | Wrap; set an error ref |
| No `loading` state during fetch | Add one, cleared in `finally` |
| **A secondary fetch writing to the page-level `error` ref** | Give it its own ref and render it inline |

That last one is the highest-value check in this skill. When `error` is
rendered with `v-else-if` at the page root, *any* writer to it blanks the
entire page. A secondary fetch failing must degrade to an inline banner, not
take down content that loaded fine. This exact bug shipped in `Orders.vue`:
a failed `/api/restock-orders` call hid all 250 orders and 4 stat cards.

## Reporting

```
client/src/views/Orders.vue
  L165  error-state   secondary fetch wrote page-level error ref  → FIXED
  L142  reactivity    v-for :key used index                       → FIXED
  L88   performance   filter in method                            → REPORTED (needs API change)

3 findings · 2 fixed · 1 reported · vite build: OK
```

State the build result every time. A fix you have not built is not verified.

## Rules

- This repo's `client/CLAUDE.md` is the source of truth for Vue conventions
  here; its "Common Pitfalls" list feeds categories 1 and 2. Follow it over
  generic Vue advice.
- Max 3 lines per code comment, and only to say *why*.
- Never add a dependency. Never add an icon library.
- If a file is clean, say so. Do not invent findings to look useful.
