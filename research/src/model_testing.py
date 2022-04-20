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
	do_training = False
	if not do_training:
		print('Biome classifier accuracy:')
		earth_bc = BiomeClassifier(columns=features.columns, exoplanet=False)
		fit_and_score(earth_bc, input_data=features, labels=labels)
		print('EXOPLANET MODE:')
		exo_bc = BiomeClassifier(columns=features.columns, exoplanet=True)
		fit_and_score(exo_bc, input_data=features, labels=labels)
		exit(1)
	# dtree_zpickle = path.join(data_dir, 'dtree-model.pickle.gz')
	print('definitions classifier...')
	bc = OldBiomeClassifier(features.columns)
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
	print('rp.classes_ =', rp.classes_)
	normalizer: MinMaxScaler = rp_pipe['normalize']
	print('normalizer.data_min_ =', normalizer.data_min_)
	print('normalizer.data_max_ =', normalizer.data_max_)
	print('normalizer.data_range_ =', normalizer.data_range_)
	print('normalizer.scale_ =', normalizer.scale_)

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

## inputs:  ['solar_flux', 'pressure', 'altitude', 'temperature_mean', 'temperature_range', 'precipitation']
terrestrial_data_normalizer_minmaxes = DataFrame(numpy.asarray([
	## mins
	[ 1.1084170e-19,  4.5783211e+01, -1.6270000e+03, -2.4903875e+01,  1.2730642e-01,  0.0000000e+00],
	## maxes
	[1.9760277e+03, 1.6078096e+04, 6.3260000e+03, 5.4133900e+01, 4.2466022e+01,  5.8917738e+04]
], dtype=float32),
	columns=['solar_flux', 'pressure', 'altitude', 'temperature_mean', 'temperature_range', 'precipitation']
)

terrestrial_reference_classes = numpy.asarray([1, 2, 3, 4, 5, 6, 8, 9], dtype=uint8)
terrestrial_reference_points = numpy.asarray([
## wetlands
[[9.66866970e-01, 3.44602927e-03, 2.21051112e-01, 6.68643355e-01,
 1.16806954e-01, 3.32654789e-02],
[4.23255265e-01, 3.67337209e-03, 2.17167795e-01, 2.33419389e-01,
 6.37225509e-01, 1.74140818e-02],
[4.76645857e-01, 9.57702287e-03, 2.21521258e-01, 3.82326394e-01,
 3.45598221e-01, 2.20833831e-02],
[8.00941825e-01, 3.66082601e-03, 2.37592861e-01, 5.87369025e-01,
 2.99632013e-01, 2.10805945e-02],
[5.61772823e-01, 3.33963661e-03, 2.29130179e-01, 3.05382371e-01,
 6.42809033e-01, 1.41723473e-02]],

[[9.89321232e-01, 3.35620833e-03, 2.28097796e-01, 6.73157573e-01,
 8.69841650e-02, 3.87548171e-02],
[9.04909372e-01, 3.06568365e-03, 2.82655239e-01, 6.13019466e-01,
 1.73770785e-01, 3.27553898e-02],
[7.67642021e-01, 3.95438354e-03, 2.42302433e-01, 5.22339344e-01,
 2.47791708e-01, 2.49677077e-02],
[9.88941193e-01, 2.98168021e-03, 2.96959370e-01, 6.42321587e-01,
 8.64978433e-02, 3.34428139e-02],
[9.70767677e-01, 2.14036391e-03, 4.65123057e-01, 5.65884590e-01,
 1.30025938e-01, 3.25797834e-02]],

[[5.33872604e-01, 3.24080512e-03, 2.45580614e-01, 3.42286527e-01,
 5.98508716e-01, 1.21523589e-02],
[9.47117805e-01, 3.00760171e-03, 2.93881506e-01, 6.73809648e-01,
 1.72600970e-01, 2.12327447e-02],
[7.72515893e-01, 2.98179965e-03, 2.96573430e-01, 5.22810459e-01,
 3.25278640e-01, 2.12862641e-02],
[6.75903678e-01, 3.13613890e-03, 2.64301360e-01, 3.99888694e-01,
 5.19578099e-01, 1.56620871e-02],
[5.40472388e-01, 3.42405331e-03, 2.30422705e-01, 4.39976603e-01,
 4.12625283e-01, 1.38190407e-02]],

[[4.93523210e-01, 6.17733039e-03, 2.27266490e-01, 4.03869301e-01,
 3.39339316e-01, 2.22206078e-02],
[5.96311033e-01, 2.68650148e-03, 3.45203191e-01, 3.87292534e-01,
 4.35955614e-01, 1.26070864e-02],
[5.29044151e-01, 3.22159147e-03, 2.48883799e-01, 3.29995036e-01,
 5.76287508e-01, 1.34433182e-02],
[7.21484363e-01, 2.99842726e-03, 2.92114198e-01, 5.12095809e-01,
 3.24575722e-01, 2.22618878e-02],
[8.81542325e-01, 1.64361310e-03, 5.71533740e-01, 4.83431935e-01,
 2.16882482e-01, 2.16850471e-02]],

[[9.59432840e-01, 3.11504863e-03, 2.74776757e-01, 7.23367631e-01,
 1.78709954e-01, 1.92522723e-02],
[4.74296480e-01, 3.23710404e-03, 2.58537203e-01, 2.61353970e-01,
 6.34064853e-01, 1.12368092e-02],
[6.64515555e-01, 3.18234414e-03, 3.06940168e-01, 5.22040606e-01,
 6.53039217e-01, 7.28974305e-03],
[7.66061962e-01, 3.05869710e-03, 2.89622694e-01, 5.94409645e-01,
 3.83008778e-01, 1.39850471e-02],
[8.42199624e-01, 1.25335844e-03, 6.73347592e-01, 4.97755945e-01,
 3.63429934e-01, 9.26538371e-03]],

[[8.95991564e-01, 1.89115328e-03, 5.33740938e-01, 6.67914510e-01,
 3.13437641e-01, 7.20088789e-03],
[4.01492923e-01, 3.23354616e-03, 2.45115086e-01, 1.81874037e-01,
 7.13867784e-01, 9.90626216e-03],
[4.52764899e-01, 3.29471100e-03, 2.54418224e-01, 2.73410648e-01,
 5.72441339e-01, 1.25368591e-02],
[8.49489868e-01, 3.10155470e-03, 2.77285367e-01, 7.32748032e-01,
 4.19105798e-01, 4.85429959e-03],
[9.29874182e-01, 3.12989624e-03, 2.72464097e-01, 7.93554485e-01,
 2.78345227e-01, 6.77830819e-03]],

[[3.31589788e-01, 4.77934768e-03, 2.59708703e-01, 1.02509975e-01,
 6.02857947e-01, 1.10007264e-02],
[8.50780249e-01, 1.34407193e-03, 6.52715206e-01, 5.39237857e-01,
 4.32048351e-01, 6.30054483e-03],
[4.08641100e-01, 3.13554448e-03, 3.11209381e-01, 2.22716048e-01,
 4.45691258e-01, 1.42845185e-02],
[6.29764795e-01, 2.41161673e-03, 3.99556339e-01, 3.67565900e-01,
 4.15959805e-01, 1.53236073e-02],
[8.35651517e-01, 3.56870447e-03, 2.58797556e-01, 7.30460644e-01,
 3.78586709e-01, 3.84847308e-03]],

[[9.33901429e-01, 3.17807565e-03, 2.64219820e-01, 8.35781872e-01,
 2.90852070e-01, 1.64775155e-03],
[8.71193349e-01, 3.09935329e-03, 2.80733943e-01, 8.08090866e-01,
 4.04747546e-01, 1.74297113e-03],
[7.51265168e-01, 2.74931733e-03, 3.49162489e-01, 6.90088212e-01,
 5.94493032e-01, 2.51922244e-03],
[8.31308663e-01, 8.75420170e-04, 7.69911528e-01, 4.75095689e-01,
 4.20278132e-01, 4.32941131e-03],
[2.46214390e-01, 3.61543931e-02, 1.97870716e-01, 7.81985641e-01,
 4.34179634e-01, 3.16758081e-03]]
	], dtype=float32)
def classify_biomes(altitude: ndarray, mean_temp: ndarray, annual_precip: ndarray, temp_var: ndarray, pressure: ndarray, solar_flux: ndarray, exoplanet=False) -> ndarray:
	biomes = numpy.zeros(altitude.shape, dtype=numpy.uint8)
	# NOTE: boolean * is AND and + is OR
	## terrestrial biomes
	terrestrial_biomes = (altitude > 0)
	minmax = terrestrial_data_normalizer_minmaxes
	### normalize data for nearest control point analysis
	t_data = numpy.asarray([
		### ['solar_flux', 'pressure', 'altitude', 'temperature_mean', 'temperature_range', 'precipitation']
		(solar_flux - minmax['solar_flux'][0])/(minmax['solar_flux'][1]-minmax['solar_flux'][0]),
		(pressure - minmax['pressure'][0])/(minmax['pressure'][1]-minmax['pressure'][0]),
		(altitude - minmax['altitude'][0])/(minmax['altitude'][1]-minmax['altitude'][0]),
		(mean_temp - minmax['temperature_mean'][0])/(minmax['temperature_mean'][1]-minmax['temperature_mean'][0]),
		(temp_var - minmax['temperature_range'][0])/(minmax['temperature_range'][1]-minmax['temperature_range'][0]),
		(annual_precip - minmax['precipitation'][0])/(minmax['precipitation'][1]-minmax['precipitation'][0]),
	]).T
	class_dists = numpy.zeros((len(terrestrial_reference_classes), len(altitude)), dtype=float32) + numpy.inf
	for i in range(0, len(terrestrial_reference_classes)):
		class_dists[i] = euclidean_distances(t_data, terrestrial_reference_points[i]).min(axis=1)

	closest = numpy.argmin(class_dists, axis=0)
	biomes[terrestrial_biomes] = terrestrial_reference_classes[closest]
	### training set didn't have tundra :(
	biomes[terrestrial_biomes * (mean_temp < 5) * (mean_temp+temp_var > 0)] = Biome.TUNDRA.value
	### turn over-saturated rainfall areas to wetland
	max_rain_limit = 4170
	biomes[terrestrial_biomes * (mean_temp >= 5) * (annual_precip > max_rain_limit)] = Biome.WETLAND.value
	## aquatic biomes
	aquatic_biomes = altitude <= 0
	biomes[aquatic_biomes] = Biome.DEEP_OCEAN.value
	biomes[aquatic_biomes * (altitude > -200)] = Biome.SHALLOW_OCEAN.value
	biomes[aquatic_biomes * (solar_flux >= 85)] = Biome.ROCKY_SHALLOWS.value
	biomes[aquatic_biomes * (solar_flux >= 85) * (mean_temp > 5) * (mean_temp < 20)] = Biome.SEA_FOREST.value
	biomes[aquatic_biomes * (solar_flux >= 85) * (mean_temp >= 20) * (mean_temp < 30)] = Biome.TROPICAL_REEF.value
	## extreme biomes
	min_rain_limit = 110
	biomes[terrestrial_biomes * (annual_precip < min_rain_limit) * (mean_temp > 15)] = Biome.SAND_SEA.value
	biomes[terrestrial_biomes * (annual_precip < min_rain_limit) * (mean_temp <= 15)] = Biome.BARREN.value
	boiling_temp = boiling_point(pressure)
	biomes[aquatic_biomes * (mean_temp >= boiling_temp)] = Biome.BOILING_SEA.value
	biomes[(mean_temp+temp_var <= 0)] = Biome.ICE_SHEET.value
	if exoplanet:
		## astronomical biomes
		biomes[terrestrial_biomes * (mean_temp >= boiling_temp)] = Biome.MOONSCAPE.value
		### cryogen params based on liquid nitrogen ( https://www.engineeringtoolbox.com/nitrogen-d_1421.html )
		#### alternative cryogens: ammonia, methane; both would oxidize in presense of oxygen, so not as interesting
		#### (oxygen is a pretty common element)
		cryo_crit_temp = -147 # C
		cryo_crit_pressure = 3400 # kPa
		cryo_triple_temp = -210 # C
		# cryo_triple_pressure = 12.5 # kPa
		cryo = (mean_temp > cryo_triple_temp)*(mean_temp < cryo_crit_temp)*(pressure < cryo_crit_pressure)*( pressure > (1.6298e9*numpy.exp(0.08898*mean_temp)))
		biomes[aquatic_biomes * cryo] = Biome.CRYOGEN_SEA.value
		rock_melting_point = 600
		rock_boiling_point = 2230
		biomes[aquatic_biomes * (mean_temp > rock_melting_point) * (mean_temp < rock_boiling_point)] = Biome.MAGMA_SEA.value
	return biomes

def boiling_point(pressure_kPa: ndarray) -> ndarray:
	ln_mbar = numpy.log(pressure_kPa*10)
	coeffs_low_pressure = numpy.asarray([0.051769, 0.65545, 10.387, -10.619], dtype=float32)
	coeffs_high_pressure = numpy.asarray([0.47092, -8.2481, 75.520, -183.98], dtype=float32)
	lp = numpy.polyval(coeffs_low_pressure, ln_mbar)
	hp = numpy.polyval(coeffs_high_pressure, ln_mbar)
	out = lp
	out[pressure_kPa > 1013] = hp
	return out

class BiomeClassifier(BaseEstimator, TransformerMixin, ClassifierMixin):
	def __init__(self, columns, exoplanet=False):
		# sanity check
		self.exoplanet = exoplanet
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

	def predict(self, X):
		# Check is fit had been called
		check_is_fitted(self)

		# Input validation
		X = check_array(X)
		X = numpy.asarray(X)

		return classify_biomes(
			altitude=X[:, self.index_altitude],
			mean_temp=X[:, self.index_mean_temp],
			annual_precip=X[:, self.index_precip],
			temp_var=X[:, self.index_temp_var],
			pressure=X[:, self.index_pressure],
			solar_flux=X[:, self.index_solar_flux],
			exoplanet=self.exoplanet
		)


class OldBiomeClassifier(BaseEstimator, TransformerMixin, ClassifierMixin):
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