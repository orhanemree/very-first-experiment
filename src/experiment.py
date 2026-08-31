from collections.abc import Callable
from typing import Any
from dataclasses import asdict
from os import path
from datetime import datetime
import csv

from psychopy import monitors, visual, sound, prefs
from psychopy.hardware import keyboard


class Base:

    QUIT_KEY = "q"

    def __init__(self, window: None | visual.Window = None,
                 monitor: None | monitors.Monitor = None):
        if not (isinstance(window, visual.Window) or window is None): raise TypeError()
        if not (isinstance(monitor, monitors.Monitor) or monitor is None): raise TypeError()

        # PsychoPy objects
        if window is None:
            window = visual.Window(
            monitor=monitor,
            size=(800, 600),
            color=(-1, -1, -1),
            fullscr=False
        )
        self.win = window
        self.frame_rate = self.win.getActualFrameRate() or 60.0
        self.kb = keyboard.Keyboard()
        self.text_main = visual.TextStim(self.win, "", color=(1, 1, 1))

        # task objects
        self.trials  = []
        self.results = []
        self.abort_requested: bool = False

    def present(self, text: str, callOnFlip: None | Callable = None):
        """
        Draw text on screen. 
        (Stimulus is shown until it is overwritten.)
        """
        if not isinstance(text, str): raise TypeError()
        if not (isinstance(callOnFlip, Callable) or callOnFlip is None): raise TypeError()

        self.text_main.text = text
        self.text_main.draw()
        if callOnFlip:
            self.win.callOnFlip(callOnFlip)
        self.win.flip()

    def present_for(self, text: str, dur: float):
        """
        Draw text on screen and sleep for given duration.
        (Stimulus is shown for given duration.)
        """
        if not isinstance(text, str): raise TypeError()
        if not isinstance(dur, float): raise TypeError()

        n_frames = int(round(dur * self.frame_rate))
        self.text_main.text = text
        for _ in range(n_frames):
            self.text_main.draw()
            self.win.flip()
            self.check_quit()

    def check_quit(self):
        """
        Check if quit key pressed during any frame.
        This does not immediately abort task.
        Check abort_requested in run() to handle abort safely.
        """
        if self.kb.getKeys([self.QUIT_KEY], waitRelease=False):
            self.abort_requested = True

    def fixation(self, dur: float, cross: str = "+"):
        """
        Present fixation for given duration, + by default.
        """
        self.present_for(cross, dur)

    def mask(self, dur: float, mask: str = "#####"):
        """
        Present mask for given duration, ##### by default.
        """
        self.present_for(mask, dur)

    def show_stimulus(self, stimulus: str, dur: float):
        """
        Present textual stimulus for given duration by default.
        """
        self.present_for(stimulus, dur)

    def play_audio(self, audio_path: str):
        """
        Start playing audio file (in the background). Return audio duration.
        """
        if not isinstance(audio_path, str): raise TypeError()

        prefs.hardware["audioLib"] = ["sounddevice"] # type: ignore
        aud_stim = sound.Sound(audio_path)
        aud_dur = aud_stim.getDuration()
        aud_stim.play()
        return aud_dur

    def delay(self, dur: float):
        """
        Sleep for given duration.
        """
        self.present_for("", dur)
    
    def waiting_start(self):
        """
        Present default start screen, waiting for SPACE press.
        Return -1 if quit key pressed, return 0 if SPACE pressed.
        """
        self.kb.clearEvents()
        self.present("Press SPACE to start")
        key = self.kb.waitKeys(keyList=["space", self.QUIT_KEY], waitRelease=False)[0]
        if key.name == self.QUIT_KEY:
            self.abort_requested = True
            return -1
        return 0

    def run(self, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def _flatten_result(self, result):
        """
        Flatten a trial result to write into csv file.
        Is not to be called directly, called from save_csv().
        """
        d = asdict(result)
        flat = {}
        for key, value in d.items():
            if isinstance(value, dict):
                flat.update(value)
            else:
                flat[key] = value
        return flat

    def save_csv(self, participant_id: str, session_id: int, task_name: str,
                 out_dir: str = "data"):
        """
        Write task results into given csv file. Return createde filename.
        """
        if not self.results: return

        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{out_dir}/sub-{participant_id}_ses-{session_id:02d}_task-{task_name}_{date_str}.csv"
        rows = [self._flatten_result(r) for r in self.results]
        fieldnames = ["participant_id", "session_id", "trial_number"] + \
                     [k for k in rows[0].keys()]
        write_header = not path.exists(filename)

        with open(filename, "a+", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            for i, row in enumerate(rows, start=1):
                row["participant_id"] = participant_id
                row["session_id"] = session_id
                row["trial_number"] = i
                writer.writerow(row)

        return filename
