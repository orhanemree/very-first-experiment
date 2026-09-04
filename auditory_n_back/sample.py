"""
Sample run for Auditory N-Back Task with n=2.
"""

from .main import Audio_N_Back


if __name__ == "__main__":
    n_back = 2
    task = Audio_N_Back(n_back)
    task.run(n_trials=100, ratio=.35)
    task.save_csv(participant_id="001", session_id=1, task_name=f"audio_{n_back}_back")
    task.terminate()
