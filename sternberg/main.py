"""
Sternberg Task implementation.

Sternberg, S. (1966). High-speed scanning in human memory. Science, 153(3736), 652–654.
"""

from typing import Final, Literal
import random
import traceback
from dataclasses import dataclass

from src.experiment import Base


DIGITS = list("0123456789")
Response = Literal["j", "f"]

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
    reaction_time: float
    is_correct:    bool


class Sternberg(Base):

    MIN_SET_SIZE = 1
    MAX_SET_SIZE = 6
    YES: Final[Response] = "j"
    NO:  Final[Response] = "f"

    def __init__(self, *args, **kwargs):
        """
        Initialize Sternberg Task.
        """
        super().__init__(*args, **kwargs)
        self.text_main.height = 0.12

    def generate_trial(self, set_size: None | int = None):
        """
        Generate a single trial with given set size, random size if not specified.
        Return trial.
        """
        if not (isinstance(set_size, int) or set_size is None): raise TypeError()
        if set_size is not None:
            if self.MIN_SET_SIZE > set_size or self.MAX_SET_SIZE < set_size: raise ValueError()
        else:
            set_size  = random.randint(self.MIN_SET_SIZE, self.MAX_SET_SIZE)
        
        # generate memory set
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
    
    def generate_trials(self, n_trials: int):
        """
        Generate n trials in total, with an equal number from each set size.
        Return list of trials.
        """
        if not isinstance(n_trials, int): raise TypeError()
        if n_trials < 1: raise TypeError()

        # generate for divisible set size
        trials: list[Trial] = []
        if n_trials >= self.MAX_SET_SIZE:
            m = n_trials//self.MAX_SET_SIZE
            for i in range(self.MIN_SET_SIZE, self.MAX_SET_SIZE+1):
                for _ in range(m):
                    trial = self.generate_trial(i)
                    trials.append(trial)

        # generate for remaning size
        rem = n_trials%self.MAX_SET_SIZE
        for _ in range(rem):
            trial = self.generate_trial() # with random set size
            trials.append(trial)

        random.shuffle(trials)
        return trials
    
    def show_probe(self, probe: str):
        """
        Present probe and wait for response. Return key object.
        """
        if not isinstance(probe, str): raise TypeError()

        self.present(probe, self.kb.clock.reset)
        while True:
            key = self.kb.waitKeys(keyList=[self.YES, self.NO, self.QUIT_KEY], waitRelease=False)[0]
            if key.name == self.QUIT_KEY:
                self.abort_requested = True
                continue
            return key

    def run_trial(self, trial: Trial):
        """
        Run a single trial. Return trial result.
        """
        if not isinstance(trial, Trial): raise TypeError()

        self.fixation(dur=0.5)
        self.show_stimulus(trial.memory_set, dur=1.0)
        self.delay(dur=2.0)
        key = self.show_probe(trial.probe)
        response = key.name
        is_correct = trial.correct_response == response

        feedback = "Correct" if is_correct else "Incorrect"
        self.show_stimulus(feedback, dur=0.5)

        return TrialResult(
            trial=trial,
            response=response,
            reaction_time=round(key.rt, 3),
            is_correct=(response == trial.correct_response)
        )

    def run(self, n_trials: int):
        """
        Generate n trials and run all trials.
        """
        if not isinstance(n_trials, int): raise TypeError()
        if n_trials < 1: raise TypeError()
        self.results: list[TrialResult] = []

        try:
            # generate trials
            self.trials = self.generate_trials(n_trials)
            # show waiting screen
            aborted = self.waiting_start()

            # start task if not quited
            if not aborted:
                self.delay(dur=1.0)
                for trial in self.trials:
                    # run individual trials and save results 
                    result = self.run_trial(trial)
                    self.results.append(result)
                    # end task if quited
                    self.check_quit()
                    if self.abort_requested: break
                    self.delay(dur=0.5)

        except Exception:
            traceback.print_exc()

        finally:
            self.win.close()
