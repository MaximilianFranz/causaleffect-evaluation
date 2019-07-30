import numpy as np
import pandas as pd
from scipy import stats


from causaleval import config
from causaleval.data.data_provider import DataProvider

class TwinsDataProvider(DataProvider):
    """
    The Twin dataset provider

    The data itself is not a treatment study, but rather an observation of the mortality rates of twins.
    We synthetically create a 'control'/'treatment' as being the younger / older twin, respectively.
    """

    def __init__(self):
        super().__init__()
        self.x = None
        self.t = None
        self.y = None
        self.y_cf = None

    def load_training_data(self):
        path = config.TWINS_PATH
        x_df = pd.read_csv(path + '/twinX.csv')
        t_df = pd.read_csv(path + '/twinT.csv')
        y_df = pd.read_csv(path + '/twinY.csv')

        df = x_df.drop(['id', 'Unnamed'], axis=1)
        df = pd.concat([df, t_df[['dbirwt_0', 'dbirwt_1']]], axis=1)
        df = pd.concat([df, y_df[['mort_0', 'mort_1']]], axis=1)
        df = df.dropna()
        df = df[df['dbirwt_0'] < 2000]
        df_norm = ((df - df.min())) / (df.max() - df.min())
        w = np.random.uniform(-0.1, 0.1, df.shape[1])
        weighted = np.dot(df_norm.values, w)
        n = np.random.normal(0, 0.1, df.shape[0])
        ps = weighted + n
        sigmoid = (1/(1+np.exp(-ps)))
        treatment = np.random.binomial(1, sigmoid)
        potential_outcomes = df[['mort_0', 'mort_1']].values
        observed = []
        counterfactual = []
        i = 0
        for t in treatment:
            observed.append(potential_outcomes[i, t])
            counterfactual.append(potential_outcomes[i, (1-t)])
            i += 1

        df['observed'] = observed
        self.data = df

        self.x = df.drop(['mort_0', 'mort_1', 'dbirwt_0', 'dbirwt_1'], axis=1).values
        self.t = treatment
        self.y = np.array(observed)
        self.y_cf = np.array(counterfactual)
        self.ite = df['mort_1'].values - df['mort_0'].values


    def get_training_data(self):
        if self.x is None:
            self.load_training_data()
        return self.x, self.t, self.y

    def get_true_ite(self, data=None):
        if self.ite is None:
            self.load_training_data()
        return self.ite

    def get_true_ate(self, subset=None):
        num = self.data.shape[0]
        return (self.data['mort_1'].sum()/num) - self.data['mort_0'].sum()/num

