"""
Class definition for task object.
"""

import sys
from psychopy.gui import DlgFromDict
import initializers
import controller
import display
import psychopy.event as event
import json

from controller import EscapeKeyPressed

NOGO_TRIALS = ['01110010101100011010', '10011110011110010000', '10001101010110101001', '00001100110011011101',
               '00011010101111101000']


class Task:

    def __init__(self):
        task_info = self.get_subject()
        self.taskname = task_info['Task Name']
        self.subject = task_info['Subject']
        self.setup()

    def get_subject(self):
        info = {"Task Name": 'gonogo', "Subject": 'test'}
        infoDlg = DlgFromDict(dictionary=info,
                              title='Enter a subject number or name')
        if infoDlg.OK:
            print(info)
        else:
            sys.exit()

        return info

    def setup(self):
        self.pars = initializers.setup_pars("parameters.json")
        self.display = display.Display(self.pars)
        self.data = []

        self.logger = initializers.setup_logging(self.data)
        self.outfile, self.parsfile = initializers.setup_data_file(
            self.taskname, self.subject)
        self.joystick = initializers.setup_joystick()
        self.controller = controller.Controller(self.pars, self.display,
                                                self.logger, self.joystick)

        # save task parameters
        with open(self.parsfile, 'w+') as fp:
            json.dump(self.pars, fp)

    def teardown(self):
        self.display.close()

    def save(self):
        with open(self.outfile, 'w+') as fp:
            fp.write("\n".join(self.data))

    def run(self):
        try:
            self.controller.run_message("Tutorial instructions here")

            # tutorial
            i = 0
            while not self.controller.end_task and i < 5:
                self.controller.run_trial(is_nogo=True)
                i += 1
                if event.getKeys(keyList=['escape']):
                    raise EscapeKeyPressed()
            self.controller.end_task = False

            for trial_set_count in range(4):
                self.controller.run_message("Go Only")
                # Go only
                i = 0
                while not self.controller.end_task and i < 20:
                    self.controller.run_trial(is_nogo=False)
                    self.save()  # save data after each trial
                    i += 1
                    if event.getKeys(keyList=['escape']):
                        break
                self.controller.end_task = False

                self.controller.run_message("Go and No-Go")
                # Go and no go
                i = 0
                trial_flavour = NOGO_TRIALS[trial_set_count]
                while not self.controller.end_task and i < 20:
                    self.controller.run_trial(is_nogo=int(trial_flavour[i]))
                    self.save()  # save data after each trial
                    i += 1
                    if event.getKeys(keyList=['escape']):
                        break
                self.controller.end_task = False
        except EscapeKeyPressed:
            print("Escape key pressed. Exiting.")
