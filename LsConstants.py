# The keyword prefix
KWP = '@'

# Keywords
COMMENT = KWP + "comment"
PARAMETERS = KWP + "parameters"
PHASE = KWP + "phase"
RUN = KWP + "run"

FIGURE = KWP + "figure"
SUBPLOT = KWP + "subplot"
LEGEND = KWP + "legend"
WPLOT = KWP + "wplot"
VPLOT = KWP + "vplot"
PPLOT = KWP + "pplot"
NPLOT = KWP + "nplot"
WEXPORT = KWP + "wexport"
VEXPORT = KWP + "vexport"
PEXPORT = KWP + "pexport"
NEXPORT = KWP + "nexport"

ALL_PLOTCMDS = [WPLOT, VPLOT, PPLOT, NPLOT, SUBPLOT, FIGURE, LEGEND]
ALL_EXPORTCMDS = [WEXPORT, VEXPORT, PEXPORT, NEXPORT]
ALL_POSTCMDS = ALL_PLOTCMDS + ALL_EXPORTCMDS
ALL_KEYWORDS = [COMMENT, PARAMETERS, PHASE, RUN] + ALL_POSTCMDS

# @parameters
MECHANISM = "mechanism"
SUBJECTS = "subjects"
BEHAVIORS = "behaviors"
STIMULUS_ELEMENTS = "stimulus_elements"
BETA = "beta"

# Mechanism names
ENQUIST = 'ga'
RESCORLA_WAGNER = 'rescorla_wagner'
Q_LEARNING = 'q_learning'
SARSA = 'sarsa'
ACTOR_CRITIC = 'actor_critic'

# @phases
END = "end"
PHASEDIV = "|"

# @run
PHASES = "phases"

# Generic
LABEL = "label"

# Properties for evaluation
EVAL_SUBJECT = "subject"
EVAL_RUNLABEL = "runlabel"
EVAL_EXACTSTEPS = "exact_steps"
EVAL_EXACTN = "exact_n"
EVAL_CUMULATIVE = "cumulative"
EVAL_STEPS = "steps"
EVAL_PHASE = "phase"
EVAL_FILENAME = "filename"

# Property values for evaluation
EVAL_AVERAGE = "average"
EVAL_ON = "on"
EVAL_OFF = "off"
EVAL_ALL = "all"
