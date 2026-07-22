from psychopy import monitors, visual, core
from psychopy.hardware import keyboard


WINDOW_SIZE = (800, 600)
MONITOR = monitors.Monitor("MacBook Air 13.6 inch", width=30.41, distance=60)
MONITOR.setSizePix([2560, 1664])


class Base:

    QUIT_KEY = "q"

    def __init__(self):
        self.win = visual.Window(
            monitor=MONITOR,
            size=WINDOW_SIZE,
            color=(-1, -1, -1)
        )
        self.kb = keyboard.Keyboard()
        self.text_center = visual.TextStim(self.win, "", color=(1, 1, 1))
        self.abort_requested = False

    def present(self, text):
        self.text_center.text = text
        self.text_center.draw()
        self.win.flip()

    def wait(self, dur):
        timer = core.Clock()
        while timer.getTime() < dur:
            self.check_quit()
            core.wait(0.001)

    def check_quit(self):
        if self.kb.getKeys([self.QUIT_KEY], waitRelease=False):
            self.abort_requested = True

    def fixation(self, dur, cross="+"):
        self.present(cross)
        self.wait(dur)

    def show_stimulus(self, stimulus, dur):
        self.present(stimulus)
        self.wait(dur)

    def delay(self, dur):
        self.win.flip()
        self.wait(dur)
    
    def waiting_start(self):
        self.kb.clearEvents()
        self.present("Press SPACE to start")
        self.kb.waitKeys(keyList=["space"], waitRelease=False)[0]
    