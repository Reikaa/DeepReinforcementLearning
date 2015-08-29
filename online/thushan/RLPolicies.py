__author__ = 'Thushan Ganegedara'

from enum import IntEnum
from collections import defaultdict
from sklearn.gaussian_process import GaussianProcess
import numpy as np
import json

class Controller(object):

    def move(self, i, data, funcs):
        pass

    def end(self):
        return []


class ContinuousState(Controller):

    __slots__ = ['learning_rate', 'discount_rate', 'prev_state', 'prev_action', 'q', 'start_time', 'action_log']

    class Action(IntEnum):
        pool = 1
        reduce = 2
        increment = 3

        def __repr__(self):
            return str(self)

    def __init__(self, learning_rate=0.5, discount_rate=0.9, time_limit=1):
        self.learning_rate = learning_rate
        self.discount_rate = discount_rate

        self.prev_state = None
        self.prev_action = None
        self.prev_time = 0

        self.q = defaultdict(dict)
        self.time_limit = time_limit

    def move(self, i, data, funcs):

        #if we haven't completed 30 iterations, keep pooling
        if i <=30:
            funcs['pool'](1)
            return

        #what does this method do?
        def ma_state(name):
            retVal = 0
            if not len(data[name]) < 2:
                retVal = data[name][-1] - data[name][-2]

            return retVal
            #return 0 if len(data[name]) < 2 else data[name][-1] - data[name][-2]

        state = (data['r_15'][-1], data['neuron_balance'], ma_state('mea_5'), ma_state('mea_15'), ma_state('mea_30'))
        print('current state %d, %f, %f, %f, %f' % (data['r_15'][-1], data['neuron_balance'], ma_state('mea_5'), ma_state('mea_15'), ma_state('mea_30')))

        ''' gps = {}

        for a, value_dict in self.q.items():
            if len(value_dict) < 2:
                continue

            x, y = zip(*value_dict.items())

            gp = GaussianProcess(theta0=0.1, thetaL=0.001, thetaU==1, nugget=0.1)
            gp.fit(np.array(x), np.array(y))
            gps[a] = gp'''

        if self.prev_action or self.prev_action:

            reward = - data['error_log'][-1]

            neuron_penalty = 0

            if data['neuron_balance'] > 2 or data['neuron_balance'] < 1:
                neuron_penalty = 2 * abs(1 - data['neuron_balance'])

            reward -= neuron_penalty

            sample = reward

            if self.prev_state in self.q[self.prev_action]:
                self.q[self.prev_action][self.prev_state] = (1 - self.learning_rate) * self.q[self.prev_action][self.prev_state] + self.learning_rate * sample
            else:
                self.q[self.prev_action][self.prev_state] = sample

        action = list(self.Action)[i % len(self.Action)]

        to_move = (data['initial_size'] * 0.1) / (data['initial_size'] * data['neuron_balance'])
        if action == self.Action.pool:
            funcs['pool'](1)
        elif action == self.Action.reduce:
            funcs['merge_increment_pool'](data['pool_relevant'], to_move, 0)
        elif action == self.Action.increment:
            funcs['merge_increment_pool'](data['pool_relevant'], 0, to_move)

        actionStr = ''
        if action == 1: actionStr = 'Pool'
        elif action == 2: actionStr = 'Reduce'
        elif action == 3: actionStr = 'Increment'

        print('action taken: ', actionStr)

        self.prev_action = action
        self.prev_state = state

    def end(self):
        return [{'name': 'q_state.json', 'json': json.dumps({str(k):{str(tup): value for tup, value in v.items()} for k,v in self.q.items()})}]