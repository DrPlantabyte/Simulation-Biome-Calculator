import os, shutil, sys, re, numpy, pandas, json, pickle, time, gzip
from os import path
from subprocess import call
from PIL import Image
from numpy import ndarray, nan, uint8, float32, logical_and, logical_or, logical_not, clip, sin, cos, square, sqrt, power, log10
from pandas import DataFrame
### cython import ###
import pyximport
pyximport.install()
from biome_classifier_model import classify_planet_biomes
#

def main():
	PATCH_SOLAR_FLUX = False
	##
	data_dir = 'data'
	##
	gravity_m_per_s2 = 9.81
	mean_surface_pressure_kPa = 101.3
	toa_solar_flux_Wpm2 = 1373
	mean_solar_flux_Wpm2 = zunpickle(path.join(data_dir, 'solar_flux_1852m_singrid.pickle.gz'))
	altitude_m = zunpickle(path.join(data_dir, 'altitude_1852m_singrid.pickle.gz'))
	mean_temp_C = zunpickle(path.join(data_dir, 'surf_temp_mean_1852m_singrid.pickle.gz'))
	temp_var_C = zunpickle(path.join(data_dir, 'surf_temp_var_1852m_singrid.pickle.gz'))
	annual_precip_mm = zunpickle(path.join(data_dir, 'precip_mean_1852m_singrid.pickle.gz'))
	original_biomes = zunpickle(path.join(data_dir, 'drp_biomes_1852m_singrid.pickle.gz'))
	exoplanet = True
	if PATCH_SOLAR_FLUX:
		# had accidentally used pi/2 instead of 2/pi
		two_over_pi = 2 / numpy.pi
		pi_over_2 = 0.5 * numpy.pi
		mean_solar_flux_Wpm2 = mean_solar_flux_Wpm2 / pi_over_2 * two_over_pi
	##


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