"""
Experiment 1 from Sternberg, 1966.

Sternberg, S. (1966). High-speed scanning in human memory. Science, 153(3736), 652–654
"""

from typing import Final, Literal
import random
import traceback
from dataclasses import dataclass

from psychopy import monitors, visual, core
from psychopy.hardware import keyboard

from src.experiment import Base


DIGITS = list("0123456789")
Response = Literal["j", "f"]

class Experiment(Base):

    MIN_SET_SIZE = 1
    MAX_SET_SIZE = 6
    YES: Final[Response] = "j"
    NO: Final[Response] = "f"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_center.height = 0.12

    def generate_trial(self, set_size: None | int = None):
        """generate a single trial with random set size if not specified"""

        # generate memory set
        if set_size is None:
            set_size  = random.randint(self.MIN_SET_SIZE, self.MAX_SET_SIZE)
        negatives = list(DIGITS)
        positives = []
        for _ in range(set_size):
            d = random.choice(negatives)
            negatives.remove(d)
            positives.append(d)

        # generate probe
        weights = [1/len(DIGITS)]*len(DIGITS)
        for i in positives:
            weights[int(i)] = 1/(2*len(positives))
        for i in negatives:
            weights[int(i)] = 1/(2*len(negatives))
        probe = random.choices(DIGITS, weights=weights, k=1)[0]
        correct_response = self.YES if probe in positives else self.NO

        return Trial(
            set_size=set_size,
            memory_set="".join(positives),
            probe=probe,
            correct_response=correct_response
        )
    
    def generate_trials(self, n: int):
        """generate n many trials where each set size has equal trials if possible"""

        # generate for each length
        trials: list[Trial] = []
        if n >= self.MAX_SET_SIZE:
            m = n//self.MAX_SET_SIZE
            for i in range(self.MIN_SET_SIZE, self.MAX_SET_SIZE+1):
                for _ in range(m):
                    trial = self.generate_trial(i)
                    trials.append(trial)

        # generate for remaning size
        rem = n%self.MAX_SET_SIZE
        for _ in range(rem):
            trial = self.generate_trial() # with random set size
            trials.append(trial)

        random.shuffle(trials)
        return trials
    
    def show_probe(self, probe: str):
        self.present(probe, self.kb.clock.reset)
        while True:
            key = self.kb.waitKeys(keyList=[self.YES, self.NO, self.QUIT_KEY], waitRelease=False)[0]
            if key.name == self.QUIT_KEY:
                self.abort_requested = True
                continue
            return key

    def run_trial(self, trial: "Trial"):
        self.fixation(dur=1.0)
        self.show_stimulus(trial.memory_set, dur=1.2)
        self.delay(dur=2.0)
        key = self.show_probe(trial.probe)
        is_correct = trial.correct_response == key.name
        if is_correct:
            self.show_stimulus("Correct", dur=0.5)
        else:
            self.show_stimulus("Incorrect", dur=0.5)
        response = key.name
        return TrialResult(
            trial=trial,
            response=response,
            response_time=round(key.rt, 3),
            is_correct=(response == trial.correct_response)
        )

    def run(self, n: int):
        self.results: list[TrialResult] = []
        try:
            self.trials = self.generate_trials(n)
            self.waiting_start()
            self.delay(dur=1.0)
            for trial in self.trials:
                result = self.run_trial(trial)
                self.results.append(result)
                self.check_quit()
                if self.abort_requested:
                    break
        except Exception:
            traceback.print_exc()
        finally:
            self.win.close()


@dataclass
class Trial:
    set_size:         int
    memory_set:       str
    probe:            str
    correct_response: Response


@dataclass
class TrialResult:
    trial:         Trial
    response:      Response
    response_time: float
    is_correct:    bool


if __name__ == "__main__":
    # monitor = monitors.Monitor("MacBook Air 13.6 inch", width=30.41, distance=60)
    # monitor.setSizePix([2560, 1664])
    # TODO: add units="deg" in monitor
    experiment = Experiment()
    experiment.run(10)
    experiment.save_csv(participant_id="01", session_id=1, task_name="sternberg")
    core.quit()
