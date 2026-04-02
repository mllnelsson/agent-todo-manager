---
name: coding-guidelines
description: General coding guidelines that apply across all languages. Use when writing or reviewing code in any language. These are guiding principles — code breaking these standards is generally not accepted.
---

# Coding Guidelines

## Single responsibility

Everything should do one thing and one thing well. This applies to modules, functions, and data types. If something does too much, split it.

```
# bad: one function that fetches, transforms, and saves
# good: fetch_data / transform_data / save_data — each focused
```

## Naming clarity

Names should be descriptive and self-documenting. A good name eliminates the need for a comment.

- Prefer full words over abbreviations (`user_id` not `uid`, `calculate_total` not `calc_tot`)
- Name functions after what they do, data after what they represent
- Avoid generic names like `data`, `info`, `temp`, `obj`

## Pure functions

Prefer functions that take input and return output without side effects. Separate data transformation from I/O.

```
# good: transform is pure, caller decides what to do with result
# bad: function both transforms and writes to disk/network
```

Side effects (I/O, mutation, logging) should be pushed to the edges of the system.

## Data as values

Model data as plain, logic-free structures. Data objects carry state, not behavior — functions transform them.

```
# good: data is inert, functions do the work
user = get_user(id)
user = normalize(user)
save(user)

# bad: data object drives its own lifecycle
user.fetch()
user.normalize()
user.save()
```

## Enums and pattern matching

Model finite sets of options as enums. Use exhaustive pattern matching to handle them — never a chain of if/else.

This makes missing cases a compiler/runtime error rather than a silent bug, and makes intent explicit.

```
# bad: if status == "active" / elif status == "inactive" / else ...
# good: enum Status { Active, Inactive } + match/switch on Status
```

## No magic values

Do not embed unexplained literals in logic. Bind them to named constants that communicate intent.

```
# bad: if retries > 3
# good: MAX_RETRIES = 3 / if retries > MAX_RETRIES
```

## Error handling

Define domain-specific error types rather than raising generic errors. Catch and handle errors at system boundaries only (CLI entry points, API handlers) — not deep in business logic.

Each language has its own mechanism (exceptions, Result types, etc.) but the concept is universal.

## Public API surface

Expose only what callers need. Keep internals private. Modules should present a minimal, intentional public interface — implementation details stay hidden.

This applies at every level: functions within a file, modules within a package, packages within a system.

## Language specific

These guidelines apply on top of the general rules above. Read the relevant one when working in that language.

- **Python** → `read coding-guidelines/python/SKILL.md`
