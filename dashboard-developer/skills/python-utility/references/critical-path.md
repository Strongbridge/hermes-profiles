# Critical Path Method — Pattern Notes

## Algorithm

CPM = forward pass (ES/EF) + backward pass (LS/LF) + float = LS - ES.
Critical = float == 0 (use `abs(float) < 1e-9`, never `== 0` — float arithmetic).

## Data Model

```python
@dataclass
class Task:
    name: str
    duration: float
    predecessors: list[str]
    early_start: float = 0
    early_finish: float = 0
    late_start: float = 0
    late_finish: float = 0
    total_float: float = 0
    is_critical: bool = False
```

## Topological Sort (Kahn's)

In-degree map → queue of zero-in-degree nodes → peel off, decrement children. Cycle if result.len != tasks.len.

## Validation Gates

1. Unknown predecessor name → error before calculation
2. Cycle → error (DFS gray-set or Kahn's result check)
3. Negative duration → error on task creation

## Merge-Point Verification

Parallel paths converging on one successor: longest path drives ES of successor. Shorter path gets float = diff. Always assert at merge points — this is where float errors hide.

## Output Format

Return structured dict from `.calculate()`: `{duration, critical_path[], tasks[{name, duration, predecessors, ES, EF, LS, LF, float, critical}]}`. Display via separate `.print_schedule()` — keeps engine testable.
