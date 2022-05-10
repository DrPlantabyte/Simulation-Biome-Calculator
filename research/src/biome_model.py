from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.multioutput import MultiOutputClassifier
import numpy
from numpy import ndarray

from biome_enum import Biome

class BiomeClassifier(BaseEstimator, ClassifierMixin):

	def __init__(self):
		pass

	def fit(self, X: ndarray, y=None):
		# X : array-like of shape (n_samples, n_features) for input sample data
		# y : array-like of shape (n_samples,) or (n_samples, n_outputs) for supervised learning with target output
		pass

	def predict(self, X: ndarray, y=None):
		# X : array-like of shape (n_samples, n_features) for input sample data
		# y : not used (required for API compatibility
		# return : ndarray of shape (n_samples,)
		pass

	def predict_proba(self, X: ndarray, y=None):
		# X : array-like of shape (n_samples, n_features) for input sample data
		# y : not used (required for API compatibility
		# return : array of shape (n_samples, n_classes), or a list of n_outputs such arrays if n_outputs > 1.
		#             The class probabilities of the input samples.

		pass
