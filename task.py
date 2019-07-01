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
        correct_go_only = len([i for i in self.data if 'go-only' in i and ',go,' in i and i.endswith('1')])
        correct_positive_nogo = len([i for i in self.data if 'go-nogo' in i and ',go,' in i and i.endswith('1')])
        correct_negative_nogo = len([i for i in self.data if 'go-nogo' in i and ',no,' in i and i.endswith('1')])
        with open(os.path.join(getcwd(), "{}_{}.csv".format(self.taskname, self.subject)), 'w+') as fp:
            fp.write("\n".join(self.data))
            fp.write("\nCorrect Positive Go-Nogo={}".format(correct_positive_nogo))
            fp.write("\nCorrect Negative Go-Nogo={}".format(correct_negative_nogo))
            fp.write("\nCorrect Go-only={}".format(correct_go_only))

    def run(self, shorten=False):
        try:
            self.controller.run_message('Please press "space" when you see 1-5, and do NOT press anything if you see 0',
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
                if not shorten or trial_set_count == 0:
                    trial_count += 1
                    self.controller.run_message("Trial {}".format(trial_count), height=0.1)
                    # Go only
                    i = 0
                    while not self.controller.end_task and i < 20:
                        go_only_res.append(self.controller.run_trial(is_nogo=False, event_type='go-only'))
                        i += 1
                        if event.getKeys(keyList=['escape']):
                            break
                    self.controller.end_task = False

                trial_count += 1
                self.controller.run_message("Trial {}".format(trial_count), height=0.1)
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
            self.controller.run_message("The end, thank you", height=0.1)
            print("Go only result: {}".format(sum(go_only_res)))
            print("Go/no go only result: {}".format(sum(go_nogo_res)))
            self.controller.run_message("Go only: {}\nGo-Nogo: {}".format(sum(go_only_res), sum(go_nogo_res)), height=0.1)
        except EscapeKeyPressed:
            print("Escape key pressed. Exiting.")
