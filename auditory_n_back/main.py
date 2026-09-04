"""
Auditory N-Back task implementation.
"""

from typing import Final, Literal
from dataclasses import dataclass
import random
from typing import Any
import traceback

from src.experiment import Base


# default stimulus set consists of 28 Turkish letters excluding Ğ (soft G),
recordings = ["Aa", "Be", "Ce", "Çe", "De", "Ee", "Fe", "Ge", "He", "Iı", "İi", "Je",
              "Ke", "Le", "Me", "Ne", "Oo", "Öö", "Pe", "Re", "Se", "Şe", "Te", "Uu",
              "Üü", "Ve", "Ye", "Ze"]

# list corresponding to file names
dataset = [f'auditory_n_back/recordings/{r}.wav' for r in recordings]


TrialType = Literal["target", "non-target"]
Response = Literal["j", "f", "*"] # "*" meaning either "j" or "f"

@dataclass
class Trial:
    trial_type:       TrialType
    stimulus:         int
    correct_response: Response


@dataclass
class TrialResult:
    trial:         Trial
    response:      Response
    reaction_time: float
    is_correct:    bool


class Audio_N_Back(Base):

    YES: Final[Response] = "j"
    NO:  Final[Response] = "f"
    ANY: Final[Response] = "*"

    def __init__(self, n_back: int, dataset: list[str] = dataset, *args, **kwargs):
        """
        Initialize Audio N-Back task with parameter n_back.
        Dataset is a list consisting of path for each audio stimulus, default is Turkish letters.
        """
        if not isinstance(n_back, int): raise TypeError()
        if n_back < 1: raise ValueError()
        super().__init__(*args, **kwargs)
        self.n_back = n_back
        self.dataset = dataset

    def generate_trials(self, n_trials: int, ratio: float):
        """
        Generate n_trials many trials where ratio is number of target trials over all trials.
        """
        if not isinstance(n_trials, int): raise TypeError()
        if not isinstance(ratio, float): raise TypeError()
        if 0 > ratio or 1 < ratio: raise ValueError()

        # calculate number of target trials based on ratio to guarantee the number
        n_targets = round(n_trials * ratio)

        # randomly generate target trial indices, ensuring i >= n_back
        target_indices = sorted(random.sample(range(self.n_back, n_trials), n_targets))

        trials: list[Trial] = []
        len_dataset = len(self.dataset)

        # generate trials
        for i in range(n_trials):
            if i < self.n_back:
                # first n_back trials are non-target
                trials.append(Trial(
                    trial_type="non-target",
                    stimulus=random.randint(0, len_dataset),
                    correct_response=self.ANY
                ))
                continue
            nback_stim = trials[i-self.n_back].stimulus
            if i not in target_indices:
                # generate non-target trial
                # target trial cannot be the same as nback_stim
                trials.append(Trial(
                    trial_type="non-target",
                    stimulus=random.choice([x for x in range(len_dataset) if x != nback_stim]),
                    correct_response=self.NO
                ))
            else:
                # generate target trial
                # target trial is the same as nback_stim
                trials.append(Trial(
                    trial_type="target",
                    stimulus=nback_stim,
                    correct_response=self.YES
                ))

        return trials

    def run_trial(self, trial: Trial):
        """
        Run given trial.
        """
        if not isinstance(trial, Trial): raise TypeError()

        # play audio stimulus
        aud_dur = self.play_audio(self.dataset[trial.stimulus])
        # wait for response and save reaction time, accuracy
        self.present("Respond", self.kb.clock.reset)

        key: Any
        while True:
            key = self.kb.waitKeys(keyList=[self.YES, self.NO, self.QUIT_KEY], waitRelease=False)[0]
            if key.name == self.QUIT_KEY:
                self.abort_requested = True
                continue
            break
        response = key.name
        is_correct = trial.correct_response == self.ANY or trial.correct_response == response

        feedback = "Correct" if is_correct else "Incorrect"
        self.show_stimulus(feedback, dur=0.5)

        return TrialResult(
            trial=trial,
            response=response,
            reaction_time=round(key.rt, 3),
            is_correct=is_correct
        )
                
    def run(self, n_trials: int, ratio: float):
        """
        Generate n_trials many trials by runnig generate_trials(),
        and then run all trials.
        """
        if not isinstance(n_trials, int): raise TypeError()
        if not isinstance(ratio, float): raise TypeError()
        if 0 > ratio or 1 < ratio: raise ValueError()
        self.results: list[TrialResult] = []

        try:
            # generate trials
            self.trials = self.generate_trials(n_trials, ratio)
            # show waiting screen
            aborted = self.waiting_start()

            # start task if not quited
            if not aborted:
                self.delay(dur=1.0)
                # run individual trials and save results 
                for trial in self.trials:
                    result = self.run_trial(trial)
                    print(result)
                    self.results.append(result)
                    # end task if quited
                    self.check_quit()
                    if self.abort_requested: break
                    self.delay(dur=0.5)

        except Exception:
            traceback.print_exc()

        finally:
            self.win.close()
