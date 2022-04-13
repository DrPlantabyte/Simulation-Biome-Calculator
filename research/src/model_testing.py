import os, shutil, sys, re, requests, base64, urllib.parse, numpy, pandas, json, pickle, ssl, time, gzip
from os import path
from subprocess import call
from PIL import Image
from copy import deepcopy
from numpy import ndarray, nan, uint8, float32, logical_and, logical_or, clip, sin, cos
from pandas import DataFrame
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import *
from sklearn.metrics import classification_report, euclidean_distances
from sklearn.tree import DecisionTreeClassifier, export_text, export_graphviz
from sklearn.base import BaseEstimator, TransformerMixin, ClassifierMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from matplotlib import pyplot
from biome_enum import Biome

def main():
	# RELOAD = True
	data_dir = 'data'
	data_sets_zpickles = [path.join(data_dir, 'Earth_biome_DataFrame-%s.pickle.gz' % n) for n in range(0,4)]
	# data splitting: 3 training batches and 1 test batch
	src_data: DataFrame = zunpickle(data_sets_zpickles[0])
	# remove unclassified rows and reduce data size and remove oceans
	dev_data = src_data[numpy.logical_and(src_data['biome'] != 0, src_data['biome'] < 0x10)]
	print('columns: ', list(dev_data.columns))
	labels = dev_data['biome']
	features: DataFrame = dev_data.drop(['biome', 'gravity', 'solar_flux', 'pressure', 'altitude'], axis=1, inplace=False)
	print('features: ', list(features.columns))
	# dtree_zpickle = path.join(data_dir, 'dtree-model.pickle.gz')

	rp_pipe = Pipeline([
		('normalize', MinMaxScaler()),
		('my_classifier', ReferencePointClassifier())
	])
	print('reference point classifier...')
	fit_and_score(rp_pipe, input_data=features, labels=labels)

	# for dtree_size in range(2,10):
	dtree_size = 6
	# if RELOAD or not path.exists(dtree_zpickle):
	dtree_pipe = Pipeline([
		('normalize', MinMaxScaler()),
		('decision_tree', DecisionTreeClassifier(max_depth=dtree_size))
	])
	print('fitting decision tree model with %s layers...' % dtree_size)
	dtree_pipe.fit(X=features, y=labels)
		# zpickle(pipe, dtree_zpickle)
	# else:
		# pipe = zunpickle(dtree_zpickle)
	fit_and_score(dtree_pipe, input_data=features, labels=labels)

	#print(export_text(pipe['decision_tree'], max_depth=dtree_size))
	# graphviz_export(
	# 	pipe['decision_tree'], 'dtree', feature_names=features.columns,
	# 	class_names=[str(n) for n in pipe['decision_tree'].classes_]
	# )
	#
	print('...Done!')
def fit_and_score(pipe: Pipeline, input_data: DataFrame, labels: ndarray):
	## NOTE:
	## precision = fraction of positive predictions that were correct (true positives/(true+false positives))
	## recall = fraction that were correctly predicted for this class (true positives/(true pod.+false neg.)
	## f1-score = 2*(Recall * Precision) / (Recall + Precision)
	## support = total number of this class
	pipe.fit(X=input_data, y=labels)
	print(classification_report(y_true=labels, y_pred=pipe.predict(input_data)))
	percent_accuracy = 100 * pipe.score(X=input_data, y=labels)
	print('Overall accuracy: %s %%' % int(percent_accuracy))

class ReferencePointClassifier(BaseEstimator, TransformerMixin, ClassifierMixin):
	def __init__(self, num_pts):
		self.
		pass

	def fit(self, X, y):
		# Check that X and y have correct shape
		X: ndarray = numpy.asarray(X)
		y: ndarray = numpy.asarray(y)
		X, y = check_X_y(X, y)
		# Store the classes seen during fit
		self.classes_ = unique_labels(y)
		self.feature_count_ = len(X[0])
		# fitting operation
		self.ref_points = []
		for i in range(0, len(self.classes_)):
			L = self.classes_[i]
			self.ref_points.append(X.take(numpy.where(y == L), axis=0)[0].mean(axis=0).reshape((1,X.shape[1])))
		# Return the classifier
		return self

	def _rand_point(self, X, y):
		# A1 = self.ref_points[numpy.random.randint(len(self.classes_))]
		# p1 = A1[numpy.random.randint(A1.shape[0])]
		# A2 = self.ref_points[numpy.random.randint(len(self.classes_))]
		# p2 = A2[numpy.random.randint(A2.shape[0])]
		# p3 = 0.5 * (p1 + p2)
		p3 = numpy.random.rand(self.feature_count_)
		score = self.score(X, y)
		for i in range(0, len(self.classes_)):
			old = self.ref_points[i]
			temp = numpy.append(old, p3.reshape(1,self.feature_count_), axis=0)
			self.ref_points[i] = temp
			new_score = self.score(X, y)
			if new_score <= score:
				# not an improvement
				self.ref_points[i] = old
			else:
				# improvement
				score = new_score

	def predict(self, X):
		# Check is fit had been called
		check_is_fitted(self)

		# Input validation
		X = check_array(X)

		class_dists = numpy.zeros((len(self.classes_),len(X))) + numpy.inf
		for i in range(0, len(self.classes_)):
			class_dists[i] = euclidean_distances(X, self.ref_points[i]).min(axis=1)

		closest = numpy.argmin(class_dists, axis=0)
		return self.classes_[closest]

def zpickle(obj, filepath):
	print('Pickling %s with gzip compression...' % filepath)
	parent = path.dirname(path.abspath(filepath))
	if not path.isdir(parent):
		os.makedirs(parent, exist_ok=True)
	with gzip.open(filepath, 'wb') as zout:
		pickle.dump(obj, zout)

def zunpickle(filepath):
	print('Unpickling %s with gzip decompression...' % filepath)
	if path.exists(filepath):
		with gzip.open(filepath, 'rb') as zin:
			return pickle.load(zin)
	else:
		raise FileNotFoundError("File '%s' does not exist" % path.abspath(filepath))

def graphviz_export(dtc: DecisionTreeClassifier, name, feature_names, class_names=None):
	dot_file = '%s.dot' % name
	img_file = '%s.png' % name
	export_graphviz(dtc, out_file='dtree.dot', feature_names=feature_names,
		class_names=class_names, rounded=True, filled=True)
	call(['dot', '-Tpng', dot_file, '-o%s' % img_file])
	img = Image.open(img_file)
	img.show()

##########
if __name__ == '__main__':
	main()