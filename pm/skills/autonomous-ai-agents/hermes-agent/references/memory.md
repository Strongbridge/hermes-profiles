# Persistent Memory Management

The `memory` tool provides durable facts storage across sessions. Load it during review before reading or modifying existing memory entries.

## API Overview

### Add an entry
```python
memory(action='add', content='fact about the user', target='memory')
```

### Remove an entry
```python
memory(action='remove', old_text='exact text to delete', target='memory')
```

### Patch (edit) an entry
```python
memory(action='patch', old_text='old content', new_text='updated content', target='memory')
```

### Batch operations (atomic)
When capacity exceeds, combine remove + add in one operations array:
```python
memory(operations=[
    {'action': 'remove', 'old_text': 'entry to delete'},
    {'action': 'add', 'content': 'new entry'}
], target='memory')
```

## Capacity Limits

- Default limit: 2,200 characters
- Adding exceeds? Batch with remove operations to free space first
- Usage checked only on final batch result

## Common Pitfalls

- **Missing action parameter** — use `action='add'|'patch'|'remove'` or `operations=[...]`
- **Wrong parameter names** — `patch` requires both `old_text` AND `new_text`; `add` requires `content`
- **Read-before-write protection** — the memory file is protected after read; if write_file fails with stale-write error, the memory tool's add/patch works correctly as it manages state differently
- **Entry matching is exact** — `remove` and `patch` require the exact text that appears in the current entry

## Reading Current State

Use `memory` tool with no action to list current entries when capacity issues arise. The error response includes `current_entries` for diffing.

## File Location

Memory persists at `~/.hermes/memories/MEMORY.md` (profile-relative). Each entry is a paragraph separated by `§` markers.