"""
Sample run for Sternberg Task.
"""

from psychopy import core

from .main import Sternberg


if __name__ == "__main__":
    task = Sternberg()
    trial_n = 10
    task.run(trial_n)
    task.save_csv(participant_id="001", session_id=1, task_name="sternberg")
    core.quit()
