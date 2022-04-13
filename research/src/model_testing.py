import os, shutil, sys, re, requests, base64, urllib.parse, numpy, pandas, json, pickle, ssl, time, gzip
from os import path
from numpy import ndarray, nan, uint8, float32, logical_and, logical_or, clip, sin, cos
from pandas import DataFrame
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import *
from sklearn.metrics import classification_report
from sklearn.tree import DecisionTreeClassifier, export_text, export_graphviz
from matplotlib import pyplot
from biome_enum import Biome

def main():
	RELOAD = False
	data_dir = 'data'
	data_sets_zpickles = [path.join(data_dir, 'Earth_biome_DataFrame-%s.pickle.gz' % n) for n in range(0,4)]
	# data splitting: 3 training batches and 1 test batch
	src_data: DataFrame = zunpickle(data_sets_zpickles[0])
	dev_data = src_data[src_data['biome'] != 0][::10] # remove unclassified rows and reduce data size
	labels = dev_data['biome']
	features = dev_data.drop('biome', axis=1, inplace=False)
	dtree_zpickle = path.join(data_dir, 'dtree-model.pickle.gz')
	dtree_size = 32
	if RELOAD or not path.exists(dtree_zpickle):
		pipe = Pipeline([
			('normalize', MinMaxScaler()),
			('decision_tree', DecisionTreeClassifier(max_depth=dtree_size))
		])
		print('fitting decision tree model...')
		pipe.fit(X=features, y=labels)
		zpickle(pipe, dtree_zpickle)
	else:
		pipe = zunpickle(dtree_zpickle)
	print(classification_report(y_true=labels, y_pred=pipe.predict(features)))
	print('Overall accuracy: %s %%' % (100 * pipe.score(X=features, y=labels)))
	print(type(pipe['decision_tree']))
	#print(export_text(pipe['decision_tree'], max_depth=dtree_size))
	export_graphviz(
		pipe['decision_tree'], out_file='dtree.dot', feature_names=features.columns,
		class_names=None, rounded=True, filled=True
	)
	#
	print('...Done!')

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

##########
if __name__ == '__main__':
	main()