# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- **Dev server**: `cd EduNexus && npm run dev`
- **Build**: `cd EduNexus && npm run build` (runs vue-tsc + vite build)
- **Preview**: `cd EduNexus && npm run preview`
- **Type-check**: `cd EduNexus && npx vue-tsc --noEmit`

## Project Architecture

**EduNexus** is a Vue 3 + TypeScript + Vite education management platform with a dark-themed, Google AI Studio-inspired UI. It uses a multi-agent AI education concept.

### Tech Stack
- **Framework**: Vue 3 (Composition API with `<script setup lang="ts">`)
- **Build**: Vite 8 + vue-tsc 3 + TypeScript 6
- **Routing**: vue-router 4 (WebHistory mode)
- **Styling**: Tailwind CSS 3 + autoprefixer + postcss, dark-only theme with CSS variables
- **UI Components**: shadcn-vue (built on reka-ui, class-variance-authority, clsx, tailwind-merge)
- **Icons**: lucide-vue-next
- **Utilities**: @vueuse/core
- **Recommended IDE extension**: Vue.volar

### Directory Structure

```
EduNexus/
├── src/
│   ├── main.ts                    # App entry — creates Vue app, installs router, mounts
│   ├── App.vue                    # Root component (just <router-view />)
│   ├── style.css                  # Tailwind directives + global dark styles
│   ├── router/index.ts            # Route definitions
│   ├── layouts/
│   │   └── DashboardLayout.vue    # Main authenticated layout (sidebar + header + content)
│   ├── views/
│   │   ├── LoginView.vue          # Login page (unauthenticated)
│   │   ├── HomeView.vue           # Dashboard home with DAG visualization, agent status, profile
│   │   └── MainView.vue           # Additional view (not yet wired into router)
│   ├── components/
│   │   ├── AppSidebar.vue         # Sidebar navigation (console, courses, students, analytics, settings)
│   │   └── ui/                    # shadcn-vue components (button, card, sidebar, dialog, etc.)
│   └── lib/
│       └── utils.ts               # cn() helper (clsx + twMerge), valueUpdater
├── components.json                # shadcn-vue configuration
├── tailwind.config.js             # Tailwind config with shadcn-vue theme tokens
├── vite.config.ts                 # Vite config with @ alias to ./src
└── tsconfig*.json                 # TypeScript config (app + node references)
```

### Routes
- `/login` — LoginView (standalone, no layout)
- `/` — DashboardLayout wrapping HomeView (authenticated area with sidebar)

### UI Component Pattern
All shadcn-vue components follow the same pattern:
- Each component has a directory in `src/components/ui/` 
- The component `.vue` file uses `<script setup lang="ts">` with reka-ui's `Primitive` for polymorphic rendering
- Variants defined via `class-variance-authority` (cva)
- An `index.ts` barrel file exports the component and variant types
- Classes merged using `cn()` from `@/lib/utils`

### Path Aliases
- `@/` maps to `./src/` (configured in both vite.config.ts and tsconfig)
