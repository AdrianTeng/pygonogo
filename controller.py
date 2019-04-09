import numpy as np
from psychopy.core import CountdownTimer, Clock, StaticPeriod
import psychopy.event as event


class Controller:

    def __init__(self, pars, display, logger, joystick):
        self.pars = pars
        self.display = display
        self.trialnum = 0
        self.score = 0
        self.end_task = False
        self.mark_event = logger
        self.joystick = joystick

    def open_trial(self, has_nogo):
        self.trialnum += 1
        self.result = ''
        self.pts_this_trial = 0
        self.trial_over = False
        self.target_is_on = False
        self.input_received = False
        self.no_response = False
        self.response_timer = None
        self.rt = float('NaN')
        self.data = []

        numtargs = np.prod(self.pars['grid'])
        self.which_target = np.random.randint(0, numtargs)
        self.onset_interval = np.random.uniform(self.pars['min_onset'],
                                                self.pars['max_onset'])
        self.is_nogo = np.random.rand() < self.pars['frac_nogo'] if has_nogo else False
        if self.is_nogo:
            self.trial_type = 'no'
        else:
            self.trial_type = 'go'

        self.onset_countdown = CountdownTimer(self.onset_interval)

    def run_trial(self, has_nogo):
        self.open_trial(has_nogo)

        while not self.trial_over:
            self.wait_for_input()

            if self.input_received:
                self.handle_input()
                self.display_outcome()
            else:
                self.handle_no_input()

            self.refresh()

        self.close_trial()

        return self.data

    def wait_for_input(self):
        pressed = []
        while True:
            self.present_target()
            pressed = event.getKeys(keyList=['space', 'escape'])
            if 'escape' in pressed:
                self.end_task = True
                raise EscapeKeyPressed()
            elif pressed or (self.joystick and True in self.joystick.getAllButtons()):
                self.input_received = True
                break
            elif self.target_is_on and (self.response_timer.getTime() > self.pars['max_rt']):
                self.no_response = True
                break

    def present_target(self):
        if not self.target_is_on and self.onset_countdown.getTime() < 0:
            # rotate target into view
            self.display.onset(self.which_target, self.trial_type)
            self.target_is_on = True
            self.response_timer = Clock()

        self.display.draw()

    def handle_input(self):
        if self.target_is_on:
            self.result = 'hit'
            self.trial_over = True
            self.rt = self.response_timer.getTime()

            self.correct = not self.is_nogo
            if self.correct:
                self.pts_this_trial = self.calculate_points(self.pars,
                                                            self.rt)
                self.outcome_sound = self.display.cashsnd
            else:
                self.pts_this_trial = -self.pars['pts_per_correct']
                self.outcome_sound = self.display.buzzsnd

            self.outcome_delay = self.pars['disp_resp']

        else:
            self.result = 'premature'
            self.trial_over = True
            self.correct = False
            self.pts_this_trial = -self.pars['pts_per_correct']
            self.outcome_sound = self.display.firesnd
            self.outcome_delay = 0.3

        # remember to reset input
        self.input_received = False

    def handle_no_input(self):
        self.result = 'no response'
        self.correct = self.is_nogo
        self.trial_over = True

    def display_outcome(self):
        self.score += self.pts_this_trial

        # refresh screen
        self.outcome_sound.play()

        # during static period, code between start and complete will run
        iti = StaticPeriod()
        iti.start(self.outcome_delay)
        self.display.draw()
        iti.complete()

        # remove text overlay on target
        self.display.set_target_text(self.which_target, '')

    def refresh(self):
        if self.target_is_on:
            self.display.offset(self.which_target)
            self.display.draw()

    def close_trial(self):
        # print to screen
        self.mark_event(",".join(map(str, [self.trialnum, self.trial_type, self.result, self.rt, self.correct, self.pts_this_trial])))
        print('Trial {0:d}: Type {1}  Result: {2}  RT: {3:0.3g}  Correct: {4:d}  Points: {5:d}'.
              format(self.trialnum, self.trial_type, self.result, self.rt, self.correct, self.pts_this_trial))

    def calculate_points(self, pars, rt):
        return int(np.floor(pars['pts_per_correct'] * np.exp(
            -(rt - pars['pts_offset']) / pars['pts_decay'])))

    def run_message(self, message):
        self.display.display_message(message)
        while True:
            pressed = event.getKeys(keyList=['space', 'escape'])
            if 'escape' in pressed:
                raise EscapeKeyPressed()
            elif pressed:
                break


class EscapeKeyPressed(Exception):
    pass