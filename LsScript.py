import LsUtil
import LsWorld
import LsMechanism
from LsOutput import ScriptOutput
from LsSimulation import ScriptRun
from LsExceptions import LsParseException
from LsConstants import *

import ast
import matplotlib.pyplot as plt


class LsScript():
    def __init__(self, script):
        self.script = clean_script(script)
        self.comment = Comment()
        self.parameters = Parameters()
        self.phases = Phases()
        self.runs = Runs()

        self.postcmds = PostCmds()

        # Used to label unlabelled @run-statements with "run1", "run2", ...
        self.unnamed_run_cnt = 1
        # Used to label unlabelled @phase-statements with "phase1", "phase2", ...
        self.unnamed_phase_cnt = 1

        self._parse()

    def _parse(self):
        blocks = LsUtil.strsplit(self.script, ALL_KEYWORDS)
        for block in blocks:
            postcmd, cmdarg = LsUtil.split1_strip(block)
            if postcmd in ALL_POSTCMDS:
                postcmd_obj = parse_postcmd(postcmd, cmdarg, self.parameters)
                self.postcmds.add(postcmd_obj)
                continue
            scriptblock = parse_block(block)
            kw = scriptblock.keyword
            if kw == COMMENT:
                self.comment.add(scriptblock)
            elif kw == PARAMETERS:
                self.parameters.add(scriptblock)
            elif kw == PHASE:
                if LABEL not in scriptblock.pvdict:
                    scriptblock.pvdict[LABEL] = self._next_unnamed_phase()
                if END not in scriptblock.pvdict:
                    raise LsParseException("The property 'end' is required in {}.".format(PHASE))
                self.phases.add(scriptblock, self.parameters)  # .clone()
            elif kw == RUN:
                # If 'phases' not specified, use empty tuple (which means all phases)
                phases_to_use = scriptblock.pvdict.get(PHASES, tuple())
                if type(phases_to_use) != tuple:  # Allow string for single phase
                    phases_to_use = (phases_to_use,)
                world = self.phases.make_world(phases_to_use)
                mechanism_obj = self.parameters.make_mechanism_obj()
                run_label = scriptblock.pvdict.get(LABEL, self._next_unnamed_run())
                n_subjects = self.parameters.parameters.get(SUBJECTS, 1)
                self.runs.add(run_label, world, mechanism_obj, n_subjects)
            else:
                raise LsParseException("Unknown keyword '{}'".format(kw))

    def run(self):
        return self.runs.run()

    def postproc(self, simulation_data):
        # self.postcmds.set_output(self.script_output)
        self.postcmds.run(simulation_data)
        plt.show()

    def _next_unnamed_run(self):
        run_label = "run{}".format(self.unnamed_run_cnt)
        self.unnamed_run_cnt += 1
        return run_label

    def _next_unnamed_phase(self):
        phase_label = "phase{}".format(self.unnamed_phase_cnt)
        self.unnamed_phase_cnt += 1
        return phase_label


class PostCmds():
    def __init__(self):
        self.cmds = list()  # List of PostCmd objects

    def add(self, cmd):
        self.cmds.append(cmd)

    def run(self, simulation_data):
        for cmd in self.cmds:
            cmd.run(simulation_data)


# class PostCmd():
#     def __init__(self):
#         self.simulation_data = None

#     def set_simdata(self, script_output):
#         self.script_output = script_output


class PlotCmd():
    def __init__(self, cmd, expr, eval_prop, plot_prop):
        self.cmd = cmd
        self.expr = expr
        self.eval_prop = eval_prop
        self.plot_prop = plot_prop
        if 'linewidth' not in self.plot_prop:
            self.plot_prop['linewidth'] = 1

    def run(self, simulation_data):
        label_expr = beautify_expr_for_label(self.expr)
        if self.cmd == VPLOT:
            ydata = simulation_data.vwpn_eval('v', self.expr, self.eval_prop)
            legend_label = "v{}".format(label_expr)
        elif self.cmd == WPLOT:
            ydata = simulation_data.vwpn_eval('w', self.expr, self.eval_prop)
            legend_label = "w{}".format(label_expr)
        elif self.cmd == PPLOT:
            ydata = simulation_data.vwpn_eval('p', self.expr, self.eval_prop)
            legend_label = "p{}".format(label_expr)
        elif self.cmd == NPLOT:
            ydata = simulation_data.vwpn_eval('n', self.expr, self.eval_prop)
            legend_label = "n{}".format(label_expr)
        if self.eval_prop[EVAL_SUBJECT] == EVAL_ALL:
            for i, subject_ydata in enumerate(ydata):
                subject_legend_label = "{0}, subject {1}".format(legend_label, i)
                plt.plot(subject_ydata, label=subject_legend_label, **self.plot_prop)
        else:
            plt.plot(ydata, label=legend_label, **self.plot_prop)
        plt.grid(True)


def beautify_expr_for_label(expr0):
    expr = expr0[:]
    expr_type = type(expr)
    is_list = (expr_type is list)
    is_tuple = (expr_type is tuple)
    if is_list or is_tuple:
        expr = [e for e in expr if e is not None]
    else:
        return "('" + expr + "')"
    for i, e in enumerate(expr):
        if type(e) is tuple and len(e) == 1:
            expr[i] = e[0]
    if len(expr) == 1:
        return beautify_expr_for_label(expr[0])
    else:
        if is_tuple:
            return tuple(expr)
        else:
            return expr


class FigureCmd():
    def __init__(self, title, mpl_prop):
        self.title = title
        self.mpl_prop = mpl_prop

    def run(self, simulation_data):
        f = plt.figure(**self.mpl_prop)
        if self.title is not None:
            f.suptitle(self.title)  # Figure title


class SubplotCmd():
    def __init__(self, spec, mpl_prop):
        self.spec = spec  # Subplot specification, e.g. 211 or (2,1,1)
        self.mpl_prop = mpl_prop

    def run(self, simulation_data):
        plt.subplot(self.spec, **self.mpl_prop)


class LegendCmd():
    def __init__(self, labels, mpl_prop):
        self.labels = labels
        self.mpl_prop = mpl_prop

    def run(self, simulation_data):
        if self.labels is not None:
            plt.legend(self.labels, **self.mpl_prop)
        else:
            plt.legend(**self.mpl_prop)


class ScriptBlock():
    def __init__(self, keyword, pvdict, content):
        self.keyword = keyword
        self.pvdict = pvdict
        self.content = content


class Comment():
    def __init__(self):
        self.comment = ""

    def add(self, newblock):
        # newblock is a ScriptBlock object
        self.comment += newblock.content


class Parameters():
    def __init__(self):
        self.parameters = dict()

    def get(self, parameter_name):
        if parameter_name not in self.parameters:
            errmsg = "The parameter '{0}' is not set in {1}".format(parameter_name, PARAMETERS)
            raise Exception(errmsg)
        return self.parameters[parameter_name]

    def add(self, newblock):
        try:
            newdict = ast.literal_eval(newblock.content)
        except Exception:
            raise LsParseException(PARAMETERS + " must be a valid Python dictionary.")
        self.parameters.update(newdict)

    def make_mechanism_obj(self):
        if MECHANISM not in self.parameters:
            raise LsParseException("The parameter {0} is required.".format(MECHANISM))
        mechanism_name = self.parameters[MECHANISM].lower()
        if mechanism_name == RESCORLA_WAGNER:
            mechanism_obj = LsMechanism.RescorlaWagner(**self.parameters)
        elif mechanism_name == Q_LEARNING:
            mechanism_obj = LsMechanism.Qlearning(**self.parameters)
        elif mechanism_name == SARSA:
            mechanism_obj = LsMechanism.SARSA(**self.parameters)
        elif mechanism_name == ACTOR_CRITIC:
            mechanism_obj = LsMechanism.ActorCritic(**self.parameters)
        elif mechanism_name == ENQUIST:
            mechanism_obj = LsMechanism.Enquist(**self.parameters)
        else:
            raise Exception('Unknown mechanism "' + mechanism_name + '".')
        return mechanism_obj


class Phases():
    def __init__(self):
        # A 2-tuple. Index 0 is phase labels, index 1 is corresponding Phase objects, index 2
        # is PhaseWorld objects
        self.phases = (list(), list(), list())

    def add(self, newblock, parameters):
        label = newblock.pvdict[LABEL]
        rows = newblock.content.splitlines()
        if label in self.phases[0]:
            ind = self.phases[0].index(label)
            self.phases[1][ind].add_rows(rows)
            self.phases[1][ind].pvdict.update(newblock.pvdict)
            self.phases[2][ind] = self.phases[1][ind].make_world(parameters)
        else:
            self.phases[0].append(label)
            phase_obj = Phase(newblock.pvdict, rows)
            self.phases[1].append(phase_obj)
            self.phases[2].append(phase_obj.make_world(parameters))

    def make_world(self, phases_to_use):
        if len(phases_to_use) == 0:  # Empty tuple means all phases
            phases_to_use = self.phases[0]  # list(self.phases.keys())
        phase_worlds = list()
        for lbl in phases_to_use:
            if lbl not in self.phases[0]:
                raise Exception("Invalid phase label '{}'.".format(lbl))
            ind = self.phases[0].index(lbl)
            phase_obj = self.phases[2][ind]
            phase_worlds.append(phase_obj)
        return LsWorld.World(phase_worlds)


class Phase():
    '''A number or rows of text and a parameters dict.'''

    def __init__(self, pvdict, rows):
        self.pvdict = pvdict  # dict()
        self.rows = rows  # list()

    '''Adds the specified list of rows to self.rows.'''
    def add_rows(self, rows):
        self.rows.extend(rows)

    def make_world(self, parameters):
        return LsWorld.PhaseWorld(self.rows, self.pvdict,
                                  parameters.get(STIMULUS_ELEMENTS),
                                  parameters.get(BEHAVIORS))


class Runs():
    def __init__(self):
        # A dict with ScriptRun objects. Keys are run labels.
        self.runs = dict()

    def add(self, label, world, mechanism_obj, n_subjects):
        if label in self.runs:
            raise LsParseException("Run label " + label + " is duplicated.")
        self.runs[label] = ScriptRun(label, world, mechanism_obj, n_subjects)

    def run(self):
        out = dict()
        for label, run in self.runs.items():
            out[label] = run.run()
        return ScriptOutput(out)


# ---------------------- Static methods ----------------------

def clean_script(script):
    # Replace each tab with a space
    script = script.replace("\t", " ")

    # Strip leading and trailing spaces
    lines = script.splitlines()
    lines = [line.strip() for line in lines]

    for i in range(1, len(lines)):
        lines[i] = lines[i].split('#')[0].strip()  # Remove comments
    lines = list(filter(None, lines))  # Remove empty lines
    return '\n'.join(lines)


def parse_block(block):
    first_row, content = LsUtil.split1_strip(block, '\n')
    keyword, pvstr = LsUtil.split1_strip(first_row)
    pvdict = dict()
    if pvstr is not None:
        try:
            pvdict = ast.literal_eval(pvstr)
            if type(pvdict) is not dict:
                raise LsParseException("Expected a dictionary. Got\n'" + pvstr + "'.")
        except Exception:
            raise LsParseException("Expected a dictionary. Got\n'" + pvstr + "'.")
    return ScriptBlock(keyword, pvdict, content)


def parse_postcmd(cmd, cmdarg, simulation_parameters):
    if cmdarg is not None:
        args = LsUtil.parse_sso(cmdarg)
        if args is None:  # Parse failed
            raise LsParseException("Invalid argument list to {}".format(cmd))
        nargs = len(args)
    else:
        args = list()  # Empty list
        nargs = 0

    if cmd == FIGURE:
        if nargs > 2:
            raise LsParseException("The number of arguments to {} must be <= 2.".format(cmd))
        title = None
        mpl_prop = dict()
        if nargs == 2:
            title = args[0]
            mpl_prop = args[1]
        elif nargs == 1:
            either = args[0]
            if type(either) is str:
                title = either
            elif type(either) is dict:
                mpl_prop = either
            else:
                raise LsParseException("Arguments to {} must be string and/or dict.".format(cmd))

        if title is not None:
            if type(title) != str:
                raise LsParseException("Title argument to {} must be a string.".format(cmd))
        if type(mpl_prop) != dict:
            raise LsParseException("Figure properties argument to {} must be a dict.".format(cmd))
        return FigureCmd(title, mpl_prop)

    elif cmd == SUBPLOT:
        if nargs > 2 or nargs == 0:
            raise LsParseException("The number of arguments to {} must be 1 or 2.".format(cmd))
        spec = args[0]
        errmsg = "First argument (subplot specification) to {} must be a tuple or three-positive-digits integer.".format(cmd)
        parse_subplotspec(spec, errmsg)
        mpl_prop = dict()
        if nargs == 2:
            mpl_prop = args[1]
            if type(mpl_prop) is not dict:
                raise LsParseException("Second argument to {} must be a dictionary.".format(cmd))
        return SubplotCmd(spec, mpl_prop)

    elif cmd == LEGEND:
        if nargs > 2:
            raise LsParseException("The number of arguments to {} must be <=2.".format(cmd))
        labels = None
        mpl_prop = dict()
        if nargs == 2:
            labels = args[0]
            mpl_prop = args[1]
        elif nargs == 1:
            either = args[0]
            if (type(either) is tuple) or (type(either) is str):
                labels = either
            elif type(either) is dict:
                mpl_prop = either
            else:
                raise LsParseException("Arguments to {} must be tuple, string or dict.".format(cmd))
        if labels is not None:
            if type(labels) is str:
                labels = (labels,)
            if type(labels) is not tuple:
                raise LsParseException("Legend labels must be a tuple ('label1','label2',...) or a string.".format(cmd))
        if type(mpl_prop) is not dict:
            raise LsParseException("Second argument to {} must be a dictionary.".format(cmd))
        return LegendCmd(labels, mpl_prop)

    elif cmd == PPLOT:
        expr = args[0]
        if type(expr) is not tuple:
            raise LsParseException("First argument to {} must be a tuple.".format(cmd))
        if type(expr[0]) is not tuple:
            listexpr = list(expr)
            listexpr[0] = (listexpr[0],)
            expr = tuple(listexpr)
        beta = simulation_parameters.get(BETA)
        eval_prop = {BETA: beta}
        if nargs >= 2:
            eval_prop.update(args[1])
            # eval_prop = args[1]
        plot_prop = dict()
        if nargs >= 3:
            plot_prop = args[2]
        return PlotCmd(cmd, expr, eval_prop, plot_prop)

    elif cmd == NPLOT:
        if (nargs == 0) or (nargs > 4):
            raise LsParseException("The number of arguments to {} must be 1, 2, 3 or 4.".
                                   format(cmd))
        seq = args[0]
        seqref = None
        eval_prop = dict()
        plot_prop = dict()
        if nargs >= 2:
            if (type(args[1]) is str) or (type(args[1]) is tuple) or (type(args[1]) is list):
                seqref = args[1]
            elif type(args[1]) is dict:
                eval_prop = args[1]
            else:
                raise LsParseException("Invalid second argument to {}.".format(cmd))
        if nargs >= 3:
            if seqref is None:
                plot_prop = args[2]
            else:
                eval_prop = args[2]
        if nargs == 4:
            plot_prop = args[3]

        return PlotCmd(cmd, (seq, seqref), eval_prop, plot_prop)

    else:  # vplot or wplot
        expr = args[0]
        eval_prop = dict()
        if nargs >= 2:
            eval_prop = args[1]
        plot_prop = dict()
        if nargs >= 3:
            plot_prop = args[2]
        return PlotCmd(cmd, expr, eval_prop, plot_prop)


def parse_subplotspec(spec, errmsg):
    if type(spec) is tuple:
        if len(spec) != 3:
            raise LsParseException(errmsg)
        for i in spec:
            if type(spec[i]) != int:
                raise LsParseException(errmsg)
            if spec[i] <= 0:
                raise LsParseException(errmsg)
    elif type(spec) is int:
        if spec <= 0:
            raise LsParseException(errmsg)
        strspec = str(spec)
        if len(strspec) != 3:
            raise LsParseException(errmsg)
        if '0' in strspec:
            raise LsParseException(errmsg)
    else:
        raise LsParseException(errmsg)
