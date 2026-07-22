"""
Experiment 1 from Sternberg, 1966.

Sternberg, S. (1966). High-speed scanning in human memory. Science, 153(3736), 652–654
"""

import random
from dataclasses import dataclass
from typing import Literal
from psychopy import monitors, visual, core
from psychopy.hardware import keyboard

from src.experiment import Base


DIGITS = list("0123456789")

class Experiment(Base):

    MIN_SET_SIZE = 1
    MAX_SET_SIZE = 6
    YES = "j"
    NO  = "f"

    def __init__(self, particiant_id):
        super().__init__()
        self.participant_id = particiant_id

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
            memory_set=positives,
            probe=probe,
            correct_response=correct_response
        )
    
    def generate_trials(self, n):
        """generate n many trials where each set size has equal trials if possible"""

        # generate for each length
        trials = []
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
    
    def probe(self, probe):
        self.text_center.text = probe
        self.text_center.draw()
        self.win.callOnFlip(self.kb.clock.reset)
        self.win.flip()

        while True:
            key = self.kb.waitKeys(keyList=[self.YES, self.NO, self.QUIT_KEY], waitRelease=False)[0]
            if key.name == self.QUIT_KEY:
                self.abort_requested = True
                continue
            return key

    def run_trial(self, trial: "Trial"):
        self.fixation(dur=1.0)
        self.show_stimulus("".join(trial.memory_set), dur=1.2)
        self.delay(dur=2.0)
        key = self.probe(trial.probe)
        is_correct = trial.correct_response == key.name
        if is_correct:
            self.show_stimulus("Correct", dur=0.5)
        else:
            self.show_stimulus("Incorrect", dur=0.5)
        return TrialResult(
            trial=trial,
            response=key.name,
            response_time=key.rt
        )

    def run(self, n):
        self.results = []
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
        except Exception as e:
            print(e)
        finally:
            self.win.close()

    def save_csv(self, filename):
        with open(filename, "a+") as f:
            for result in self.results:
                f.write((f"{self.participant_id}, "
                    f"{result.trial.set_size}, "
                    f"{''.join(result.trial.memory_set)}, "
                    f"{result.trial.probe}, "
                    f"{result.trial.correct_response}, "
                    f"{result.response}, "
                    f"{result.response_time}\n"
                ))


@dataclass
class Trial:
    set_size:   int
    memory_set: list[str]
    probe:      str
    correct_response: Literal[Experiment.YES] | Literal[Experiment.NO]


@dataclass
class TrialResult:
    trial: None | Trial
    response: str
    response_time: float

    @property
    def is_correct(self):
        return self.response == self.trial.correct_response


if __name__ == "__main__":
    experiment = Experiment("1")
    experiment.run(10)
    experiment.save_csv("sterberg.csv")
    core.quit()