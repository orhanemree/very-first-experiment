from collections.abc import Callable
from typing import Any
from dataclasses import asdict
from os import path
from datetime import datetime
import csv

from psychopy import monitors, visual
from psychopy.hardware import keyboard


class Base:

    QUIT_KEY = "q"

    def __init__(self, monitor: None | monitors.Monitor = None,
                 window_size: tuple[int, int] = (800, 600),
                 window_color: tuple[int, int, int] = (-1, -1, -1),
                 window_fullscr: bool = False):
        self.win = visual.Window(
            monitor=monitor,
            size=window_size,
            color=window_color,
            fullscr=window_fullscr
        )
        # TODO: can specify monitor object
        self.frame_rate = self.win.getActualFrameRate() or 60.0
        self.kb = keyboard.Keyboard()
        self.text_center = visual.TextStim(self.win, "", color=(1, 1, 1))

        self.trials  = []
        self.results = []
        self.abort_requested: bool = False

    def present(self, text: str, callOnFlip: None | Callable = None):
        self.text_center.text = text
        self.text_center.draw()
        if callOnFlip:
            self.win.callOnFlip(callOnFlip)
        self.win.flip()

    def present_for(self, text: str, dur: float):
        n_frames = int(round(dur * self.frame_rate))
        self.text_center.text = text
        for _ in range(n_frames):
            self.text_center.draw()
            self.win.flip()
            self.check_quit()

    def check_quit(self):
        if self.kb.getKeys([self.QUIT_KEY], waitRelease=False):
            self.abort_requested = True
            # NOTE: this does not immediately abort,
            # check abort_requested in run() function
            # in order not to abort during a trial

    def fixation(self, dur: float, cross: str = "+"):
        self.present_for(cross, dur)

    def mask(self, dur: float, mask: str = "#####"):
        self.present_for(mask, dur)

    def show_stimulus(self, stimulus: str, dur: float):
        self.present_for(stimulus, dur)

    def delay(self, dur: float):
        self.present_for("", dur)
    
    def waiting_start(self):
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
        """Flatten a trial result to write into csv file, called from save_csv()"""
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
        if not self.results:
            return
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
