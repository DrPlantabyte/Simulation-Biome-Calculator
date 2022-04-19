import os, shutil, sys, re, requests, base64, urllib.parse, numpy, pandas, json, pickle, ssl, time, gzip
from os import path
from subprocess import call
from PIL import Image
from copy import deepcopy

from imblearn.under_sampling import RandomUnderSampler
from numpy import ndarray, nan, uint8, float32, logical_and, logical_or, clip, sin, cos, square, sqrt, power, log10
from pandas import DataFrame
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import *
from sklearn.metrics import classification_report, euclidean_distances
from sklearn.tree import DecisionTreeClassifier, export_text, export_graphviz
from sklearn.base import BaseEstimator, TransformerMixin, ClassifierMixin
from sklearn.cluster import KMeans
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from matplotlib import pyplot
from biome_enum import Biome
from photophysiology import *
import hillclimb

def main():
	# RELOAD = True
	data_dir = 'data'
	data_sets_zpickles = [path.join(data_dir, 'Earth_biome_DataFrame-%s.pickle.gz' % n) for n in range(0,4)]
	# data splitting: 3 training batches and 1 test batch
	src_data: DataFrame = zunpickle(data_sets_zpickles[0])
	# remove unclassified rows
	src_data: DataFrame = src_data[src_data['biome'] != 0]
	# remove unclassified rows and reduce data size and remove oceans
	dev_data = src_data[src_data['biome'] < 0x10]
	print('columns: ', list(dev_data.columns))
	labels = dev_data['biome']
	features: DataFrame = dev_data.drop(['biome', 'gravity'], axis=1, inplace=False)
	print('features: ', list(features.columns))

	print('estimating GPP potential...')
	## see MOD17 product documentation - http://www.ntsg.umt.edu/project/modis/mod17.php and http://www.ntsg.umt.edu/project/modis/user-guides/mod17c61usersguidev11mar112021.pdf
	## see also
	dev_data = dev_data.assign(**{
		'rel_photosythesis': photosynthesis_score(
			mean_temp_C=dev_data['temperature_mean'], temp_variation_C=dev_data['temperature_range'],
			precip_mm=dev_data['precipitation'], solar_flux_Wpm2=dev_data['solar_flux'],
			pressure_kPa=dev_data['pressure']
		)
	})


	## lets take a peek at the data
	make_plots = False
	if make_plots:
		print('making plots...')
		classes = numpy.unique(labels)
		for feature in [str(c) for c in dev_data.columns if str(c) != 'biome']:
			print('plotting %s comparison...' % feature)
			pyplot.bar(
				[str(Biome(bcode)).replace('Biome.', '') for bcode in classes],
				[dev_data[feature][dev_data['biome'] == bcode].mean() for bcode in classes],
				yerr=[dev_data[feature][dev_data['biome'] == bcode].std() for bcode in classes]
			)
			pyplot.xticks(rotation=30, ha='right')
			pyplot.title(feature)
			pyplot.ylabel(feature)
			pyplot.tight_layout()
			pyplot.savefig('biome %s.png' % feature)
			#pyplot.show()
			pyplot.clf()
		for i in range(0, len(classes)):
			bcode = classes[i]
			hexplot_y_vs_x_for_z_df(
				df=dev_data, x_col_name='temperature_mean', y_col_name='precipitation', z_col_name='biome',
				z_value=bcode, name=str(Biome(bcode)),
				x_range=(-20,50), x_grids =35, y_range =(0,3000), y_grids =30
			)
			hexplot_y_vs_x_for_z_df(
				df=dev_data, x_col_name='temperature_mean', y_col_name='temperature_range', z_col_name='biome',
				z_value=bcode, name=str(Biome(bcode)),
				x_range=(-20,50), x_grids=35, y_range=(0,50), y_grids=25
			)
			hexplot_y_vs_x_for_z_df(
				df=dev_data, x_col_name='altitude', y_col_name='temperature_mean', z_col_name='biome',
				z_value=bcode, name=str(Biome(bcode)),
				x_range=(0,5000), x_grids =25, y_range=(-20,50), y_grids =35
			)
			hexplot_y_vs_x_for_z_df(
				df=dev_data, x_col_name='altitude', y_col_name='precipitation', z_col_name='biome',
				z_value=bcode, name=str(Biome(bcode)),
				x_range=(0,5000), x_grids =25, y_range =(0,3000), y_grids =30
			)
			hexplot_y_vs_x_for_z_df(
				df=dev_data, x_col_name='precipitation', y_col_name='rel_photosythesis', z_col_name='biome',
				z_value=bcode, name=str(Biome(bcode)),
				x_range=(0,3000), x_grids=30, y_range=(0,1), y_grids=20
			)
			hexplot_y_vs_x_for_z_df(
				df=dev_data, x_col_name='temperature_mean', y_col_name='rel_photosythesis', z_col_name='biome',
				z_value=bcode, name=str(Biome(bcode)),
				x_range=(-20,50), x_grids=35, y_range=(0,1), y_grids=20
			)
		exit(1)
	# dtree_zpickle = path.join(data_dir, 'dtree-model.pickle.gz')
	print('definitions classifier...')
	bc = BiomeClassifier(features.columns)
	fit_and_score(bc, input_data=features, labels=labels)
	##
	balancer = RandomUnderSampler()
	bfeatures, blabels = balancer.fit_resample(features, labels)
	print('balanced data:', len(bfeatures), 'rows')
	print('old params:', bc.get_param_array())
	def opti_bc(*params):
		bc.set_param_array(params)
		return bc.score(bfeatures, blabels)
	print('optimizing...')
	opt_p, iters = hillclimb.maximize(opti_bc, bc.get_param_array(), precision=0.1)
	print('...completed in %s iterations' % iters)
	bc.set_param_array(opt_p)
	print('new params:', bc.get_param_array())
	print('optimized definitions classifier...')
	#fit_and_score(bc, input_data=features, labels=labels)
	print(classification_report(y_true=blabels, y_pred=bc.predict(bfeatures)))
	percent_accuracy = 100 * bc.score(X=bfeatures, y=blabels)
	print('Overall accuracy: %s %%' % int(percent_accuracy))


	rp_pipe = Pipeline([
		('normalize', MinMaxScaler()),
		('my_classifier', ReferencePointClassifier(5))
	])
	print('reference point classifier...')
	fit_and_score(rp_pipe, input_data=bfeatures, labels=blabels)
	print('optimizing...')
	rp = rp_pipe['my_classifier']
	print('old params:', rp.get_param_array())
	def opti_rp(*params):
		rp.set_param_array(params)
		return rp_pipe.score(bfeatures, blabels)
	opti_batch_size = 10
	iter_count = 0
	# for batch in range(0, opti_batch_size):
	# 	opt_p, iters = hillclimb.maximize(opti_rp, rp.get_param_array(), precision=0.1, iteration_limit=10)
	# 	iter_count += iters
	# 	if iters < opti_batch_size:
	# 		break
	# 	zpickle(opt_p, 'opti-iter-%s.pickle.gz' % iter_count)
	opt_p = [4.74522233e-01, 5.97136563e-02, 2.21170157e-01, 3.31737679e-01
, 1.68830615e-01, 2.38661129e-02, 9.58740294e-01, 3.40067828e-03
, 1.99193367e-01, 6.70710135e-01, 9.04792666e-02, 3.63164350e-02
, 5.17211258e-01, 4.11254190e-02, 1.98408973e-01, 2.95791209e-01
, 6.42506576e-01, 5.49450967e-02, 3.61655164e-01, -9.20337467e-03
, 1.03954166e-01, 1.79754853e-01, 6.16359448e-01, 1.10553836e-02
, -8.01116145e-01, 1.60361649e+00, 2.38641173e-01, 5.85226417e-01
, 3.01822424e-01, 2.08827164e-02, -8.42267966e-01, 4.79010213e-03
, 2.41739258e-01, 5.18335164e-01, 2.45613098e-01, 2.51809247e-02
, 1.04527696e+00, -4.70551305e-02, 3.22202700e-01, 5.92476141e-01
, 1.05346578e-01, 4.56759490e-02, 9.64450157e-01, -1.37392296e-03
, 2.27874652e-01, 6.72113025e-01, 9.01038900e-02, 3.78424965e-02
, 1.07403543e+00, 2.11025635e-03, 5.30940390e-01, 4.90665364e-01
, 2.04334614e-01, 3.27762924e-02, 9.59799075e-01, 3.01728141e-03
, 2.76172990e-01, 6.13597381e-01, 7.85429299e-02, 4.54119638e-02
, 5.28845263e-01, 4.07051189e-02, 2.47987318e-01, 3.90981513e-01
, 5.93736303e-01, 2.78222561e-02, 1.04114652e+00, -3.28336810e-03
, 2.91753894e-01, 6.54442203e-01, 1.81461000e-01, 8.67428184e-03
, 5.20863843e-01, 5.96471171e-02, 2.42642400e-01, 4.48208326e-01
, 4.23211139e-01, -4.90405336e-03, 7.60191488e-01, -3.45635516e-02
, 3.00020862e-01, 5.23062718e-01, 3.51038712e-01, 4.61989097e-02
, 7.72914898e-01, 3.09479283e-03, 2.45043916e-01, 3.75516415e-01
, 4.81523955e-01, 2.81092783e-02, 4.97509420e-01, -4.68194705e-02
, 2.73140424e-01, 3.38627571e-01, 5.93735743e-01, 1.19503666e-02
, 7.20489562e-01, 2.55982168e-03, 3.11639088e-01, 5.36003673e-01
, 3.26463115e-01, 1.27768576e-02, 5.66884863e-01, -9.85462735e-03
, 2.94655991e-01, 3.48561937e-01, 4.35687125e-01, -6.32250234e-03
, 8.06999135e-01, -4.84098320e-02, 5.98830247e-01, 4.85298651e-01
, 1.54572800e-01, 7.14108620e-02, 4.73877323e-01, 5.61311349e-02
, 1.89685011e-01, 3.91044307e-01, 3.56962729e-01, 5.03646627e-02
, 7.48842371e-01, -5.95166711e-02, 2.84548080e-01, 5.80330682e-01
, 3.86792344e-01, 7.26229660e-03, -1.12948216e+00, 3.21608619e-03
, 2.57012755e-01, 2.57744282e-01, 6.33007526e-01, 1.12029379e-02
, 5.82783151e-01, -2.18458309e-02, 2.95717007e-01, 4.90978539e-01
, 6.49286985e-01, 7.53348414e-03, 9.71849036e-01, -2.19252746e-02
, 2.75546277e-01, 7.23628950e-01, 1.54027572e-01, 3.17102380e-02
, 7.31836033e-01, -4.88117600e-02, 6.78535819e-01, 5.27396560e-01
, 3.61248332e-01, 1.39877040e-02, 3.57735980e-01, -4.68094090e-02
, 2.26241854e-01, 1.94145334e-01, 6.88113928e-01, -8.89836922e-03
, -6.70242047e-01, 3.08203069e-03, 2.73266375e-01, 7.91979074e-01
, 2.77801067e-01, 6.77557802e-03, 8.98902225e-01, 1.55581220e-02
, 2.83997661e-01, 7.62390792e-01, 3.87480974e-01, 3.61068784e-02
, 1.01486276e+00, 3.36348496e-03, 6.94801712e-01, 6.78602290e-01
, 2.15935802e-01, 8.76573157e-03, -1.14739156e+00, 3.20733641e-03
, 2.55343646e-01, 2.73449004e-01, 5.67882419e-01, 1.27276909e-02
, 3.39412093e-01, 2.34864878e-02, 2.97155356e-01, 1.02349952e-01
, 6.02937245e-01, -7.75046013e-03, 9.25932717e-01, -2.36998965e-02
, 6.52715206e-01, 5.07276058e-01, 4.18485510e-01, -4.36994552e-02
, -9.70201290e-01, 2.36761756e-03, 3.99560928e-01, 3.66962314e-01
, 4.15035337e-01, 1.53226797e-02, -7.64197206e-01, 3.52483359e-03
, 2.58797556e-01, 7.29496658e-01, 3.77655566e-01, 3.84847308e-03
, 4.71212596e-01, 3.09121143e-03, 3.73755038e-01, 2.31737131e-01
, 4.07214874e-01, 2.05342308e-02, 9.22544169e-01, -9.06175394e-02
, 2.64522165e-01, 8.38151920e-01, 2.69116563e-01, -2.95563077e-02
, 6.83066356e-01, 5.24725904e-02, 4.53665257e-01, 7.49211276e-01
, 6.42830431e-01, -2.26928439e-02, 7.00747275e-01, -1.16934684e-02
, 8.01157379e-01, 4.71069545e-01, 4.94137806e-01, 4.30046674e-03
, 8.67477441e-01, 3.05538368e-03, 2.86306924e-01, 7.95031297e-01
, 3.75466502e-01, -2.95855785e-02, 2.86042368e-01, 6.78240508e-03
, 2.30966449e-01, 7.76091743e-01, 6.29519260e-01, 3.33183655e-03]
	print('...completed in %s iterations' % iter_count)
	rp.set_param_array(opt_p)
	print('new params:', rp.get_param_array())
	print('optimized definitions classifier...')
	# fit_and_score(bc, input_data=features, labels=labels)
	print(classification_report(y_true=blabels, y_pred=rp.predict(bfeatures)))
	percent_accuracy = 100 * rp_pipe.score(X=bfeatures, y=blabels)
	print('Overall accuracy: %s %%' % int(percent_accuracy))

	# for dtree_size in range(2,10):
	dtree_size = 6
	# if RELOAD or not path.exists(dtree_zpickle):
	dtree_pipe = Pipeline([
		('normalize', MinMaxScaler()),
		('decision_tree', DecisionTreeClassifier(max_depth=dtree_size))
	])
	print('fitting decision tree model with %s layers...' % dtree_size)
		# zpickle(pipe, dtree_zpickle)
	# else:
		# pipe = zunpickle(dtree_zpickle)
	fit_and_score(dtree_pipe, input_data=bfeatures, labels=blabels)

	#print(export_text(pipe['decision_tree'], max_depth=dtree_size))
	# graphviz_export(
	# 	pipe['decision_tree'], 'dtree', feature_names=features.columns,
	# 	class_names=[str(n) for n in pipe['decision_tree'].classes_]
	# )
	#
	print('...Done!')

def hexplot_y_vs_x_for_z_df(df: DataFrame, x_col_name: str, y_col_name: str, z_col_name: str,
		z_value, name, x_range: (float,float), x_grids: int, y_range: (float,float), y_grids: int,
		cmap='rainbow', show=False
	):
	hexplot_y_vs_x_for_z(
		xdata=df[x_col_name], ydata=df[y_col_name], zdata=df[z_col_name], z_value=z_value, name=name,
		x_range=x_range, x_grids=x_grids, y_range=y_range, y_grids=y_grids,
		x_axis_title=x_col_name, y_axis_title=y_col_name, cmap=cmap, show=show
	)

def hexplot_y_vs_x_for_z(xdata: ndarray, ydata: ndarray, zdata: ndarray, z_value, name,
		x_range: (float,float), x_grids: int, y_range: (float,float), y_grids: int,
		x_axis_title: str, y_axis_title: str, cmap='rainbow', show=False
	):
	filename = '%s vs %s - %s.png' % (y_axis_title, x_axis_title, name)
	print('plotting %s...' % filename)
	rows = zdata == z_value
	#pyplot.scatter(dev_data['temperature_mean'][rows], dev_data['precipitation'][rows], label=bname, alpha=0.01)
	pyplot.hexbin(
		xdata[rows], ydata[rows], label=name,
		gridsize=(x_grids,y_grids), extent=(x_range[0],x_range[1] , y_range[0],y_range[1]),
		cmap=cmap
	)
	pyplot.xlim(x_range)
	pyplot.ylim(y_range)
	# pyplot.legend(loc='upper center')
	pyplot.grid()
	pyplot.title(name)
	pyplot.xlabel(x_axis_title)
	pyplot.ylabel(y_axis_title)
	pyplot.savefig(filename)
	if show:
		pyplot.show()
	pyplot.clf()

def fit_and_score(pipe: Pipeline, input_data: DataFrame, labels: ndarray):
	## NOTE:
	## precision = fraction of positive predictions that were correct (true positives/(true+false positives))
	## recall = fraction that were correctly predicted for this class (true positives/(true pod.+false neg.)
	## f1-score = 2*(Recall * Precision) / (Recall + Precision)
	## support = total number of this class
	pipe.fit(X=input_data, y=labels)
	print('Definitions:')
	print('\tprecision - true positives / all positive IDs')
	print('\trecall - true positives / real number')
	print(classification_report(y_true=labels, y_pred=pipe.predict(input_data)))
	percent_accuracy = 100 * pipe.score(X=input_data, y=labels)
	print('Overall accuracy: %s %%' % int(percent_accuracy+0.5))


class BiomeClassifier(BaseEstimator, TransformerMixin, ClassifierMixin):
	def __init__(self, columns):
		# constants
		self.jungle_ps = 0.748
		self.barren_ps = 0.189
		self.sand_sea_min_temp = 15
		self.wetland_min_precip = 1225
		self.desert_max_precip = 412
		## happy tree zone elipsoid
		self.tree_mean_var_focus1 = numpy.asarray([ -1.40, 36.2], dtype=numpy.float32)
		self.tree_mean_var_focus2 = numpy.asarray([11, 2.2], dtype=numpy.float32)
		self.treellipse_dist = 54.6 # sum of d1 and d2 of a point relative to f1 and f2
		self.broadleaf_temp_precip_divider = numpy.asarray([[-1.8,1197],[10.5,603]], dtype=float32)
		# sanity check
		self.columns = list(columns)
		for req in ['temperature_mean', 'temperature_range', 'precipitation', 'altitude', 'pressure', 'solar_flux']:
			if req not in self.columns:
				raise ValueError('Missing required data column %s' % req)
		self.index_mean_temp = self.columns.index('temperature_mean')
		self.index_temp_var = self.columns.index('temperature_range')
		self.index_precip = self.columns.index('precipitation')
		self.index_pressure = self.columns.index('pressure')
		self.index_altitude = self.columns.index('altitude')
		self.index_solar_flux = self.columns.index('solar_flux')

	def get_param_array(self) -> ndarray:
		p=numpy.zeros((14,), dtype=float32)
		p[0] = self.jungle_ps
		p[1] = self.barren_ps
		p[2] = self.sand_sea_min_temp
		p[3] = self.wetland_min_precip
		p[4] = self.desert_max_precip
		p[5:7] = self.tree_mean_var_focus1
		p[7:9] = self.tree_mean_var_focus2
		p[9] = self.treellipse_dist
		p[10:12] = self.broadleaf_temp_precip_divider[0]
		p[12:14] = self.broadleaf_temp_precip_divider[1]
		return p

	def set_param_array(self, p: ndarray):
		self.jungle_ps = p[0]
		self.barren_ps = p[1]
		self.sand_sea_min_temp = p[2]
		self.wetland_min_precip = p[3]
		self.desert_max_precip = p[4]
		self.tree_mean_var_focus1 = p[5:7]
		self.tree_mean_var_focus2 = p[7:9]
		self.treellipse_dist = p[9]
		self.broadleaf_temp_precip_divider[0] = p[10:12]
		self.broadleaf_temp_precip_divider[1] = p[12:14]

	def fit(self, X, y):
		# Check that X and y have correct shape
		X: ndarray = numpy.asarray(X)
		y: ndarray = numpy.asarray(y)
		X, y = check_X_y(X, y)
		# Store the classes seen during fit
		self.classes_ = unique_labels(y)
		self.feature_count_ = len(X[0])
		## no fitting operation
		# Return the classifier
		return self

	def biome_for(self, altitude: ndarray, mean_temp: ndarray, annual_precip: ndarray, temp_var: ndarray, pressure: ndarray, solar_flux: ndarray):
		out = numpy.zeros(mean_temp.shape, dtype=numpy.uint8)
		# NOTE: boolean * is AND and + is OR
		photosynth = photosynthesis_score(
			mean_temp_C  = mean_temp, temp_variation_C = temp_var, precip_mm=annual_precip,
			solar_flux_Wpm2=solar_flux, pressure_kPa=pressure
		)
		### terrestrial biomes ###
		## super high GPP means jungle
		out[(altitude >= 0) * (photosynth >= self.jungle_ps)] = Biome.JUNGLE.value
		## super low GPP is barren or sand sea
		out[(altitude >= 0) * (photosynth <= self.barren_ps) * (mean_temp >= self.sand_sea_min_temp)] = Biome.SAND_SEA.value
		out[(altitude >= 0) * (photosynth <= self.barren_ps) * (mean_temp < self.sand_sea_min_temp)] = Biome.BARREN.value
		## wetlands wetter than forests & grasslands wetter than deserts
		out[(altitude >= 0) * (photosynth < self.jungle_ps) * (photosynth > self.barren_ps) \
			* (annual_precip >= self.wetland_min_precip)] = Biome.WETLAND.value
		out[(altitude >= 0) * (photosynth < self.jungle_ps) * (photosynth > self.barren_ps) \
			* (annual_precip <= self.desert_max_precip)] = Biome.DESERT_SHRUBLAND.value
		### trees in happy-tree-zone, otherwise only grass grows, and needleleaf trees are hardier than broadleaf
		treelipse_dist = sqrt(square(mean_temp - self.tree_mean_var_focus1[0]) + square(temp_var - self.tree_mean_var_focus1[1])) \
			+ sqrt(square(mean_temp - self.tree_mean_var_focus2[0]) + square(temp_var - self.tree_mean_var_focus2[1]))
		out[(altitude >= 0) * (photosynth < self.jungle_ps) * (photosynth > self.barren_ps) \
			* (annual_precip > self.desert_max_precip) * (annual_precip < self.wetland_min_precip) \
			* (treelipse_dist > self.treellipse_dist)] = Biome.GRASSLAND.value
		div_slope = (self.broadleaf_temp_precip_divider[1,1] - self.broadleaf_temp_precip_divider[0,1]) \
				/ (self.broadleaf_temp_precip_divider[1,0] - self.broadleaf_temp_precip_divider[0,0])
		div_offset = self.broadleaf_temp_precip_divider[0,1] \
				- div_slope * self.broadleaf_temp_precip_divider[0,0]
		out[(altitude >= 0) * (photosynth < self.jungle_ps) * (photosynth > self.barren_ps) \
			* (annual_precip > self.desert_max_precip) * (annual_precip < self.wetland_min_precip) \
			* (treelipse_dist <= self.treellipse_dist) * (annual_precip < (div_slope * mean_temp + div_offset))] = Biome.NEEDLELEAF_FOREST.value
		out[(altitude >= 0) * (photosynth < self.jungle_ps) * (photosynth > self.barren_ps) \
			* (annual_precip > self.desert_max_precip) * (annual_precip < self.wetland_min_precip) \
			* (treelipse_dist <= self.treellipse_dist) * (annual_precip >= (div_slope * mean_temp + div_offset))] = Biome.SEASONAL_FOREST.value
		del treelipse_dist
		return out

	def predict(self, X):
		# Check is fit had been called
		check_is_fitted(self)

		# Input validation
		X = check_array(X)
		X = numpy.asarray(X)

		return self.biome_for(
			altitude=X[:, self.index_altitude],
			mean_temp=X[:, self.index_mean_temp],
			annual_precip=X[:, self.index_precip],
			temp_var=X[:, self.index_temp_var],
			pressure=X[:, self.index_pressure],
			solar_flux=X[:, self.index_solar_flux]
		)

class ReferencePointClassifier(BaseEstimator, TransformerMixin, ClassifierMixin):
	def __init__(self, num_pts_per_class):
		self.num_pts_per_class = num_pts_per_class
		pass

	def fit(self, X, y):
		# Check that X and y have correct shape
		X: ndarray = numpy.asarray(X)
		y: ndarray = numpy.asarray(y)
		X, y = check_X_y(X, y)
		# Store the classes seen during fit
		self.classes_ = unique_labels(y)
		self.class_count_ = len(self.classes_)
		self.feature_count_ = len(X[0])
		# fitting operation
		ref_points = []
		for i in range(0, self.class_count_):
			L = self.classes_[i]
			km = KMeans(n_clusters=self.num_pts_per_class)
			km.fit(X[y == L])
			ref_points.append(km.cluster_centers_)
		self.ref_points = numpy.asarray(ref_points)
		print('self.ref_points.shape',self.ref_points.shape)
		# Return the classifier
		return self

	def get_param_array(self):
		return self.ref_points.reshape((self.class_count_ * self.num_pts_per_class * self.feature_count_,))

	def set_param_array(self, p: ndarray):
		self.ref_points = numpy.asarray(p).reshape((self.class_count_, self.num_pts_per_class, self.feature_count_))

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