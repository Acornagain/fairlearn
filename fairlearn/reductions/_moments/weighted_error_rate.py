# Copyright (c) Microsoft Corporation and contributors.
# Licensed under the MIT License.

import pandas as pd
from .moment import ClassificationMoment, _ALL, _LABEL
_WEIGHTS = "weights"


class WeightedErrorRate(ClassificationMoment):
    r"""Weighted Loss error.

    Parameters
    ----------
    loss : {SquareLoss, AbsoluteLoss}
        A loss object with an `eval` method, e.g. `SquareLoss` or
        `AbsoluteLoss`.
    """

    short_name = "Weighted Error Rate"

    def __init__(self):
        super(WeightedErrorRate, self).__init__()

    # We need to augment data here. Hence to avoid unnecessary calculation, 
    # in this function, we use augmented data that have been calculated 
    # in the function load_data in cdf_demographic_parity_moment.py
    # that is, X and y. And meanwhile, we choose to directly return 
    # in the following function load_data to adapt to the call 
    # self.obj.load_data(X, y, sensitive_features=sensitive_features)
    # in the file _lagrangian.py
    def load_augmented_data(self, X, y, **kwargs):
        # Load the specified data into the object
        super().load_data(X, y, **kwargs)
        self.index = [_ALL]
        self.n = y.shape[0]
        if _WEIGHTS in kwargs:
            self.weights = kwargs[_WEIGHTS]
            self.weights = self.n * self.weights / self.weights.sum()
        else:
            self.weights = 1
        self.tags[_WEIGHTS] = self.weights

    def load_data(self, X, y, **kwargs):
        return

    def gamma(self, predictor):
        def h(X):
            return 1* (predictor(X.drop(['theta'], axis=1)) - X['theta'] >= 0)
        # Return the gamma values for the given predictor
        pred = h(self.X)
        error = pd.Series(data=(self.tags[_WEIGHTS]*(self.tags[_LABEL] - pred).abs()).mean(),
                          index=self.index)
        self._gamma_descr = str(error)
        return error

    def project_lambda(self, lambda_vec):
        """Return the lambda values."""
        return lambda_vec

    def signed_weights(self, lambda_vec=None):
        """Return the signed weights."""
        if lambda_vec is None:
            return self.tags[_WEIGHTS] * (2 * self.tags[_LABEL] - 1)
        else:
            return lambda_vec[_ALL] * self.tags[_WEIGHTS] * (2 * self.tags[_LABEL] - 1)
