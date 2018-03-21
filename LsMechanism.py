from LsExceptions import LsParseException
import LsConstants
import LsUtil

from math import exp
from random import seed, random
seed()

STIMULUS_ELEMENTS = 'stimulus_elements'
BEHAVIORS = 'behaviors'
RR = 'response_requirements'
U = 'u'
C = 'behavior_cost'
START_V = 'start_v'
ALPHA_V = 'alpha_v'
ALPHA_W = 'alpha_w'
BETA = 'beta'
OMIT_LEARNING = 'omit_learning'

ALL_PARAMETER_NAMES = {LsConstants.SUBJECTS,
                       LsConstants.MECHANISM,
                       STIMULUS_ELEMENTS,
                       BEHAVIORS,
                       RR,
                       U,
                       C,
                       START_V,
                       ALPHA_V,
                       ALPHA_W,
                       BETA,
                       OMIT_LEARNING}

DEFAULT = 'default'

DEFAULT_U_VALUE = 0
DEFAULT_C_VALUE = 0


def get_default(key):
    DEFAULTS = {START_V: {DEFAULT: 0},
                U: {DEFAULT: 0},
                C: {DEFAULT: 0},
                ALPHA_V: 1,
                ALPHA_W: 1,
                BETA: 1,
                RR: dict(),
                OMIT_LEARNING: list()}
    return DEFAULTS[key]

# -------------------------------------------------------------------------
# ----------------------     Base class for mechanisms     ----------------
# -------------------------------------------------------------------------


class Mechanism():
    '''Base class for mechanisms'''

    def __init__(self, **kwargs):
        for p in kwargs:
            if p not in ALL_PARAMETER_NAMES:
                raise LsParseException("Unknown parameter '{}'".format(p))

        # Required
        for required in [BEHAVIORS, STIMULUS_ELEMENTS]:
            if required not in kwargs:
                raise LsParseException("The parameter '" + required + "' is required.")
        self.behaviors = kwargs[BEHAVIORS]
        self.stimulus_elements = kwargs[STIMULUS_ELEMENTS]

        # Optional
        self.start_v = kwargs.get(START_V, get_default(START_V))
        self.alpha_v = kwargs.get(ALPHA_V, get_default(ALPHA_V))
        self.alpha_w = kwargs.get(ALPHA_W, get_default(ALPHA_W))
        self.beta = kwargs.get(BETA, get_default(BETA))
        self.omit_learning = kwargs.get(OMIT_LEARNING, get_default(OMIT_LEARNING))
        self.response_req = kwargs.get(RR, get_default(RR))

        # Needs to be copies since they are input and they are altered (in initialize_uc)
        self.u = dict(kwargs.get(U, get_default(U)))
        self.c = dict(kwargs.get(C, get_default(C)))

        # Be nice - if DEFAULT not given, assume it is DEFAULT_{UC}_VALUE
        if DEFAULT not in self.u:
            self.u[DEFAULT] = DEFAULT_U_VALUE
        if DEFAULT not in self.c:
            self.c[DEFAULT] = DEFAULT_C_VALUE

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
        if (DEFAULT not in self.u) and (set(self.stimulus_elements) != set(self.u.keys())):
                raise LsParseException("The parameter {0} must have the key '{1}' or be exhaustive.".format(U, DEFAULT))

        for key in self.c:
            if (key != DEFAULT) and (key not in self.behaviors):
                raise LsParseException("Unknown behavior '{0}' in '{1}'".format(key, C))
        if (DEFAULT not in self.c) and (set(self.behaviors) != set(self.c.keys())):
            raise LsParseException("The parameter {0} must have the key '{1}' or be exhaustive.".format(C, DEFAULT))

        if type(self.response_req) is not dict:
            raise LsParseException("{0} must be a dict.".format(RR))
        for key, val in self.response_req.items():
            if key not in self.behaviors:
                raise LsParseException("Unknown behavior '{0}' in {1}.".format(key, RR))
            if type(val) is str:
                if val not in self.stimulus_elements:
                    raise LsParseException("Unknown stimulus element {0} in {1}.".format(val, RR))
            elif type(val) is list:
                for e in val:
                    if e not in self.stimulus_elements:
                        raise LsParseException("Unknown stimulus element {0} in {1}.".format(val, RR))
            else:
                raise LsParseException("Value for {0} in {1} must be a string or a list of strings.".format(key, RR))

        # Make self.stimulus_req
        self.response_req = dict(self.response_req)  # Copy since input and will be altered
        for response in self.behaviors:
            if response not in self.response_req:
                self.response_req[response] = list(self.stimulus_elements)
        self.stimulus_req = LsUtil.dict_inv(self.response_req)

        # Check that all stimulus elements has at least one feasible response
        if set(self.stimulus_req) != set(self.stimulus_elements):
            elements_without_response = set(self.stimulus_elements) - set(self.stimulus_req)
            raise LsParseException("Invalid response_requirements: Stimulus elements {} has no possible responses.".format(elements_without_response))

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
        x, feasible_behaviors = self._support_vector(stimulus)
        q = random() * sum(x)
        index = 0
        while q > sum(x[0:index + 1]):
            index += 1
        return feasible_behaviors[index]

    def _support_vector(self, stimulus):
        return support_vector_static(stimulus, self.behaviors, self.stimulus_req,
                                     self.beta, self.v)

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


# feasible_behaviors_cache = dict()

def get_feasible_behaviors(stimulus, behaviors, stimulus_req):
    if not stimulus_req:  # If stimulus_req is empty
        return behaviors

    # if stimulus in feasible_behaviors_cache:
    #     return feasible_behaviors_cache[stimulus]

    feasible_behaviors = set()
    for element in stimulus:
        #if element in stimulus_req:
        for b in stimulus_req[element]:
            feasible_behaviors.add(b)
        #else:
        #    feasible_behaviors = behaviors
        #    break
    feasible_behaviors = list(feasible_behaviors)
    # feasible_behaviors_cache[stimulus] = feasible_behaviors
    return feasible_behaviors


def support_vector_static(stimulus, behaviors, stimulus_req, beta, v):
    feasible_behaviors = get_feasible_behaviors(stimulus, behaviors, stimulus_req)

    # XXX
    #print(stimulus)
    if stimulus == ("E3",):
        print("feasible behaviors for E3: {}".format(feasible_behaviors))

    vector = list()
    for behavior in feasible_behaviors:
        value = 0
        for element in stimulus:
            value += beta * v[(element, behavior)]
        value = exp(value)
        vector.append(value)
    return vector, feasible_behaviors


# For postprocessing only
def probability_of_response(stimulus, behavior, behaviors, stimulus_req, beta, v):
    x, feasible_behaviors = support_vector_static(stimulus, behaviors, stimulus_req, beta, v)
    index = feasible_behaviors.index(behavior)
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


'''class ActorCritic(Mechanism):
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
            self.w[element] += deltaw'''


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
        # v
        # Markus, I copied Enquist and just changed this row by replacing vsum_prev with wsum_prev
        delta = self.alpha_v * (usum + wsum - self.c[self.response] - wsum_prev)
        for element in self.prev_stimulus:
            self.v[(element, self.response)] += delta
        # w
        delta = self.alpha_w * (usum + wsum - self.c[self.response] - wsum_prev)
        for element in self.prev_stimulus:
            self.w[element] += delta


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
