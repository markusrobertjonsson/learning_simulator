from LsExceptions import LsParseException

from math import exp
from random import seed, random
seed()

STIMULUS_ELEMENTS = 'stimulus_elements'
BEHAVIORS = 'behaviors'
U = 'u'
C = 'behavior_cost'
START_V = 'start_v'
ALPHA_V = 'alpha_v'
ALPHA_W = 'alpha_w'
BETA = 'beta'
OMIT_LEARNING = 'omit_learning'

DEFAULT = 'default'

DEFAULTS = {START_V: {DEFAULT: 0},
            U: {DEFAULT: 0},
            C: {DEFAULT: 0},
            ALPHA_V: 1,
            ALPHA_W: 1,
            BETA: 1,
            OMIT_LEARNING: list()}

# -------------------------------------------------------------------------
# ----------------------     Base class for mechanisms     ----------------
# -------------------------------------------------------------------------


class Mechanism():
    '''Base class for mechanisms'''

    def __init__(self, **kwargs):
        # Required
        for required in [BEHAVIORS, STIMULUS_ELEMENTS]:
            if required not in kwargs:
                raise LsParseException("The parameter '" + required + "' is required.")
        self.behaviors = kwargs[BEHAVIORS]
        self.stimulus_elements = kwargs[STIMULUS_ELEMENTS]

        # Optional
        self.start_v = kwargs.get(START_V, DEFAULTS[START_V])
        self.alpha_v = kwargs.get(ALPHA_V, DEFAULTS[ALPHA_V])
        self.alpha_w = kwargs.get(ALPHA_W, DEFAULTS[ALPHA_W])
        self.beta = kwargs.get(BETA, DEFAULTS[BETA])
        self.omit_learning = kwargs.get(OMIT_LEARNING, DEFAULTS[OMIT_LEARNING])

        # Needs to be copies since they are input and they are altered
        self.u = dict(kwargs.get(U, DEFAULTS[U]))
        self.c = dict(kwargs.get(C, DEFAULTS[C]))

        for key in self.start_v:
            if (key != DEFAULT):
                if type(key) is not tuple:
                    raise LsParseException("Keys in {0} must be tuples or '{1}'.".format(START_V, DEFAULT))
                if len(key) != 2:
                    raise LsParseException("Keys in {0} must be tuples of length two or {1}.".format(START_V, DEFAULT))
                if (key[0] not in self.stimulus_elements):
                    raise LsParseException("Unknown stimulus element '{0}' in '{1}'".format(key[0], START_V))
                if (key[1] not in self.behaviors):
                    raise LsParseException("Unknown behavior '{0}' in '{1}'".format(key[1], START_V))
        if DEFAULT not in self.start_v:
            raise LsParseException("The parameter {0} must have the key '{1}'.".format(U, DEFAULT))

        for key in self.u:
            if (key != DEFAULT) and (key not in self.stimulus_elements):
                raise LsParseException("Unknown stimulus element '{0}' in '{1}'".format(key, U))
        if (DEFAULT not in self.u) and (set(self.stimulus_elements) != self.u.keys()):
                raise LsParseException("The parameter {0} must have the key '{1}' or be exhaustive.".format(U, DEFAULT))

        for key in self.c:
            if (key != DEFAULT) and (key not in self.behaviors):
                raise LsParseException("Unknown behavior '{0}' in '{1}'".format(key, C))
        if (DEFAULT not in self.c) and (set(self.behaviors) != self.c.keys()):
            raise LsParseException("The parameter {0} must have the key '{1}' or be exhaustive.".format(C, DEFAULT))

        self._initialize_uc()
        self.subject_reset()

    def subject_reset(self):
        self._initialize_v()
        self._initialize_w()
        self.prev_stimulus = None
        self.response = None

    def learn_and_respond(self, stimulus):
        ''' stimulus is a tuple. '''
        if self.prev_stimulus is not None and not (set(self.omit_learning) & set(stimulus)):
            '''Do not update if first time or if any stimulus element is in omit'''
            self.learn(stimulus)

        self.response = self._get_response(stimulus)
        self.prev_stimulus = stimulus
        return self.response

    def _get_response(self, stimulus):
        x = self._support_vector(stimulus)
        q = random() * sum(x)
        index = 0
        while q > sum(x[0:index + 1]):
            index += 1
        return self.behaviors[index]

    def _support_vector(self, stimulus):
        return support_vector_static(stimulus, self.behaviors, self.beta, self.v)

        # vector = []
        # for behavior in self.behaviors:
        #     value = 0
        #     for element in stimulus:
        #         value += exp(self.beta * self.v[(element, behavior)])
        #     vector.append(value)
        # return vector

    def _initialize_uc(self):
        # u
        for element in self.stimulus_elements:
            if element not in self.u:
                self.u[element] = self.u[DEFAULT]
        if DEFAULT in self.u:
            self.u.pop(DEFAULT)

        # c
        for behavior in self.behaviors:
            if behavior not in self.c:
                self.c[behavior] = self.c[DEFAULT]
        if DEFAULT in self.c:
            self.c.pop(DEFAULT)

    def _initialize_v(self):
        self.v = dict()
        for element in self.stimulus_elements:
            for behavior in self.behaviors:
                key = (element, behavior)
                self.v[key] = self.start_v.get(key, self.start_v[DEFAULT])

    def _initialize_w(self):
        self.w = dict()
        for element in self.stimulus_elements:
            # w should start with zero for all elements
            self.w[element] = 0


def support_vector_static(stimulus, behaviors, beta, v):
    vector = list()
    for behavior in behaviors:
        value = 0
        for element in stimulus:
            value += exp(beta * v[(element, behavior)])
        vector.append(value)
    return vector


# For postprocessing only
def probability_of_response(stimulus, behavior, behaviors, beta, v):
    x = support_vector_static(stimulus, behaviors, beta, v)
    index = behaviors.index(behavior)
    p = x[index] / sum(x)
    return p


# -------------------------------------------------------------------------
# ----------------------     Specific mechanisms        ----------------
# -------------------------------------------------------------------------


class RescorlaWagner(Mechanism):
    # def __init__(self, behaviors, stimulus_elements, u, c, start_v, alpha_v, beta):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def learn(self, stimulus):
        if self.prev_stimulus is None:
            return
        usum, vsum = 0, 0
        for element in stimulus:
            usum += self.u[element]
        for element in self.prev_stimulus:
            vsum += self.v[(element, self.response)]
        for element in self.prev_stimulus:
            self.v[(element, self.response)] += self.alpha_v * \
                (usum - vsum - self.c[self.response])


class Qlearning(Mechanism):
    # def __init__(self, behaviors, stimulus_elements, u, c, start_v, alpha_v, beta):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def learn(self, stimulus):
        usum = 0, 0
        for element in stimulus:
            usum += self.u[element]
        maxv = 0
        for element in self.prev_stimulus:
            vval = self.v[(element, self.response)]
            if vval > maxv:
                maxv = vval
        for element in self.prev_stimulus:
            self.v[(element, self.response)] += self.alpha_v * \
                (usum - maxv - self.c[self.response])


class SARSA(Mechanism):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def learn(self, stimulus):
        usum, vsum1, vsum2 = 0, 0, 0
        for element in stimulus:
            usum += self.u[element]
        for element in self.prev_stimulus:
            vsum1 += self.v[(element, self.response)]
        for element in self.stimulus:
            vsum2 += self.v[(element, self.response)]   # XXX ???
        for element in self.prev_stimulus:
            self.v[(element, self.response)] += self.alpha_v * \
                (usum + vsum2 - vsum1 - self.c[self.response])


class ActorCritic(Mechanism):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def learn(self, stimulus):
        vsum_prev, wsum_prev, usum, wsum = 0, 0, 0, 0
        for element in self.prev_stimulus:
            vsum_prev += self.v[(element, self.response)]
            wsum_prev += self.w[element]
        for element in stimulus:
            usum += self.u[element]
            wsum += self.w[element]

        delta = usum + wsum - wsum_prev - self.c[self.response]
        deltav = self.alpha_v * delta
        deltaw = self.alpha_w * delta

        # v
        for element in self.prev_stimulus:
            self.v[(element, self.response)] += deltav
        # w
        for element in self.prev_stimulus:
            self.w[element] += deltaw


class Enquist(Mechanism):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def learn(self, stimulus):
        vsum_prev, wsum_prev, usum, wsum = 0, 0, 0, 0
        for element in self.prev_stimulus:
            vsum_prev += self.v[(element, self.response)]
            wsum_prev += self.w[element]
        for element in stimulus:
            usum += self.u[element]
            wsum += self.w[element]
        # v
        delta = self.alpha_v * (usum + wsum - self.c[self.response] - vsum_prev)
        for element in self.prev_stimulus:
            self.v[(element, self.response)] += delta
        # w
        delta = self.alpha_w * (usum + wsum - self.c[self.response] - wsum_prev)
        for element in self.prev_stimulus:
            self.w[element] += delta
