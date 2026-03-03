# FLLUnearthedLorePlot

A Python tool that visualises task-completion time data collected during an FLL Unearthed round (2 min 30 sec timespan).

## What it does

* Accepts a Python list of time strings in `"M:SS"` or `"MM:SS"` format (range `00:00` – `2:30`).
* **`"00:00"` entries are treated separately** – they mean the team did *not* complete the task.
* Generates a PowerPoint-ready PNG with two panels:
  * **Left** – histogram of actual completion times (15-second bins), annotated with counts and a red callout for non-completions.
  * **Right** – donut chart showing the Completed vs. Not Done ratio.

## Requirements

```
pip install matplotlib numpy
```

## Usage

### Run the built-in demo

```bash
python visualize_tasks.py
# → saves task_completion.png in the current directory
```

### Use as a module

```python
from visualize_tasks import visualize

time_points = [
    "00:00", "00:00",          # did not do the task
    "0:45", "1:00", "1:30",
    "2:10", "2:25",
]

visualize(time_points, output_path="my_chart.png", title="My FLL Round")
```

| Parameter | Default | Description |
|---|---|---|
| `time_points` | *(required)* | List of `"M:SS"` strings |
| `output_path` | `"task_completion.png"` | Path for the saved PNG |
| `title` | `"FLL Unearthed – Task Completion Times"` | Chart title |

## Output

The saved PNG is 150 dpi and sized 14 × 6.5 inches – ideal for pasting directly into a PowerPoint slide.
