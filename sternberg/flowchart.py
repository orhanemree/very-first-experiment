"""
The code that generated Figure 1.
"""

from src.flowchart import Scene, Flowchart
from .main import Sternberg


if __name__ == "__main__":
    task = Sternberg()
    task.text_main.height = .3

    flowchart = Flowchart(task)
    flowchart.add_scenes([
        Scene(lambda: task.present("+"), "fixation", "Fixation (.5s)"),
        Scene(lambda: task.present("62840"), "memory_set", "Memory set (1s)"),
        Scene(lambda: task.present(""), "delay", "Delay (2s)"),
        Scene(lambda: task.present("2"), "probe", "Probe (waiting response)"),
        Scene(lambda: task.present("Correct"), "feedback", "Feedback (.5s)")
    ])

    flowchart.generate("sternberg/fig/Figure_1.png")
    task.terminate()