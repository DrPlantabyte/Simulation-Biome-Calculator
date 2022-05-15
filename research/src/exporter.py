import os, shutil, sys, numpy, pandas, pickle, time, gzip
from os import path
from numpy import ndarray, nan, uint8, float32, logical_and, logical_or, logical_not, clip, sin, cos, square, sqrt, power, log10
from pandas import DataFrame
from matplotlib import pyplot
from biome_enum import Biome
### cython import ###
import pyximport
pyximport.install()
from biome_classifier_model import classify_planet_biomes

def main():
	PATCH_SOLAR_FLUX = False
	##
	data_dir = 'data'
	subsamp = 10
	##
	gravity_m_per_s2 = 9.81
	mean_surface_pressure_kPa = 101.3
	toa_solar_flux_Wpm2 = 1373
	mean_solar_flux_Wpm2: ndarray = zunpickle(path.join(data_dir, 'solar_flux_1852m_singrid.pickle.gz'))[::subsamp, ::subsamp].copy()
	altitude_m: ndarray = zunpickle(path.join(data_dir, 'altitude_1852m_singrid.pickle.gz'))[::subsamp, ::subsamp].copy()
	mean_temp_C: ndarray = zunpickle(path.join(data_dir, 'surf_temp_mean_1852m_singrid.pickle.gz'))[::subsamp, ::subsamp].copy()
	temp_var_C: ndarray = zunpickle(path.join(data_dir, 'surf_temp_var_1852m_singrid.pickle.gz'))[::subsamp, ::subsamp].copy()
	annual_precip_mm: ndarray = zunpickle(path.join(data_dir, 'precip_mean_1852m_singrid.pickle.gz'))[::subsamp, ::subsamp].copy()
	original_biomes: ndarray = zunpickle(path.join(data_dir, 'drp_biomes_1852m_singrid.pickle.gz'))[::subsamp, ::subsamp].copy()
	exoplanet = True
	_shape = original_biomes.shape
	calculated_biomes = classify_planet_biomes(
		gravity_m_per_s2,  # float gravity_m_per_s2,
		mean_surface_pressure_kPa,  # float mean_surface_pressure_kPa,
		mean_solar_flux_Wpm2.reshape((-1,)),  # float[:] mean_solar_flux_Wpm2,
		altitude_m.reshape((-1,)),  # float[:] altitude_m,
		mean_temp_C.reshape((-1,)),  # float[:] mean_temp_C,
		temp_var_C.reshape((-1,)),  # float[:] temp_var_C,
		annual_precip_mm.reshape((-1,)),  # float[:] annual_precip_mm,
		exoplanet  # bint exoplanet,
	).reshape(_shape)
	if PATCH_SOLAR_FLUX:
		# had accidentally used pi/2 instead of 2/pi
		two_over_pi = 2 / numpy.pi
		pi_over_2 = 0.5 * numpy.pi
		mean_solar_flux_Wpm2 = mean_solar_flux_Wpm2 / pi_over_2 * two_over_pi
	##
	data_table = DataFrame.from_dict({
		'gravity_m_per_s2':[gravity_m_per_s2]*len(annual_precip_mm.ravel()),
		'mean_surface_pressure_kPa':[mean_surface_pressure_kPa]*len(annual_precip_mm.ravel()),
		'toa_solar_flux_Wpm2':[toa_solar_flux_Wpm2]*len(annual_precip_mm.ravel()),
		'mean_solar_flux_Wpm2':mean_solar_flux_Wpm2.ravel(),
		'altitude_m':altitude_m.ravel(),
		'mean_temp_C':mean_temp_C.ravel(),
		'temp_var_C':temp_var_C.ravel(),
		'annual_precip_mm':annual_precip_mm.ravel(),
		'exoplanet':[exoplanet]*len(annual_precip_mm.ravel()),
		'biome':calculated_biomes.ravel(),
	})
	data_table.dropna(inplace=True)
	print(data_table)
	fpath = path.join(data_dir, "Earth_ref_table.csv")
	data_table.to_csv(fpath)
	gzip_file(fpath)
	print('...Done!')


def imshow(img: ndarray, title=None, range=None, cmap='gist_rainbow', shadow_img=None):
	if range is None:
		range = (numpy.nanmin(img), numpy.nanmax(img))
	if shadow_img is None:
		pyplot.imshow(numpy.clip(img, range[0], range[1]), alpha=1, cmap=cmap)
	else:
		pyplot.imshow(shadow_img, alpha=1, cmap='gist_gray')
		pyplot.imshow(numpy.clip(img, range[0], range[1]), alpha=0.5, cmap=cmap)
	pyplot.gca().invert_yaxis()
	if title is not None:
		pyplot.title(title)

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

def gzip_file(filepath):
	out_file = str(filepath)+'.gz'
	print('Compressing %s to %s...' % (filepath, out_file), end='')
	with gzip.open(out_file, 'wb') as fout:
		with open(filepath, 'rb') as fin:
			fout.write(fin.read())
	print('...done')
##########
if __name__ == '__main__':
	main()