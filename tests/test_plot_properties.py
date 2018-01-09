import matplotlib.pyplot as plt

import unittest
import LsScript
from LsExceptions import LsEvalException

# import time
# time.sleep(40)


class TestPlotProperties(unittest.TestCase):

    def setUp(self):
        self.base_script = """
            @parameters
            {
            'subjects'          : 10, # number of individuals
            'mechanism'         : 'ga',
            'behaviors'         : ['response','no_response'],
            'stimulus_elements' : ['new_trail', 'context', 'us', 'cs', 'reward'],
            'start_v'           : {'default':-1},
            'start_w'           : {'default':0},
            'alpha_v'           : 0.1,
            'alpha_w'           : 0.1,
            'beta'              : 1.5,
            'behavior_cost'     : {'response':4,'default':0},
            'u'                 : {'reward':10, 'default': 0},
            'omit_learning'     : ['new_trail']
            }

            @phase {'label':'pretraining', 'end':'us=10'}
            NEW_TRIAL   'new_trail'               | CONTEXT
            CONTEXT     'context'                 | 5:SHOW_US            | CONTEXT
            SHOW_US     ('us','context')          | 'response': REWARD   | NEW_TRIAL
            REWARD      ('reward','context')      | NEW_TRIAL

            @phase {'label':'conditioning', 'end':'cs=10'}
            NEW_TRIAL   'new_trail'               | 1:CONTEXT            | NEW_TRIAL
            CONTEXT     'context'                 | 5:SHOW_CS            | CONTEXT
            SHOW_CS     ('cs','context')          | 1:SHOW_US            | SHOW_CS
            SHOW_US     ('us','context')          | response: REWARD     | NEW_TRIAL
            REWARD      ('reward','context')      | NEW_TRIAL
        """

    def tearDown(self):
        # pass
        plt.close('all')

    def get_plotdata(self, fig_num):
        ax = plt.figure(fig_num).axes
        self.assertEqual(len(ax), 1)
        lines = ax[0].get_lines()
        self.assertEqual(len(lines), 1)
        x = lines[0].get_xdata(True)
        y = lines[0].get_ydata(True)
        return list(x), list(y)

    # @staticmethod
    def run_script(self, script):
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        script_obj.postproc(simulation_data, False)
        plt.show(block=False)

    def test_invalid_runlabel(self):
        script = self.base_script + '''
            @run {'label':'pretraining_only', 'phases':'pretraining'}
            @run {'label':'conditioning_only', 'phases':'conditioning'}
            @run {'label':'both', 'phases':('pretraining','conditioning')}

            @figure
            @wplot 'us' {'runlabel':'pretraining'}  # Should be 'pretraining_only'
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        with self.assertRaises(LsEvalException):
            script_obj.postproc(simulation_data, False)
        plt.show(block=False)

    def test_runlabel(self):
        script = self.base_script + '''
            @run {'label':'pretraining_only', 'phases':'pretraining'}
            @run {'label':'conditioning_only', 'phases':'conditioning'}
            @run {'label':'both', 'phases':('pretraining','conditioning')}

            @figure
            @pplot ('us','response') {'runlabel':'pretraining_only'}
            @figure
            @pplot ('us','response') {'runlabel':'conditioning_only'}
            @figure
            @pplot ('us','response') {'runlabel':'both'}

            @figure
            @vplot ('cs','response') {'runlabel':'pretraining_only'}
            @figure
            @vplot ('cs','response') {'runlabel':'conditioning_only'}
            @figure
            @vplot ('cs','response') {'runlabel':'both'}

            @figure
            @wplot 'context' {'runlabel':'pretraining_only'}
            @figure
            @wplot 'context' {'runlabel':'conditioning_only'}
            @figure
            @wplot 'context' {'runlabel':'both'}

            @figure
            @nplot 'cs' {'runlabel':'pretraining_only', 'cumulative':'on'}
            @figure
            @nplot 'cs' {'runlabel':'conditioning_only', 'cumulative':'on'}
            @figure
            @nplot 'cs' {'runlabel':'both', 'cumulative':'on'}

            @figure
            @nplot 'us' {'runlabel':'pretraining_only', 'cumulative':'on'}
            @figure
            @nplot 'us' {'runlabel':'conditioning_only', 'cumulative':'on'}
            @figure
            @nplot 'us' {'runlabel':'both', 'cumulative':'on'}
        '''
        self.run_script(script)

        # pplot
        x1, y1 = self.get_plotdata(1)
        x2, y2 = self.get_plotdata(2)
        x3, y3 = self.get_plotdata(3)
        self.assertTrue(len(x1) < len(x3))
        self.assertTrue(len(x2) < len(x3))

        # vplot
        x1, y1 = self.get_plotdata(4)
        x2, y2 = self.get_plotdata(5)
        x3, y3 = self.get_plotdata(6)
        self.assertTrue(len(x1) < len(x3))
        self.assertTrue(len(x2) < len(x3))

        self.assertEqual(x1[0], 0)
        for pt in y1:
            self.assertEqual(pt, -1)

        self.assertEqual(x2[0], 0)
        self.assertEqual(y2[0], -1)

        self.assertEqual(x3[0], 0)
        self.assertEqual(y3[0], -1)

        # wplot
        x1, y1 = self.get_plotdata(7)
        x2, y2 = self.get_plotdata(8)
        x3, y3 = self.get_plotdata(9)
        self.assertTrue(len(x1) < len(x3))
        self.assertTrue(len(x2) < len(x3))
        self.assertEqual(x1[0], 0)
        self.assertEqual(x2[0], 0)
        self.assertEqual(x3[0], 0)
        self.assertEqual(y1[0], 0)
        self.assertEqual(y2[0], 0)
        self.assertEqual(y3[0], 0)

        # nplot cs
        x1, y1 = self.get_plotdata(10)
        x2, y2 = self.get_plotdata(11)
        x3, y3 = self.get_plotdata(12)

        self.assertTrue(len(x1) < len(x3))
        self.assertTrue(len(x2) < len(x3))

        self.assertEqual(y1[-1], 0)
        self.assertEqual(y2[-1], 10)
        self.assertEqual(y3[-1], 10)

        # nplot us
        x1, y1 = self.get_plotdata(13)
        x2, y2 = self.get_plotdata(14)
        x3, y3 = self.get_plotdata(15)

        self.assertTrue(len(x1) < len(x3))
        self.assertTrue(len(x2) < len(x3))

        self.assertEqual(y1[-1], 10)
        self.assertEqual(y2[-1], 9)
        self.assertEqual(y3[-1], 19)

    def test_invalid_subject1(self):
        script = self.base_script + '''
            @run {'label':'both', 'phases':('pretraining','conditioning')}

            @figure
            @pplot ('us','response') {'subject':'qwqw'}
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        with self.assertRaises(LsEvalException):
            script_obj.postproc(simulation_data, False)
        plt.show(block=False)

    def test_invalid_subject2(self):
        script = self.base_script + '''
            @run {'label':'both', 'phases':('pretraining','conditioning')}

            @figure
            @pplot ('us','response') {'subject':10}
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        with self.assertRaises(LsEvalException):
            script_obj.postproc(simulation_data, False)
        plt.show(block=False)

    def test_subject(self):
        script = self.base_script + '''
            @run {'label':'both', 'phases':('pretraining','conditioning')}

            @figure
            @pplot ('us','response') {'subject':0}
            @figure
            @pplot ('us','response') {'subject':9}
            @figure
            @pplot ('us','response') {'subject':'average'}
            @figure
            @pplot ('us','response') {'subject':'all'}
        '''
        self.run_script(script)
        x1, y1 = self.get_plotdata(1)
        x2, y2 = self.get_plotdata(2)
        self.assertTrue(x1[0] == x2[0])
        self.assertTrue(y1 != y2)

        x3, y3 = self.get_plotdata(3)
        self.assertTrue(x1[0] == x3[0])

        ax = plt.figure(4).axes
        self.assertEqual(len(ax), 1)
        lines = ax[0].get_lines()
        self.assertEqual(len(lines), 10)

    def test_steps(self):
        pass

    def test_exact_steps(self):
        pass

    def test_phase(self):
        pass
