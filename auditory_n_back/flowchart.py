"""
The code that generated Figure 1.
"""

from src.flowchart import Scene, Flowchart
from .main import Audio_N_Back


if __name__ == "__main__":
    task = Audio_N_Back(n_back=1)
    task.text_main.height = .3

    flowchart = Flowchart(task)
    flowchart.add_scenes([
        Scene(lambda: task.present("+"), "fixation", "Fixation (1s)"),
        Scene(lambda: task.present("<<>>"), "audio", "Audio (waiting response)"),
        Scene(lambda: task.present("Correct"), "feedback", "Feedback (.5s)"),
        Scene(lambda: task.present(""), "delay", "Delay (.5s)"),
        Scene(lambda: task.present("<<>>"), "audio", "Audio (waiting response)"),
        Scene(lambda: task.present("Incorrect"), "feedback", "Feedback (.5s)"),
        Scene(lambda: task.present(""), "delay", "Delay (.5s)")
    ])

    flowchart.generate("auditory_n_back/fig/Figure_1.png")
    task.terminate()