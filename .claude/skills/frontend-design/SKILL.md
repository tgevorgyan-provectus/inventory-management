---
name: frontend-design
description: Redesign a Vue 3 application's UI into a modern SaaS-style interface - vertical navigation sidebar on the left instead of a top nav bar, consistent spacing, polished card layouts. Use when asked to redesign the UI, modernize the frontend, apply a SaaS look, or move navigation to a sidebar.
---

# Frontend Design: SaaS-Style Vue 3 Redesign

Restructure a Vue 3 app's shell into a modern SaaS layout. This is a process,
not a theme: you derive the design from what the app already has rather than
importing an opinion.

## Core Rules

1. **Derive, never invent.** The palette, fonts, and radii come from the
   existing codebase. Read them out and promote them to CSS custom properties.
   Do not introduce a new color scheme unless the user asks for one.
2. **No new dependencies without asking.** No icon library, no CSS framework,
   no component kit. Inline SVG covers icons.
3. **Shell only by default.** You change the layout shell and global styles.
   Page/view internals and their scoped styles are out of scope unless the
   user explicitly asks. Say this boundary out loud when you propose the plan.
4. **Evidence before claims.** Every statement about the app rests on a file
   you read or a command you ran. Every success claim rests on output you saw.

## Step 1 — Inventory

Before designing anything, establish these facts and write them down:

- **The shell.** Which file renders `<router-view>`? That file owns the nav.
- **The routes.** Read the router config. List every route, its path, and its
  component. The sidebar must cover exactly these — no more, no fewer. Count
  them; do not assume the nav and the router agree.
- **Style ownership.** Which styles are global (unscoped) vs `<style scoped>`?
  Global rules like `.card` or `.stat-card` are your lever: restyling them
  restyles every view without touching a view file. Confirm which shared
  class names the views actually consume.
- **Label indirection.** Are nav labels literal strings or i18n keys
  (`t('nav.x')`)? Check the locale files for the keys that exist. A label with
  no key must stay literal — inventing one is a translation regression.
- **Selector blast radius.** Grep every selector you intend to delete or
  rename across the whole source tree. Deleting a rule another file depends on
  is the most common way this task breaks something.
- **Existing tests.** What suites exist, do any cover the frontend, and what
  is the pass count *before* you change anything? Without that number, a pass
  afterward proves nothing.

## Step 2 — Propose, then stop

Report the inventory and the plan: the exact files you will change, the files
you will *not* change and why, the risks you found, and how you will verify.
Get approval before editing. Do not present a plan and start in the same turn.

## Step 3 — Build the shell

- **Extract the sidebar into its own component.** Do not let the shell file
  grow a large nav template inline.
- **Layout:** the shell becomes a row — fixed-width sidebar beside a content
  column holding any sub-header and the router view. Give the content column
  `min-width: 0` so it shrinks instead of overflowing. A sidebar anchors the
  layout, so a centering `max-width` on the old top-nav container is usually
  now wrong; check each one rather than assuming.
- **Stale offsets:** anything positioned relative to the old top bar — a
  sticky sub-header with `top: <navheight>px`, a scroll-margin, a fixed
  overlay — is now measuring against something that no longer exists. Grep for
  the old nav's height as a number.
- **Icons:** one inline `<svg>` per nav item, uniform size, `aria-hidden="true"`
  since the adjacent text label is the accessible name.
- **Active state:** keep whatever route matching the app already used.
- **Tokens:** add a `:root` block of custom properties holding the colors and
  spacing you found in Step 1, then reference them. This is what makes the look
  consistent — not a bigger palette.

### Moving existing components into the rail

Components that lived in a horizontal top bar carry assumptions that a vertical
rail breaks. Before moving one, read its CSS and check:

- **Dropdown direction.** A menu styled `top: calc(100% + ...)` opens downward.
  Near the bottom of a full-height rail that is off-screen. Flip it upward with
  `bottom: calc(100% + ...)` / `top: auto`.
- **Clipping.** `overflow` on an ancestor clips absolutely-positioned
  descendants no matter their z-index. Never put `overflow-y: auto` on the rail
  itself — put it on the nav list, which has no absolute children, so footer
  menus stay free.
- **Width assumptions.** A `min-width` sized for a wide bar can exceed the rail.

Fix these in the new sidebar's scoped styles with `:deep()` rather than editing
the shared components, so other consumers are unaffected.

## Step 4 — Global polish, surgically

Restyle the shared global classes the views already use (cards, stat tiles,
tables, badges). Consistent radius, one shadow treatment, one spacing scale.
Because these are global, this reaches every page with a small diff. Resist
touching a view file to "match" — if a view looks wrong afterward, that is a
finding to report, not a license to widen scope.

## Step 5 — Verify and report honestly

Run, in this order, and paste real output:

1. Production build — catches template/compile errors.
2. The existing test suite — compare against the Step 1 baseline number.
3. Load **every** route from Step 1 in a browser. Check for console errors and
   layout breakage, and open any menu you moved into the rail.

A build does not render a page. If the browser shows the old UI, trust the
browser and find out why before concluding anything. Separate pre-existing
failures from ones you caused, and prove which is which. Report failures as
failures; if you skipped a check, say so.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll pick a nicer palette" | The app has a palette. Derive it. A redesign is not a rebrand. |
| "Just add an icon library, it's one package" | A dependency is the user's decision. Inline SVG. |
| "While I'm here I'll tidy this view's CSS" | Out of scope. Report it; don't do it. |
| "The build passed, it works" | A build does not render a page. Load every route. |
| "This selector is obviously unused" | Grep it. Obvious is how you delete something load-bearing. |
| "Labels are just strings, I'll hardcode them" | Check for i18n keys first. A label with no key stays literal. |
| "The dropdown will be fine in the sidebar" | It opens downward off-screen and gets clipped. Read its CSS. |
| "The page still looks old, must be cache" | Maybe the files changed under you. Verify what the server serves. |
| "I'll present the plan and get started" | Step 2 is a stop. Approval is the gate. |
