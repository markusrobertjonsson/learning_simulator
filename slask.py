import LsScript


def slask():
        script = '''
        @parameters
        {
        'mechanism' :         'Rescorla_Wagner',
        'behaviors' :         ['R','RR'],
        'stimulus_elements' : ['E1','rew1','E2','rew2'],
        'u'                 : {'rew1':1, 'rew2':1, 'E1':0, 'E2':0}
        }

        @phase {'label':'phase1', 'end':'B=3'}
        A 'E1'   | 5:B | A
        B 'rew1' | A

        @phase {'label':'phase2', 'end':'B=6'}
        A 'E2'   | 5:B | A
        B 'rew2' | A

        @run

        # @nplot 'E' {'cumulative':'off', 'steps':'rew'}

        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        #return simulation_data.run_outputs["run1"].output_subjects[0]
        return simulation_data


def slask2():
    script = '''
    @parameters
    {
    'subjects'          : 1, # number of individuals
    'mechanism'         : 'Enquist',
    'behaviors'         : ['R','R0'],
    'stimulus_elements' : ['context','reward','us','cs','lever'],
    'start_v'           : {'default':0},
    'start_w'           : {'default':0},
    'alpha_v'           : 0.1,
    'alpha_w'           : 0.1,
    'beta'              : 1,
    'behavior_cost'     : {'R':0.1,'default':0},
    'u'                 : {'reward':10, 'default': 0},
    'omit_stimulus'     : []
    }

    # ------------- CLASSICAL CONDITIONING -------------
    @phase {'label':'pretraining', 'end':'us=150'}
    CONTEXT context            | 25:US       | CONTEXT
    US      ('us','context')     | R: REWARD | CONTEXT
    REWARD  ('reward','context') | CONTEXT

    @phase {'label':'conditioning', 'end':'cs=50'}
    CONTEXT 'context'            | 25:CS |       CONTEXT
    CS      ('cs','context')     | 2:US  | CS
    US      ('us','context')     | R: REWARD | CONTEXT
    REWARD  ('reward','context') | CONTEXT

    @phase {'label':'test', 'end':'CS=25'}
    CONTEXT 'context'        | 25:CS | CONTEXT
    REWARD  ('cs','context')  | CONTEXT

    @run {'phases':('pretraining')}

    @figure
    @nplot (['context','R']) {'seqref':'context', 'steps':'us','cumulative':'off'}

    @figure
    @pplot ('cs','R') {'steps':'us'}
    '''

    script_obj = LsScript.LsScript(script)
    simulation_data = script_obj.run()
    script_obj.postproc(simulation_data)
    return simulation_data
