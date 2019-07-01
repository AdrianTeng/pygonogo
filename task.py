"""
Class definition for task object.
"""

import sys
from os import getcwd
import os

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
        self.joystick = initializers.setup_joystick()
        self.controller = controller.Controller(self.pars, self.display,
                                                self.logger, self.joystick)


    def teardown(self):
        self.display.close()

    def save(self):
        final_score = len([i for i in self.data if i.endswith("1")])
        with open(os.path.join(getcwd(), "{}_{}.csv".format(self.taskname, self.subject)), 'w+') as fp:
            fp.write("\n".join(self.data))
            fp.write("\nFinal score={}".format(final_score))

    def run(self, shorten=False):
        try:
            self.controller.run_message('Please press "space" when you see 1-5, and do NOT click anything if you see 0',
                                        height=0.1)

            # tutorial
            i = 0
            while not self.controller.end_task and i < 5:
                self.controller.run_trial(is_nogo=bool(i % 2), event_type=None)
                i += 1
                if event.getKeys(keyList=['escape']):
                    raise EscapeKeyPressed()
            self.controller.end_task = False

            go_only_res = []
            go_nogo_res = []

            trial_count = 0
            for trial_set_count in range(4):
                trial_count += 1
                if not shorten or trial_set_count == 0:
                    self.controller.run_message("Trial {}".format(trial_count))
                    # Go only
                    i = 0
                    while not self.controller.end_task and i < 20:
                        go_only_res.append(self.controller.run_trial(is_nogo=False, event_type='go-only'))
                        i += 1
                        if event.getKeys(keyList=['escape']):
                            break
                    self.controller.end_task = False

                trial_count += 1
                self.controller.run_message("Trial {}".format(trial_count))
                # Go and no go
                i = 0
                trial_flavour = NOGO_TRIALS[trial_set_count]
                while not self.controller.end_task and i < 20:
                    go_nogo_res.append(self.controller.run_trial(is_nogo=int(trial_flavour[i]), event_type='go-nogo'))
                    i += 1
                    if event.getKeys(keyList=['escape']):
                        break
                self.controller.end_task = False
            self.save()
            self.controller.run_message("The end, thank you")
            print("Go only result: {}".format(sum(go_only_res)))
            print("Go/no go only result: {}".format(sum(go_nogo_res)))
            self.controller.run_message("Go only: {}, go-nogo: {}".format(sum(go_only_res), sum(go_nogo_res)))
        except EscapeKeyPressed:
            print("Escape key pressed. Exiting.")
