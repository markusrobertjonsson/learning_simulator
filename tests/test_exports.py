# import matplotlib.pyplot as plt

import unittest
import LsScript


class TestPlots(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_singlesubject(self):
        script='''@parameters
        {
        'subjects'          : 1,
        'mechanism'         : 'GA',
        'behaviors'         : ['R0','R1','R2'],
        'stimulus_elements' : ['S1','S2','reward','reward2','new trial'],
        'start_v'           : {'default':-1},
        'alpha_v'           : 0.1,
        'alpha_w'           : 0.1,
        'beta'              : 1,
        'behavior_cost'     : {'R1':1, 'R2':1, 'default':0},
        'u'                 : {'reward':10, 'default': 0},
        'omit_learning'     : ['new trial']
        }

        ## ------------- SEQUENCE LEARNING -------------
        @phase {'label':'chaining', 'end': 'reward=25'}
        NEW_TRIAL   'new trial'     | STIMULUS_1    
        STIMULUS_1  'S1'              | R1: STIMULUS_2     | NEW_TRIAL 
        STIMULUS_2  'S2'              | R2: REWARD         | NEW_TRIAL
        REWARD     reward      | NEW_TRIAL  

        @phase {'label':'test_A', 'end': 'S1=100'}
        NEW_TRIAL    'new trial'       | STIMULUS_1 
        STIMULUS_1  'S1'           | REWARD
        REWARD     'reward2'        | NEW_TRIAL 

        @phase {'label':'test_B', 'end': 'S1=100'}
        NEW_TRIAL   'new trial'   | STIMULUS_1  
        STIMULUS_1  'S1'              | R1: STIMULUS_2     | NEW_TRIAL
        STIMULUS_2  'S2'              | NEW_TRIAL   

        @run {'phases':('chaining','test_B')}

        @wexport 'S1' {'filename':'test_wexport1.csv'}
        @wexport 'S2' {'filename':'test_wexport2.csv'}

        @pexport (('S1','S2'), 'R1') {'filename':'test_pexport1.csv'}
        @pexport ('S1', 'R0') {'filename':'test_pexport2.csv'}

        @vexport ('S1', 'R1') {'filename':'test_vexport1.csv'}
        @vexport ('S1', 'R0') {'filename':'test_vexport2.csv'}

        @nexport 'reward' {'cumulative':'on', 'filename':'test_nexport1.csv'}
        @nexport 'S1' {'cumulative':'on', 'filename':'test_nexport2.csv'}
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        script_obj.postproc(simulation_data, False)

        # self.subject_output = simulation_data.run_outputs["run1"].output_subjects[0]


    def test_multisubject(self):
        script='''@parameters
        {
        'subjects'          : 10,
        'mechanism'         : 'GA',
        'behaviors'         : ['R0','R1','R2'],
        'stimulus_elements' : ['S1','S2','reward','reward2','new trial'],
        'start_v'           : {'default':-1},
        'alpha_v'           : 0.1,
        'alpha_w'           : 0.1,
        'beta'              : 1,
        'behavior_cost'     : {'R1':1, 'R2':1, 'default':0},
        'u'                 : {'reward':10, 'default': 0},
        'omit_learning'     : ['new trial']
        }

        ## ------------- SEQUENCE LEARNING -------------
        @phase {'label':'chaining', 'end': 'reward=25'}
        NEW_TRIAL   'new trial'     | STIMULUS_1    
        STIMULUS_1  'S1'              | R1: STIMULUS_2     | NEW_TRIAL 
        STIMULUS_2  'S2'              | R2: REWARD         | NEW_TRIAL
        REWARD     reward      | NEW_TRIAL  

        @phase {'label':'test_A', 'end': 'S1=100'}
        NEW_TRIAL    'new trial'       | STIMULUS_1 
        STIMULUS_1  'S1'           | REWARD
        REWARD     'reward2'        | NEW_TRIAL 

        @phase {'label':'test_B', 'end': 'S1=100'}
        NEW_TRIAL   'new trial'   | STIMULUS_1  
        STIMULUS_1  'S1'              | R1: STIMULUS_2     | NEW_TRIAL
        STIMULUS_2  'S2'              | NEW_TRIAL   

        @run {'phases':('chaining','test_B')}

        @wexport 'S1' {'subject':'all', 'filename':'test_wexportMS1.csv'}
        @wexport 'S2' {'filename':'test_wexportMS2.csv'}

        @pexport (('S1','S2'), 'R1') {'filename':'test_pexportMS1.csv'}
        @pexport ('S1', 'R0') {'filename':'test_pexportMS2.csv'}

        @vexport ('S1', 'R1') {'filename':'test_vexportMS1.csv'}
        @vexport ('S1', 'R0') {'filename':'test_vexportMS2.csv'}

        @nexport 'reward' {'cumulative':'on', 'filename':'test_nexportMS1.csv'}
        @nexport 'S1' {'cumulative':'on', 'filename':'test_nexportMS2.csv'}
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        script_obj.postproc(simulation_data, False)

        # self.subject_output = simulation_data.run_outputs["run1"].output_subjects[0]
