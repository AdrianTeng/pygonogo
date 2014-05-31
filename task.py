"""
Class definition for task object.

TO DO:
* make task metaclass?
* task handles event loop, with list of functions to call each iteration?
"""

import initializers
import controller, display
from psychopy.core import monotonicClock, Clock
import psychopy.event as event

class Task:
    def __init__(self, taskname, subject):
        self.taskname = taskname
        self.subject = subject
        self.keep_running = True
        self.setup()

    def setup(self):
        self.pars = initializers.setup_pars("parameters.json")
        self.display = display.Display(self.pars)
        # plexon init here ...
        self.outfile = initializers.setup_data_file(self.taskname, 
            self.subject)
        self.controller = controller.Controller(self.pars, self.display)
        self.data = []

    def teardown(self):
        # plexon close here...
        self.display.close()

    def run(self):
        self.start_time = monotonicClock.getTime()

        self.killtimer = Clock()

        while not self.controller.end_task and self.killtimer.getTime() < 10:
            self.controller.run_trial()

            # save data

            # esc check

        # self.display.draw()
        # event.waitKeys()
        # self.display.onset(3, 'go')
        # clk = Clock()
        # while clk.getTime() < 2:
        #     self.display.draw()
        # self.display.offset(3)
        # clk.reset() 
        # while clk.getTime() < 2:
        #     self.display.draw()

        # event.waitKeys()