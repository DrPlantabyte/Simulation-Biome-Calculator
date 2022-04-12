import os, shutil, sys, re, requests, base64, urllib.parse, numpy, pandas, json, pickle, ssl, time, gzip
from os import path
from numpy import ndarray, nan, uint8, float32, logical_and, logical_or, clip, sin, cos
from pandas import DataFrame
from matplotlib import pyplot

## This script preporcesses the downloaded data into training and testing data

# see https://lpdaac.usgs.gov/documents/101/MCD12_User_Guide_V6.pdf for biome codes

## biome codes
from landcover_codes import *
from biome_enum import Biome

def main():
	data_dir = 'data'
	shape_1852m = (10800, 21600)
	## gzipped pickles of downloaded data
	igbp_zpickle = path.join(data_dir, 'MCQ12Q1_1852m_igbp.pickle.gz')
	fao_lccs1_zpickle = path.join(data_dir, 'MCQ12Q1_1852m_fao-lccs.pickle.gz')
	fao_hydro_zpickle = path.join(data_dir, 'MCQ12Q1_1852m_fao-hydrology.pickle.gz')
	altitude_zpickle = path.join(data_dir, 'altitude_1852m_singrid.pickle.gz')
	surface_temp_mean_zpickle = path.join(data_dir, 'surf_temp_mean_1852m_singrid.pickle.gz')
	surface_temp_variation_zpickle = path.join(data_dir, 'surf_temp_var_1852m_singrid.pickle.gz')
	annual_precip_mean_zpickle = path.join(data_dir, 'precip_mean_1852m_singrid.pickle.gz')
	annual_precip_variation_zpickle = path.join(data_dir, 'precip_var_1852m_singrid.pickle.gz')

	##
	altitude = zunpickle(altitude_zpickle)
	imshow(numpy.clip(altitude[::10,::10], -200, 3000), 'altitude', cmap='terrain')
	surface_temp_mean = zunpickle(surface_temp_mean_zpickle)
	imshow(numpy.clip(surface_temp_mean[::10,::10], 0, 50), 'surface temperature')

	print('Converting biomes...')
	# convert to DrPlantabyte biomes
	drplantabyte_biomes = numpy.zeros(shape_1852m, dtype=numpy.uint8)
	igbp = zunpickle(igbp_zpickle)
	fao_hydro = zunpickle(fao_hydro_zpickle)
	##### TERRESTRIAL BIOMES #####
	## wetland
	mask = logical_or(
		igbp == IGBP_PERMANENT_WETLAND,
		logical_or(fao_hydro == FAO_HYDRO_HERBACEOUS_WETLANDS, fao_hydro == FAO_HYDRO_WOODY_WETLANDS)
	)
	drplantabyte_biomes += Biome.WETLAND.value * mask_to_binary(logical_and(mask, drplantabyte_biomes == 0))
	## jungle
	mask = igbp == IGBP_EVERGREEN_BROADLEAF_FOREST
	drplantabyte_biomes += Biome.JUNGLE.value * mask_to_binary(logical_and(mask, drplantabyte_biomes == 0))
	## seasonal forest
	mask = logical_or(
		igbp == IGBP_DECIDUOUS_BROADLEAF_FOREST,
		logical_or(igbp == IGBP_DECIDUOUS_NEEDLELEAF_FOREST, igbp == IGBP_MIXED_FOREST)
	)
	drplantabyte_biomes += Biome.SEASONAL_FOREST.value * mask_to_binary(logical_and(mask, drplantabyte_biomes == 0))
	## needle-leaf/taiga forest
	mask = igbp == IGBP_EVERGREEN_NEEDLELEAF_FOREST
	drplantabyte_biomes += Biome.NEEDLELEAF_FOREST.value * mask_to_binary(logical_and(mask, drplantabyte_biomes == 0))
	## grassland and savannahs
	mask = logical_or(
		igbp == IGBP_GRASSLAND,
		logical_or(igbp == IGBP_SAVANNA, igbp == IGBP_WOODY_SAVANNA)
	)
	drplantabyte_biomes += Biome.GRASSLAND.value * mask_to_binary(logical_and(mask, drplantabyte_biomes == 0))
	## deserts and dry shrublands
	mask = logical_or(igbp == IGBP_OPEN_SHRUBLAND, igbp == IGBP_CLOSED_SHRUBLAND)
	drplantabyte_biomes += Biome.DESERT_SHRUBLAND.value * mask_to_binary(logical_and(mask, drplantabyte_biomes == 0))
	## sand sea & barren
	### sand dunes are all between latitude 49 N and 28S, so just going to declare barrens within that sand dunes and
	### everythong else not sand dunes
	mask2 = numpy.zeros_like(drplantabyte_biomes)
	mask2[int((90-28)*drplantabyte_biomes.shape[0]/180):int((90+49)*drplantabyte_biomes.shape[0]/180),:] = 1
	mask = logical_and(mask2 == 1, igbp == IGBP_BARREN)
	drplantabyte_biomes += Biome.SAND_SEA.value * mask_to_binary(logical_and(mask, drplantabyte_biomes == 0))
	mask = logical_and(mask2 == 0, igbp == IGBP_BARREN)
	drplantabyte_biomes += Biome.BARREN.value * mask_to_binary(logical_and(mask, drplantabyte_biomes == 0))
	del mask2
	## ice sheet
	mask = logical_or(
		igbp == IGBP_SNOW_AND_ICE, fao_hydro == FAO_HYDRO_PERMANENT_SNOW_AND_ICE
	)
	drplantabyte_biomes += Biome.ICE_SHEET.value * mask_to_binary(logical_and(mask, drplantabyte_biomes == 0))
	## artificial biomes
	mask = logical_or(igbp == IGBP_CROPLAND, igbp == IGBP_CROPLAND_NATURAL_VEGETATION_MOSAICS)
	drplantabyte_biomes += Biome.FARMLAND.value * mask_to_binary(logical_and(mask, drplantabyte_biomes == 0))
	mask = igbp == IGBP_URBAN_AND_BUILT_UP_LANDSCAPE
	drplantabyte_biomes += Biome.URBAN.value * mask_to_binary(logical_and(mask, drplantabyte_biomes == 0))
	##### AQUATIC BIOMES #####
	## fresh water
	mask = logical_and(
		altitude > 0,
		logical_or(igbp == IGBP_WATER_BODIES, fao_hydro == FAO_HYDRO_WATER_BODIES)
	)
	drplantabyte_biomes += Biome.FRESHWATER.value * mask_to_binary(logical_and(mask, drplantabyte_biomes == 0))
	### the next bit is a little fuzzy, as no decent global distribution maps exist for sea grasses or kelp forests or corals
	## sea forest
	mask = logical_and(
		logical_and(altitude > -90, altitude < -6),
		logical_and(surface_temp_mean > 5, surface_temp_mean < 20)
	)
	drplantabyte_biomes += Biome.SEA_FOREST.value * mask_to_binary(logical_and(mask, drplantabyte_biomes == 0))
	## tropical reef
	mask = logical_and(
		logical_and(altitude > -90, altitude < 0),
		logical_and(surface_temp_mean >= 20, surface_temp_mean < 30)
	)
	drplantabyte_biomes += Biome.TROPICAL_REEF.value * mask_to_binary(logical_and(mask, drplantabyte_biomes == 0))
	## fill the remaining shallows with rocky shores
	mask = logical_and(altitude > -90, altitude < 0)
	drplantabyte_biomes += Biome.ROCKY_SHALLOWS.value * mask_to_binary(logical_and(mask, drplantabyte_biomes == 0))
	## shallow ocean areas
	mask = logical_and(altitude >= -200, altitude <= -90)
	drplantabyte_biomes += Biome.SHALLOW_OCEAN.value * mask_to_binary(logical_and(mask, drplantabyte_biomes == 0))
	## fill the rest with  deepocean
	mask = altitude < -200
	drplantabyte_biomes += Biome.DEEP_OCEAN.value * mask_to_binary(logical_and(mask, drplantabyte_biomes == 0))
	#### done!
	del mask
	print('...Biomes converted!')
	##### finished with biomes #####
	imshow(drplantabyte_biomes, 'Biomes', cmap='prism')
	del igbp; del fao_hydro
	surface_temp_range = zunpickle(surface_temp_variation_zpickle)
	precip_mean = zunpickle(annual_precip_mean_zpickle)

	# prepare fearures and labels
	feature_names = 'gravity;annual-mean-solar-flux;pressure;altitude;annual-mean-temperature;annual-range-temperature;annual-mean-precip'.split(';')
	feature_units = 'm/s2;W/m2;kPa;m;C;+/-C;mm'.split(';')
	## make a small set first for quick testing
	small_drplantabyte_biomes = drplantabyte_biomes[::10, ::10]
	small_altitude = altitude[::10, ::10]
	small_temp_mean = surface_temp_mean[::10, ::10]
	small_temp_range = surface_temp_range[::10, ::10]
	small_precip = precip_mean[::10, ::10]
	## pressure
	sealevel_pressure = 101 # kPa
	small_pressure_kpa = pressure_at_altitude(101, small_altitude)
	## solar flux claculation
	### tidally locked: flux I = Imax * cos(lat) * cos(lon)
	### rotating but without tilt: flux I = Imax * 2/pi * cos(lat)
	### rotating but with tilt: flux I = Imax * 2/pi * 0.5 * (clip[cos(lat-tilt), 0-1] + clip[cos(lat+tilt), 0-1])
	deg2Rad = numpy.pi / 180.0
	two_over_pi = 2.0 / numpy.pi
	axis_tilt = 23
	max_solar_flux_TOA = 1373
	small_latitudes = latitudes_like(small_altitude)
	small_solar_flux = solar_flux_at_pressure(max_solar_flux_TOA * two_over_pi * 0.5 * (
		clip(cos(deg2Rad*(small_latitudes - axis_tilt)),0,1)
		+ clip(cos(deg2Rad*(small_latitudes + axis_tilt)),0,1)
	), small_pressure_kpa)



def mask_to_binary(m: ndarray) -> ndarray:
	return m.astype(uint8)

def latitudes_like(map: ndarray, dtype=numpy.float32) -> ndarray:
	col = 180 * numpy.arange(map.shape[0], dtype=dtype)/(map.shape[0]-1) - 90
	row = numpy.ones((map.shape[1],), dtype=dtype)
	return numpy.outer(col, row)

def pressure_at_altitude(sealevel_pressure_kPa, gravity_m_per_s2, mean_temp_C, altitude_m: ndarray) -> ndarray:
	# underwater
	water_density_kg = 1
	underwater = numpy.ma.masked_array(numpy.zeros_like(altitude_m), mask=altitude_m >= 0) \
		+ sealevel_pressure_kPa - gravity_m_per_s2 * altitude_m * water_density_kg
	# up in the atmosphere
	K = mean_temp_C + 273.15
	R = 8.314510  # j/K/mole
	air_molar_mass = 0.02897  # kg/mol
	above_water = sealevel_pressure_kPa * numpy.exp(-(air_molar_mass * gravity_m_per_s2 * altitude_m)/(R*K))
	return underwater.filled(above_water)

def solar_flux_at_altitude(top_of_atmosphere_flux, sealevel_pressure_kPa, gravity_m_per_s2, mean_temp_C, altitude_m: ndarray) -> ndarray:
	epsilon_air = 0.08464 # Absorption per 100 kPa
	epsilon_water =   # Absorption per meter (150m == 1% transmission (0.01 = 10^(-epsilon*150))
	return top_of_atmosphere_flux * numpy.power(10, -epsilon_air * surface_pressure_kPa)

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

def imshow(img: ndarray, title=None, cmap='gist_rainbow'):
	pyplot.imshow(img, alpha=1, cmap=cmap)
	pyplot.gca().invert_yaxis()
	if title is not None:
		pyplot.title(title)
	pyplot.show()

if __name__ == '__main__':
	main()