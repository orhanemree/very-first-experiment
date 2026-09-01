"""
Sample run for Sternberg Task.
"""

from .main import Sternberg


if __name__ == "__main__":
    task = Sternberg()
    task.run(n_trials=10)
    task.save_csv(participant_id="001", session_id=1, task_name="sternberg")
    task.terminate()
