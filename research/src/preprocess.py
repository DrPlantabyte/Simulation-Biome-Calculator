import os, shutil, sys, re, requests, base64, urllib.parse, numpy, pandas, json, pickle, ssl, time, gzip
from os import path
from numpy import ndarray, nan, uint8, float32, logical_and, logical_or
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



def mask_to_binary(m: ndarray):
	return m.astype(uint8)

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