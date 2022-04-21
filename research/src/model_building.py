import os, shutil, sys, re, requests, base64, urllib.parse, numpy, pandas, json, pickle, ssl, time, gzip
from os import path
from subprocess import call
from PIL import Image
from copy import deepcopy

from imblearn.under_sampling import RandomUnderSampler
from numpy import ndarray, nan, uint8, float32, logical_and, logical_or, logical_not, clip, sin, cos, square, sqrt, power, log10
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
	PATCH_SOLAR_FLUX = True
	data_dir = 'data'
	data_sets_zpickles = [path.join(data_dir, 'Earth_biome_DataFrame-%s.pickle.gz' % n) for n in range(0,4)]
	# data splitting: 3 training batches and 1 test batch
	src_data: DataFrame = zunpickle(data_sets_zpickles[0])
	if PATCH_SOLAR_FLUX:
		# had accidentally used pi/2 instead of 2/pi
		two_over_pi = 2 / numpy.pi
		pi_over_2 = 0.5 * numpy.pi
		src_data['solar_flux'] = src_data['solar_flux'] / pi_over_2 * two_over_pi
	# remove unclassified rows
	src_data: DataFrame = src_data[src_data['biome'] != 0]
	# remove unclassified rows and reduce data size and remove oceans
	dev_data = src_data[src_data['biome'] < 0x10].copy()
	del src_data
	# patch-in tundra
	tmp_b = numpy.asarray(dev_data['biome'])
	tmp_b[(dev_data['precipitation'] > 110) * (dev_data['temperature_mean'] < 5) \
					  * (dev_data['temperature_mean'] + dev_data['temperature_range'] > 0)] = Biome.TUNDRA.value
	dev_data['biome'] = tmp_b
	del tmp_b
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
	balancer = RandomUnderSampler()
	bfeatures, blabels = balancer.fit_resample(features, labels)


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
	do_training = True
	if not do_training:
		print('Biome classifier accuracy:')
		earth_bc = BiomeClassifier(columns=features.columns, exoplanet=False)
		fit_and_score(earth_bc, input_data=features, labels=labels)
		print('EXOPLANET MODE:')
		exo_bc = BiomeClassifier(columns=features.columns, exoplanet=True)
		fit_and_score(exo_bc, input_data=bfeatures, labels=blabels)
		exit(1)
	# dtree_zpickle = path.join(data_dir, 'dtree-model.pickle.gz')
	print('definitions classifier...')
	bc = OldBiomeClassifier(features.columns)
	fit_and_score(bc, input_data=features, labels=labels)
	##
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
	zpickle(bc, 'bc.pickle.gz')


	print('restricting features...')
	# change rainfall to sqrt or log10 to turn source into something resembling a normal distribution
	bfeatures = bfeatures.assign(**{'sqrt_precipitation': numpy.sqrt(bfeatures['precipitation'])})
	bfeatures = bfeatures.drop(['pressure', 'altitude', 'precipitation'], axis=1, inplace=False)
	my_scaler = MinMaxScaler()
	#my_scaler.fit(bfeatures)
	my_scaler.fit(DataFrame(
		columns=['solar_flux','temperature_mean','temperature_range','sqrt_precipitation'],
		data=[
			[  0, -20, 0 ,  0], # mins
			[800, 50 , 35, 75] # maxes
		]
	))
	print('normalized features', my_scaler.feature_names_in_)
	print('mins  ', my_scaler.data_min_)
	print('maxs  ', my_scaler.data_max_)
	print('ranges', my_scaler.data_range_)
	print(list(bfeatures.columns))
	rp_pipe = Pipeline([
		('normalize', my_scaler),
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
	for batch in range(0, opti_batch_size):
		opt_p, iters = hillclimb.maximize(opti_rp, rp.get_param_array(), precision=0.1, iteration_limit=10)
		iter_count += iters
		if iters < opti_batch_size:
			zpickle(opt_p, 'opti-iter-%s.pickle.gz' % iter_count)
			break
		zpickle(opt_p, 'opti-iter-%s.pickle.gz' % iter_count)
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
	zpickle(rp_pipe, 'rp_pipe.pickle.gz')

	# for dtree_size in range(2,10):
	dtree_size = 6
	# if RELOAD or not path.exists(dtree_zpickle):
	dtree_pipe = Pipeline([
		('normalize', my_scaler),
		('decision_tree', DecisionTreeClassifier(max_depth=dtree_size))
	])
	print('fitting decision tree model with %s layers...' % dtree_size)
		# zpickle(pipe, dtree_zpickle)
	# else:
		# pipe = zunpickle(dtree_zpickle)
	fit_and_score(dtree_pipe, input_data=bfeatures, labels=blabels)

	zpickle(dtree_pipe, 'dtree_pipe.pickle.gz')
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

terrestrial_reference_classes = numpy.asarray([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=uint8)
terrestrial_reference_points = numpy.asarray([
## wetlands
       [[0.97589505, 0.6692817 , 0.09676683, 0.42183435],
        [0.2872733 , 0.5562218 , 0.21704593, 0.3098737 ],
        [0.95833284, 0.6877248 , 0.12377492, 0.2995282 ],
        [0.6171483 , 0.47020113, 0.4836682 , 0.22195342],
        [0.81850535, 0.60123855, 0.25867933, 0.31303504]],
## jungle
       [[0.7665621 , 0.5300055 , 0.2408872 , 0.3123359 ],
        [0.99121696, 0.6713649 , 0.07588506, 0.40304184],
        [0.98553646, 0.67212886, 0.08356771, 0.3337861 ],
        [0.9209426 , 0.59560406, 0.15855226, 0.3750781 ],
        [0.99228674, 0.67052644, 0.07420062, 0.49766815]],
## seasonal forest
       [[0.82307386, 0.54830164, 0.28397045, 0.32422626],
        [0.95406234, 0.68983954, 0.16054682, 0.29840717],
        [0.5337313 , 0.44197488, 0.4220576 , 0.24119267],
        [0.70596063, 0.5029748 , 0.37620285, 0.26919958],
        [0.65009725, 0.41467762, 0.53735024, 0.24624129]],
## needleleaf forest
       [[0.8442506 , 0.513412  , 0.23853904, 0.31593102],
        [0.4755671 , 0.42182055, 0.32860836, 0.25947723],
        [0.69879943, 0.5263777 , 0.3583926 , 0.24800086],
        [0.6385724 , 0.44265494, 0.30205786, 0.41645652],
        [0.59855306, 0.41948298, 0.4608879 , 0.21030518]],
## grassland
       [[0.9590115 , 0.69129807, 0.14321554, 0.33431706],
        [0.64463437, 0.51307285, 0.6764352 , 0.17131203],
        [0.75970644, 0.53838587, 0.34264302, 0.25237092],
        [0.9574419 , 0.76865923, 0.21147878, 0.2162868 ],
        [0.7787093 , 0.64991206, 0.49281284, 0.1717132 ]],
## desert
       [[0.8768907 , 0.68539584, 0.30395174, 0.18175352],
        [0.85951805, 0.75583154, 0.43008733, 0.13515931],
        [0.9133944 , 0.80276865, 0.33543584, 0.15386288],
        [0.95464563, 0.8058968 , 0.2042541 , 0.1794926 ],
        [0.7509371 , 0.62957406, 0.44375542, 0.1542665 ]],
## tundra
       [[0.4441414 , 0.30920148, 0.4959661 , 0.24957538],
        [0.4513571 , 0.23461857, 0.732274  , 0.2127717 ],
        [0.6739347 , 0.34742635, 0.41046205, 0.26215446],
        [0.577827  , 0.32734275, 0.62989986, 0.22067626],
        [0.37011942, 0.15006503, 0.65958476, 0.18708763]],
## barren
       [[0.29481938, 0.09472984, 0.59135556, 0.06860657],
        [0.86539465, 0.7506361 , 0.37203112, 0.11493613],
        [0.664666  , 0.6056427 , 0.46542227, 0.14238815],
        [0.6938545 , 0.43799615, 0.30913985, 0.2867542 ],
        [0.8466273 , 0.53237015, 0.44636855, 0.16200702]],
## sandsea
       [[0.82119286, 0.48783484, 0.44511366, 0.10902377],
        [0.9354581 , 0.8444746 , 0.28542006, 0.076657  ],
        [0.75143087, 0.70467633, 0.602095  , 0.09906711],
        [0.8729486 , 0.81519806, 0.4026484 , 0.0783796 ],
        [0.24349129, 0.7866096 , 0.45044297, 0.11177942]]
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
	biomes = numpy.ma.masked_array(biomes, mask=logical_not(terrestrial_biomes))
	biomes[:] = terrestrial_reference_classes[closest]
	biomes = numpy.asarray(biomes)
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
	out = numpy.ma.masked_array(lp, mask=pressure_kPa <= 1013)
	out[:] = hp
	return numpy.asarray(out)

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