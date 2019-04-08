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

PlexClient = None


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
            json.dump(self.data, fp)

    def run(self):
        try:
            self.controller.run_tutorial()

            # tutorial
            i = 0
            while not self.controller.end_task or i < 10:
                self.controller.run_trial(has_nogo=True)
                self.save()
                i += 1
                if event.getKeys(keyList=['escape']):
                    raise EscapeKeyPressed()
        except EscapeKeyPressed:
            print("Escape key pressed. Exiting.")

        # # Go only
        # i = 0
        # while not self.controller.end_task or i < 10:
        #     self.controller.run_trial(has_nogo=False)
        #     i += 1
        #     self.save()  # save data after each trial
        #     if event.getKeys(keyList=['escape']):
        #         break
        #
        # # Go and no go
        # i = 0
        # while not self.controller.end_task or i < 10:
        #     i += 1
        #     self.controller.run_trial(has_nogo=True)
        #     self.save()  # save data after each trial
        #     if event.getKeys(keyList=['escape']):
        #         break
