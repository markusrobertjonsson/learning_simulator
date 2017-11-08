from LsConstants import *
import LsUtil
from LsExceptions import LsParseException


class World():
    '''A world, returning a sequence of stimuli, depending on the incoming sequence of responses.'''

    def __init__(self, phases):
        # list of PhaseWorld objects
        self.phases = phases

        self.nphases = len(phases)
        self.curr_phaseind = 0

    def next_stimulus(self, response):
        ''' Returns a stimulus-tuple and current phase label.'''
        curr_phase = self.phases[self.curr_phaseind]
        stimulus = curr_phase.next_stimulus(response)
        if stimulus is None:  # Phase done
            if self.curr_phaseind + 1 >= self.nphases:  # No more phases
                return None, curr_phase.label
            else:  # Go to next phase
                self.curr_phaseind += 1
                return self.next_stimulus(response)
        else:
            return stimulus, curr_phase.label

    def subject_reset(self):
        self.curr_phaseind = 0
        for phase in self.phases:
            phase.subject_reset()


class PhaseWorld():
    '''A world (experiment) representation, represented by a "@phase" section in an LS script.'''

    def __init__(self, rows, pvdict, stimulus_elements, behaviors):
        self.label = pvdict[LABEL]
        self.endphase_str = pvdict[END]
        self.endphase_obj = None
        self.phase_lines = dict()
        self.first_label = None
        self._create(rows, stimulus_elements, behaviors)

        self.curr_lineobj = None
        self.subject_reset()

    def _create(self, rows, stimulus_elements, behaviors):
        linelabels = list()
        phase_lines_afterlabel = list()

        # First iteration through lines: Create list of lines (and labels)
        for row in rows:
            label, afterlabel = LsUtil.split1_strip(row)
            if afterlabel is None:
                raise Exception('Error on line\n"{}"'.format(row))
            coincide_err = "The phase line label '{0}' coincides with the name of a "
            if label in stimulus_elements:
                raise LsParseException((coincide_err + "stimulus element.").format(label))
            if label in behaviors:
                raise LsParseException((coincide_err + "behavior.").format(label))
            linelabels.append(label)
            phase_lines_afterlabel.append(afterlabel)
            if self.first_label is None:
                self.first_label = label

        # Second iteration: Create PhaseLine objects for all lines and put in the dict
        #                   self.phase_lines
        for i in range(len(linelabels)):
            label = linelabels[i]
            after_label = phase_lines_afterlabel[i]
            self.phase_lines[label] = PhaseLine(label, after_label, linelabels,
                                                stimulus_elements, behaviors)

    def subject_reset(self):
        self.endphase_obj = EndPhaseCondition(self.endphase_str)
        self._make_current_line(self.first_label)
        self.prev_linelabel = None
        self.first_stimulus = True

    def next_stimulus(self, response):
        if self.first_stimulus:
            rowlbl = self.first_label
            stimulus = self.curr_lineobj.stimulus
            self.first_stimulus = False
        else:
            rowlbl = self.curr_lineobj.next_row(response, self.prev_linelabel)
            stimulus = self.phase_lines[rowlbl].stimulus
            self.prev_linelabel = self.curr_lineobj.label
            self._make_current_line(rowlbl)

        if self.endphase_obj.is_met():
            return None
        else:
            self.endphase_obj.update_itemfreq(rowlbl)
            self.endphase_obj.update_itemfreq(stimulus)
            self.endphase_obj.update_itemfreq(response)
        return stimulus

    def _make_current_line(self, label):
        # self.curr_linelabel = label
        self.curr_lineobj = self.phase_lines[label]
        # self.endphase_obj.update_itemfreq(label)


class PhaseLine():
    def __init__(self, label, after_label, all_linelabels, stimulus_elements, behaviors):
        self.label = label
        self.consec_linecnt = 1
        self.consec_respcnt = 1
        self.prev_response = None

        stimulus, conditions_str = LsUtil.split1_strip(after_label, PHASEDIV)
        if conditions_str is None:
            raise LsParseException("Line with label {} has no conditions.".format(label))
        stimulus_is_tuple, stimulus_tuple = LsUtil.is_tuple(stimulus)
        if not stimulus_is_tuple:
            stimulus = LsUtil.strip_quotes(stimulus)  # Accept stimulus with or without quotes
            stimulus_tuple = (stimulus,)
        for element in stimulus_tuple:
            if element not in stimulus_elements:
                raise LsParseException("Unknown stimulus element '{}'.".format(element))
        self.stimulus = stimulus_tuple
        self.conditions = PhaseLineConditions(conditions_str, stimulus_elements,
                                              behaviors, all_linelabels)

    def next_row(self, response, prev_linelabel):
        if prev_linelabel == self.label:
            self.consec_linecnt += 1
            if self.prev_response == response:
                self.consec_respcnt += 1
            else:
                self.consec_respcnt = 1
        else:
            self.consec_linecnt = 1
            self.consec_respcnt = 1
        self.prev_response = response
        label = self.conditions.next_row(response, self.consec_linecnt, self.consec_respcnt)
        return label


class PhaseLineConditions():
    def __init__(self, conditions_str, stimulus_elements, behaviors, all_linelabels):
        # list of PhaseLineCondition objects
        self.conditions = list()

        self.conditions_str = conditions_str
        conditions = conditions_str.split(PHASEDIV)
        conditions = [c.strip() for c in conditions]
        for condition_str in conditions:
            condition_obj = PhaseLineCondition(condition_str, stimulus_elements, behaviors,
                                               all_linelabels)
            self.conditions.append(condition_obj)

    def next_row(self, response, consec_linecnt, consec_respcnt):
        for condition in self.conditions:
            condition_met, label = condition.is_met(response, consec_linecnt, consec_respcnt)
            if condition_met:
                return label
        raise Exception("No condition in '{0}' was met for response '{1}'.".
                        format(self.conditions_str, response))


class PhaseLineCondition():
    def __init__(self, condition_str, stimulus_elements, behaviors, all_linelabels):
        # Before colon
        self.response = None
        self.count = None

        # After colon
        self.goto = list()  # List of 2-tuples (probability, row_label)

        # To speed up random row selection
        self.goto_prob_cumsum = None

        self._parse(condition_str, stimulus_elements, behaviors, all_linelabels)

    def is_met(self, response, consec_linecnt, consec_respcnt):
        ismet = False
        if (self.response is None) and (self.count is None):
            ismet = True
        elif (self.response is None) and (self.count is not None):
            ismet = (consec_linecnt >= self.count)
        elif (self.response is not None) and (self.count is None):
            ismet = (response == self.response)
        elif (self.response is not None) and (self.count is not None):
            ismet = (response == self.response) and (consec_respcnt >= self.count)

        if ismet:
            label = self._goto_if_met()
            if label is None:  # In "ROW1(0.1),ROW2(0.3)", goto_if_met returns None with prob. 0.6
                ismet = False
        else:
            label = None
        return ismet, label

    def _goto_if_met(self):
        tuple_ind = LsUtil.weighted_choice(self.goto_prob_cumsum)
        if tuple_ind is None:
            return None
        else:
            return self.goto[tuple_ind][1]

    def _parse(self, condition_str, stimulus_elements, behaviors, all_linelabels):
        if condition_str.count(':') > 1:
            raise LsParseException("Condition '{}' has more than one colon.".format(condition_str))
        lcolon, rcolon = LsUtil.split1_strip(condition_str, ':')
        if rcolon is None:
            rcolon = lcolon
            lcolon = None

        # ---------- First parse lcolon ----------
        if lcolon is not None:
            if '=' in lcolon:
                response, count_str = LsUtil.split1_strip(lcolon, '=')
                is_pos_int, intval = LsUtil.is_posint(count_str)
                if not is_pos_int:
                    raise LsParseException("Expected an integer, got '{}'.".format(count_str))
                self.count = intval
            else:
                isposint, intval = LsUtil.is_posint(lcolon)
                if isposint:
                    response = None
                    self.count = intval
                else:
                    response = lcolon

            # Allow response with or without quotes
            if response is not None:
                response = LsUtil.strip_quotes(response)

            # Check that response is valid
            if response is not None:
                if response not in behaviors:
                    raise LsParseException("Unknown response '{}'.".format(response))
                else:
                    self.response = response

        # ---------- Then parse rcolon ----------
        lbls_and_probs = rcolon.split(',')
        for lbl_and_prob in lbls_and_probs:
            if lbl_and_prob in all_linelabels:
                if len(lbls_and_probs) > 1:
                    raise LsParseException("Invalid condition '{}'.".format(lbls_and_probs))
                self.goto.append((1, lbl_and_prob))
            else:
                if '(' and ')' in lbl_and_prob:
                    if lbl_and_prob.count('(') > 1 or lbl_and_prob.count(')') > 1:
                        raise LsParseException("Invalid condition '{}'. Too many parentheses".format(lbl_and_prob))
                    if lbl_and_prob.find('(') > lbl_and_prob.find('('):
                        raise LsParseException("Invalid condition '{}'.".format(lbl_and_prob))
                    lindex = lbl_and_prob.find('(')
                    rindex = lbl_and_prob.find(')')
                    lbl = lbl_and_prob[0:lindex]
                    if lbl not in all_linelabels:
                        raise LsParseException("Invalid line label '{}'.".format(lbl))
                    prob_str = lbl_and_prob[(lindex + 1): rindex]
                    isprob, prob = LsUtil.is_prob(prob_str)
                    if not isprob:
                        raise LsParseException("Expected a probability, got {}.".format(prob_str))
                    for prob_lbl in self.goto:
                        if prob_lbl[1] == lbl:
                            raise LsParseException("Label {0} duplicated in {1}.".format(lbl, rcolon))
                    self.goto.append((prob, lbl))
                else:
                    raise LsParseException("Malformed condition '{}'.".format(condition_str))

        self.goto_prob_cumsum = list()
        cumsum = 0
        for prob_lbl in self.goto:
            cumsum += prob_lbl[0]
            self.goto_prob_cumsum.append(cumsum)
        if cumsum > 1:
            raise LsParseException("Sum of probabilities in '{0}'' is {1}>1.".format(rcolon, cumsum))


class EndPhaseCondition():
    def __init__(self, endcond_str):
        item, number_str = LsUtil.parse_equals(endcond_str)
        self.item = item
        isnumber, number = LsUtil.is_posint(number_str)
        if not isnumber:
            raise Exception("Error on condition {0}. {1} is not an integer.".format(endcond_str,
                            number))
        self.limit = number
        self.itemfreq = dict()

    def update_itemfreq(self, item):
        if type(item) is not tuple:
            item = (item,)
        for element in item:
            if element in self.itemfreq:
                self.itemfreq[element] += 1
            else:
                self.itemfreq[element] = 1

    def is_met(self):
        if self.item not in self.itemfreq:
            return False
        else:
            return self.itemfreq[self.item] >= self.limit
