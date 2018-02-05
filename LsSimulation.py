import LsOutput


class ScriptRun():

    '''A class for a script run.'''

    def __init__(self, runlabel, world, mechanism_obj, n_subjects):
        self.runlabel = runlabel
        self.world = world
        self.mechanism_obj = mechanism_obj
        self.has_w = hasattr(mechanism_obj, 'w')
        self.n_subjects = n_subjects

    def run(self):
        out = LsOutput.RunOutput(self.n_subjects, self.mechanism_obj.stimulus_req)

        # Initialize output with start values
        # first_phase_label = self.world.phases[0].label
        for subject_ind in range(self.n_subjects):
            for element in self.mechanism_obj.stimulus_elements:
                if self.has_w:
                    out.write_w(subject_ind, (element,), 0, self.mechanism_obj)
                for behavior in self.mechanism_obj.behaviors:
                    out.write_v(subject_ind, (element,), behavior, 0, self.mechanism_obj)
            out.write_step(subject_ind, self.world.phases[0].label, 0)

        # The actual simulation
        for subject_ind in range(self.n_subjects):
            step = 1
            subject_done = False
            response = None
            while not subject_done:
                stimulus, phase_label = self.world.next_stimulus(response)
                subject_done = (stimulus is None)
                if not subject_done:
                    prev_stimulus = self.mechanism_obj.prev_stimulus
                    prev_response = self.mechanism_obj.response
                    response = self.mechanism_obj.learn_and_respond(stimulus)

                    if prev_stimulus is not None:
                        if self.has_w:
                            out.write_w(subject_ind, prev_stimulus, step, self.mechanism_obj)
                        out.write_v(subject_ind, prev_stimulus, prev_response, step,
                                    self.mechanism_obj)
                        out.write_history(subject_ind, prev_stimulus, prev_response)
                        out.write_step(subject_ind, phase_label, step)
                        step += 1
                    last_stimulus = stimulus
                    last_response = response
                    # step += 1
                else:
                    #step -= 1
                    # Write last step to all variables (except the ones that were written in
                    # the last step)
                    if self.has_w:
                        for element in self.mechanism_obj.stimulus_elements:
                            if True:  # element not in last_stimulus:
                                out.write_w(subject_ind, (element,), step, self.mechanism_obj)
                    for element in self.mechanism_obj.stimulus_elements:
                        for behavior in self.mechanism_obj.behaviors:
                            if True: #(element not in last_stimulus) or (behavior!=last_response):
                                out.write_v(subject_ind, (element,), behavior, step,
                                            self.mechanism_obj)
                    out.write_history(subject_ind, last_stimulus, last_response)
                    #out.write_history(subject_ind, stimulus, response)
                    out.write_step(subject_ind, "last", step)

                    # Reset mechanism and world for the next subject
                    self.mechanism_obj.subject_reset()
                    self.world.subject_reset()

        return out
