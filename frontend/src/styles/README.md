# styles

Design tokens (color palette, typography, corner radius) live in `tailwind.config.ts` at the frontend root — the single source of truth per `docs/PROJECT_PLAN_v2.md` Section 13.1. `src/index.css` just wires up Tailwind's layers. All components consume the `brand`/`success`/`warning`/`danger`/`info` theme colors rather than redefining values ad hoc.
