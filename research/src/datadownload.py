#!/usr/bin/python3.9

import os, shutil, sys, re, requests, base64, urllib.parse, numpy, pandas, json, pickle, ssl, time
import gzip, h5py
from os import path
from zipfile import ZipFile
from modis_tools.auth import ModisSession
from modis_tools.resources import CollectionApi, GranuleApi
from modis_tools.granule_handler import GranuleHandler
from osgeo import gdal
from numpy import ndarray, nan, float32
from pandas import DataFrame
from matplotlib import pyplot
from datetime import datetime, timedelta

def main():
	print("Starting %s..." % sys.argv[0])
	# find and download data
	data_dir = 'data'
	secrets = pandas.read_csv('../secrets/pw.csv')
	username = secrets['username'][0] #input('Earth Data Username: ')
	password = secrets['password'][0] #input('Earth Data Password: ')

	# desired products:
	## Altitude and Ocean Depth - GEBCO_2021
	## Terrestrial LST - MOD11C3
	## Marine SST - AQUA_MODIS NSST
	## Global precipitation - GPM IMERG
	## benthic/surface mean solar flux - calculated from solar intensity, latitude, axis tilt, and depth/atmosphere thickness

	# other data sources
	## seagrass meadow distribution - McKenzie et al 2020 The global distribution of seagrass meadows https://iopscience.iop.org/article/10.1088/1748-9326/ab7d06
	## kelp forest distribution - Jayathilake & Costello 2020 A modelled global distribution of the kelp biome https://doi.org/10.1016/j.biocon.2020.108815
	## coral reef distribution - https://pacificdata.org/data/dataset/global-distribution-of-coral-reefs

	# data resolution: 1.85 km square pixels (0.017 degrees, or 60 px/deg) on sine grid (21.6k x 10.8k pixel image)
	# with (0,0) at SW corner
	#     X(lat,lon) = 10,800*(1 + cos(lat)*sin(lon)))
	#     Y(lat,lon) = 5,400*(1 + sin(lat))
	#     lat(X,Y) = 90*((Y/5,400) - 1)
	#     lon(X,Y) = 180*((X/10,800) - 1)/cos(lat(X,Y))

	# IGBP land cover type map - https://modis-land.gsfc.nasa.gov/landcover.html
	## NOTE: MCD12Q1 is in sine grid tile mosaic (https://modis-land.gsfc.nasa.gov/MODLAND_grid.html)
	## with (0,0) being the NW corner (pos Y is south), with 463m (240 px/deg) resolution
	modis_igbp_picklepath = path.join(data_dir, 'MCQ12Q1_1852m_igbp.pickle.gz')
	modis_faolccs_picklepath = path.join(data_dir, 'MCQ12Q1_1852m_fao-lccs.pickle.gz')
	modis_faohydro_picklepath = path.join(data_dir, 'MCQ12Q1_1852m_fao-hydrology.pickle.gz')
	if not path.exists(modis_igbp_picklepath) or not path.exists(modis_faolccs_picklepath) or not path.exists(modis_faohydro_picklepath):
		modis_dir = path.join(data_dir, 'modis')
		os.makedirs(modis_dir, exist_ok=True)
		maps = retrieve_MODIS_500m_product(
			short_name='MCD12Q1', version='006', subset_indices=[0,5,7],
			start_date='2020-01-01', end_date='2020-12-31', dest_dirpath=modis_dir,
			username=username, password=password, dtype=numpy.uint8, nodata=255,
			downsample = 4, sample_strat = 'mode', delete_files = True,
			zpickle_file = None, retry_limit = 5, retry_delay = 10
		)
		igbp_map = numpy.flip(maps[0], axis=0)
		maps[0] = None # let the GC free up some memory
		fao_lccs_map = numpy.flip(maps[1], axis=0)
		maps[1] = None
		fao_hydro_map = numpy.flip(maps[2], axis=0)
		maps[2] = None
		del maps
		zpickle(igbp_map, modis_igbp_picklepath)
		zpickle(fao_lccs_map, modis_faolccs_picklepath)
		zpickle(fao_hydro_map, modis_faohydro_picklepath)
	else:
		igbp_map = zunpickle(modis_igbp_picklepath)
		fao_lccs_map = zunpickle(modis_faolccs_picklepath)
		fao_hydro_map = zunpickle(modis_faohydro_picklepath)
	print('igbp_map.shape == ', igbp_map.shape, ' dtype == ', igbp_map.dtype)
	print('fao_lccs_map.shape == ', fao_lccs_map.shape, ' dtype == ', fao_lccs_map.dtype)
	print('fao_hydro_map.shape == ', fao_hydro_map.shape, ' dtype == ', fao_hydro_map.dtype)
	del fao_lccs_map
	del fao_hydro_map
	sample = igbp_map[0::10, 0::10]
	del igbp_map
	imshow(numpy.ma.masked_array(sample, mask=sample > 17), cmap='gist_rainbow')


	# altitude - https://www.ngdc.noaa.gov/mgg/topo/gltiles.html
	## NOTE: GEBCO data is in mercator projection with y=0 at south pole, 240 pixels per degree
	alt_depth_zpickle_filepath = path.join(data_dir, 'altitude_1852m_singrid.pickle.gz')
	if not path.exists(alt_depth_zpickle_filepath):
		elevation_1852m_pickle = path.join(data_dir, 'GEBCO_elevation_1852m_mercator.pickle.gz')
		if not path.exists(elevation_1852m_pickle):
			x_dir = path.join(data_dir, 'gebco')
			alt_depth_src = path.join(x_dir, 'GEBCO_2021_sub_ice_topo.nc')
			if not path.exists(alt_depth_src):
				alt_n_depth_file = path.join(data_dir, 'gebco_2021.zip')
				if not path.exists(alt_n_depth_file):
					http_download(url='https://www.bodc.ac.uk/data/open_download/gebco/gebco_2021_sub_ice_topo/zip/', filepath=alt_n_depth_file)
				if path.exists(alt_n_depth_file):
					with ZipFile(alt_n_depth_file, 'r') as zipf:
						zipf.extractall(x_dir)
				else:
					raise Exception("Failed to retrieve GEBCO data")
			alt_depth_hdf = h5py.File(alt_depth_src, 'r')
			elevation_ds = alt_depth_hdf['elevation']
			# Note: elevation_ds.shape == (43200, 86400), y=0 is south pole, mercator projection
			#pyplot.imshow(elevation_ds[0::100,0::100]); pyplot.gca().invert_yaxis(); pyplot.show()
			#pyplot.imshow(mercator_to_singrid(elevation_ds[0::100, 0::100], nodata=nan, dtype=float32)); pyplot.gca().invert_yaxis(); pyplot.show()
			elevation_1852m_merc = sub_sample(elevation_ds, (10800, 21600), subsample_strat='mean')
			zpickle(elevation_1852m_merc, elevation_1852m_pickle)
		else:
			elevation_1852m_merc = zunpickle(elevation_1852m_pickle)
		altitude_1852m_singrid = mercator_to_singrid(elevation_1852m_merc, nodata=nan, dtype=float32, strat='mean')
		del elevation_1852m_merc
		zpickle(altitude_1852m_singrid, alt_depth_zpickle_filepath)
		del elevation_ds
		alt_depth_hdf.close()
		del alt_depth_hdf
	else:
		altitude_1852m_singrid = zunpickle(alt_depth_zpickle_filepath)

	print('altitude_1852m_singrid.shape == ',altitude_1852m_singrid.shape)
	imshow(altitude_1852m_singrid[0::10, 0::10], cmap='terrain')
	del altitude_1852m_singrid

	# pyplot.imshow(altitude_1852m_singrid[0::10, 0::10], alpha=1, cmap='terrain')
	# pyplot.imshow(numpy.ma.masked_array(sample, mask=sample > 17), alpha=0.35, cmap='gist_rainbow')
	# pyplot.gca().invert_yaxis(); pyplot.show()

	# temperature (C)
	surface_mean_temp_zp_path = path.join(data_dir, 'surf_temp_mean_1852m_singrid.pickle.gz')
	surface_variation_temp_zp_path = path.join(data_dir, 'surf_temp_var_1852m_singrid.pickle.gz')
	# variation = mean +/- 1.5 std dev
	if not path.exists(surface_mean_temp_zp_path):
		LST_zpickle = path.join(data_dir, 'LST_1852m_singrid.pickle.gz')
		LST_rng_zpickle = path.join(data_dir, 'LST_rng_1852m_singrid.pickle.gz')
		SST_zpickle = path.join(data_dir, 'SST_1852m_singrid.pickle.gz')
		SST_rng_zpickle = path.join(data_dir, 'SST_rng_1852m_singrid.pickle.gz')
		## LST
		if not path.exists(LST_zpickle) or not path.exists(LST_rng_zpickle):
			dl_dir = path.join(data_dir, 'MODIS_TERRA')
			os.makedirs(dl_dir, exist_ok=True)
			# MOD11A2(L3) is 8-day average LST at 928m resolution tiled sine grid
			# MOD11C1(L3) is daily LST at 0.05 degree (5km) resolution whole sine grid
			# https://lpdaac.usgs.gov/documents/715/MOD11_User_Guide_V61.pdf
			## remember, MODIS data has Y-axis flipped relative to our representation
			LST_mercator_zpickle = path.join(data_dir, 'LST_5km_mercator_singrid.pickle.gz')
			LST_mercator_rng_zpickle = path.join(data_dir, 'LST_variance_5km_mercator_singrid.pickle.gz')
			if not path.exists(LST_mercator_zpickle) or not path.exists(LST_mercator_rng_zpickle):
				std_aggregate = None
				for year in [2015]:
					data_saver = path.join(dl_dir, 'LST_stats_agg.pickle.gz')
					doy_saver = path.join(dl_dir, 'LST_doy.pickle.gz')
					if path.exists(doy_saver) and path.exists(data_saver):
						doy_start = int(zunpickle(doy_saver))
						std_aggregate = zunpickle(data_saver)
					else:
						doy_start = 1
					for doy in range(doy_start, 366):
						date = datetime(year=year, month=1, day=1) + timedelta(days=doy - 1)
						date_str = '%s-%s-%s' % (date.year, left_pad(date.month, '0', 2), left_pad(date.day, '0', 2))
						retries = 3
						while (retries := retries-1) > 0:
							try:
								lst_data: ndarray = numpy.flip(retrieve_MODIS_global_product(
									'MOD11C1', '006', subset_indices=[0],
									start_date=date_str, end_date=date_str,
									dest_dirpath=dl_dir, username=username, password=password,
									delete_files=doy > 3,
									dtype=numpy.float32, nodata=numpy.nan,
									retry_limit=5, retry_delay=10
								)[0], axis=0) - 273.15
								break
							except Exception as e:
								print(e, file=sys.stderr)
						lst_data: ndarray = numpy.ma.masked_array(lst_data, lst_data < -200).filled(nan)
						if std_aggregate is None:
							std_aggregate = streaming_std_dev_start(shape=lst_data.shape)
						std_aggregate = streaming_std_dev_update(std_aggregate, lst_data)
						zpickle(std_aggregate, data_saver)
						zpickle(doy+1, doy_saver)
						#imshow(lst_data)
				(mean, _variance, sampleVariance) = streaming_std_dev_finalize(std_aggregate)
				del _variance
				zpickle(mean, LST_mercator_zpickle)
				zpickle(sampleVariance, LST_mercator_rng_zpickle)
			else:
				mean = zunpickle(LST_mercator_zpickle)
				sampleVariance = zunpickle(LST_mercator_rng_zpickle)
			# imshow(mean[0::10, 0::10])
			# imshow(numpy.sqrt(sampleVariance)[0::10, 0::10])
			LST_1852m_singrid = mercator_to_singrid(
				up_sample(mean.astype(float32), (10800, 21600)),
				dtype=float32, nodata=-1
			)
			del mean
			LST_range_1852m_singrid = mercator_to_singrid(
				up_sample(1.5 * numpy.sqrt(sampleVariance.astype(float32)), (10800, 21600)),
				dtype=float32, nodata=-1
			)
			del sampleVariance
			zpickle(LST_1852m_singrid, LST_zpickle)
			zpickle(LST_range_1852m_singrid, LST_rng_zpickle)
		else:
			LST_1852m_singrid = zunpickle(LST_zpickle)
			LST_range_1852m_singrid = zunpickle(LST_rng_zpickle)
		imshow(LST_1852m_singrid[0::10, 0::10])
		imshow(LST_range_1852m_singrid[0::10, 0::10])

		## SST
		if not path.exists(SST_zpickle) or not path.exists(SST_rng_zpickle):
			SST_mercator_zpickle = path.join(data_dir, 'SST_4km_mercator_singrid.pickle.gz')
			SST_mercator_rng_zpickle = path.join(data_dir, 'SST_variance_4km_mercator_singrid.pickle.gz')
			# Using MODIS Aqua Level 3 SST Thermal IR  Daily 4km Daytime V2019.0
			# Sadly, it's not availble with the MODIS download tool, but it does appear to work with plain http
			# URL format: https://podaac-opendap.jpl.nasa.gov/opendap/allData/modis/L3/aqua/11um/v2019.0/4km/daily/YEAR/DOY/AQUA_MODIS.yyyymmdd.L3m.DAY.SST.sst.4km.nc
			if not path.exists(SST_mercator_zpickle) or not path.exists(SST_mercator_rng_zpickle):
				def SST_url(year, month, day):
					doy = left_pad((datetime(year=year, month=month, day=day) - datetime(year=year-1, month=12, day=31)).days, '0', 3)
					return 'https://podaac-opendap.jpl.nasa.gov/opendap/allData/modis/L3/aqua/11um/v2019.0/4km/daily/%s/%s/AQUA_MODIS.%s%s%s.L3m.DAY.SST.sst.4km.nc' % (
						year, doy, year, left_pad(month, '0', 2), left_pad(day, '0', 2)
					)
				dl_dir = path.join(data_dir, 'MODIS_AQUA')
				os.makedirs(dl_dir, exist_ok=True)
				std_aggregate = streaming_std_dev_start(shape=(4320, 8640))
				for year in [2015]:
					for doy in range(1,366):
						date = datetime(year=year, month=1, day=1)+timedelta(days=doy-1)
						url = SST_url(year, date.month, date.day)
						sst_file = path.join(dl_dir, 'SST_%s-%s-%s.nc' % (date.year, date.month, date.day))
						if not path.exists(sst_file):
							retries = 3
							while (retries := retries - 1) >= 0:
								try:
									http_download(url, sst_file)
									break
								except Exception as e:
									print(e, file=sys.stderr)
						sst_ds: gdal.Dataset = gdal.Open(sst_file)
						sst_index = 0
						scale = 0.0049999999
						sst_data = numpy.flip(extract_data_from_ds(sst_ds, sst_index, dtype=float32, nodata=nan), axis=0)
						sst_data = sst_data * scale
						sst_data = numpy.ma.masked_array(sst_data, mask=sst_data<-100).filled(nan)
						#imshow(sst_data[0::10, 0::10])
						std_aggregate = streaming_std_dev_update(std_aggregate, sst_data)
						del sst_data
						del sst_ds # <- so stupid that THIS is the way you close the file when using GDAL!
						if doy > 3:
							os.remove(sst_file) # delete to save HD space
				(mean, _variance, sampleVariance) = streaming_std_dev_finalize(std_aggregate)
				del _variance
				zpickle(mean, SST_mercator_zpickle)
				zpickle(sampleVariance, SST_mercator_rng_zpickle)
			else:
				mean = zunpickle(SST_mercator_zpickle)
				sampleVariance = zunpickle(SST_mercator_rng_zpickle)
			imshow(mean[0::10, 0::10])
			imshow(numpy.sqrt(sampleVariance)[0::10, 0::10])
			SST_1852m_singrid = mercator_to_singrid(
				up_sample(mean.astype(float32), (10800, 21600)),
				dtype=float32, nodata=-1
			)
			del mean
			SST_range_1852m_singrid = mercator_to_singrid(
				up_sample(1.5 * numpy.sqrt(sampleVariance.astype(float32)), (10800, 21600)),
				dtype=float32, nodata=-1
			)
			del sampleVariance
			zpickle(SST_1852m_singrid, SST_zpickle)
			zpickle(SST_range_1852m_singrid, SST_rng_zpickle)
		else:
			SST_1852m_singrid = zunpickle(SST_zpickle)
			SST_range_1852m_singrid = zunpickle(SST_rng_zpickle)
		imshow(SST_1852m_singrid[0::10, 0::10])
		imshow(SST_range_1852m_singrid[0::10, 0::10])
		mean_surface_temp = compose(LST_1852m_singrid, SST_1852m_singrid)
		del LST_1852m_singrid
		del SST_1852m_singrid
		zpickle(mean_surface_temp, surface_mean_temp_zp_path)
		variation_surface_temp = compose(LST_range_1852m_singrid, SST_range_1852m_singrid)
		del LST_range_1852m_singrid
		del SST_range_1852m_singrid
		zpickle(variation_surface_temp, surface_variation_temp_zp_path)
	else:
		mean_surface_temp = zunpickle(surface_mean_temp_zp_path)
		variation_surface_temp = zunpickle(surface_variation_temp_zp_path)
	imshow(mean_surface_temp[0::10, 0::10])
	imshow(variation_surface_temp[0::10, 0::10])
	del mean_surface_temp
	del variation_surface_temp

	# rainfall (mm/year)
	# variation = mean +/- 1.5 std dev
	## https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGDF_06/summary?keywords=%22IMERG%20final%22
	## requires you to add NASA GESDISC DATA ARCHIVE to your list of approved apps in EarthData
	annual_precip_mean_zp_path = path.join(data_dir, 'precip_mean_1852m_singrid.pickle.gz')
	annual_precip_variation_zp_path = path.join(data_dir, 'precip_var_1852m_singrid.pickle.gz')
	if path.exists(annual_precip_mean_zp_path) and path.exists(annual_precip_variation_zp_path):
		mean_annual_precip = zunpickle(annual_precip_mean_zp_path)
		range_annual_precip = zunpickle(annual_precip_variation_zp_path)
	else:
		dl_dir = path.join(data_dir, 'GPM-IMERG-final')
		os.makedirs(dl_dir, exist_ok=True)
		gpm_mean_zp = path.join(dl_dir, 'GPM_mean_annual_precip_0.1deg_mercator.pickle.gz')
		gpm_var_zp = path.join(dl_dir, 'GPM_variance_annual_precip_0.1deg_mercator.pickle.gz')
		if path.exists(gpm_mean_zp) and path.exists(gpm_var_zp):
			gpm_mean_merc = zunpickle(gpm_mean_zp)
			gpm_var_merc = zunpickle(gpm_var_zp)
		else:
			progress_pickle = path.join(dl_dir, 'GPM_progress_year_doy.pickle.gz')
			if path.exists(progress_pickle):
				(years, doy_start) = zunpickle(progress_pickle)
			else:
				(years, doy_start) = ([2015], 1)
				zpickle((years, doy_start), progress_pickle)
			std_aggregate = None
			data_saver = path.join(dl_dir, 'GPM_stats_agg.pickle.gz')
			if path.exists(data_saver):
				std_aggregate = zunpickle(data_saver)
			for y in range(0,len(years)):
				year = years[y]
				for doy in range(doy_start, 366):
					date = datetime(year=year, month=1, day=1) + timedelta(days=doy - 1)
					retries = 3
					while (retries := retries - 1) > 0:
						try:
							gpm_data: ndarray = download_GPM_final_product(
								year=date.year, month=date.month, day=date.day,
								dest_dirpath=dl_dir, username=username, password=password,
								delete_file=doy > 3
							)
							# imshow(gpm_data)
							break
						except Exception as e:
							print(e, file=sys.stderr)
							time.sleep(11)
					gpm_data: ndarray = numpy.ma.masked_array(gpm_data, mask=gpm_data < 0).filled(nan)
					# print('gpm_data.shape ==', gpm_data.shape)
					# NOTE: GPM data is (lon,lat), not (lat,lon)
					if std_aggregate is None:
						std_aggregate = streaming_std_dev_start(shape=gpm_data.shape)
					std_aggregate = streaming_std_dev_update(std_aggregate, gpm_data)
					zpickle(std_aggregate, data_saver)
					zpickle((years, doy+1), progress_pickle)
				zpickle((years[y+1:], 1), progress_pickle)
			(gpm_mean_merc, _variance, gpm_var_merc) = streaming_std_dev_finalize(std_aggregate)
			del _variance
			# imshow(gpm_mean_merc.T)
			# imshow(gpm_var_merc.T)
			zpickle(gpm_mean_merc, gpm_mean_zp)
			zpickle(gpm_var_merc, gpm_var_zp)
		mean_annual_precip = mercator_to_singrid(up_sample(
			365 * numpy.flip(gpm_mean_merc.T, axis=1), dst_shape=(10800, 21600)
		), dtype=float32, nodata=nan)
		del gpm_mean_merc
		zpickle(mean_annual_precip, annual_precip_mean_zp_path)
		range_annual_precip = mercator_to_singrid(up_sample(
			365 * 1.5 * numpy.sqrt(numpy.flip(gpm_var_merc.T, axis=1)), dst_shape=(10800, 21600)
		), dtype=float32, nodata=nan)
		del gpm_var_merc
		zpickle(range_annual_precip, annual_precip_variation_zp_path)
	print(numpy.nanmin(mean_annual_precip), '-', numpy.nanmax(mean_annual_precip))
	imshow(numpy.clip(mean_annual_precip[::10,::10], 0, 3000))
	imshow(numpy.clip(range_annual_precip[::10,::10], 0, 3000))
	del mean_annual_precip
	del range_annual_precip
	print("...Done!")

def patch_data(zpath):
	# fix screw-ups
	## flip X and correct units
	data = zunpickle(zpath)
	data = numpy.flip(data, axis=1) / 24
	zpickle(data, zpath)
	del data


def compose(primary: ndarray, secondary: ndarray) -> ndarray:
	mask = numpy.logical_not(numpy.isfinite(primary))
	return numpy.ma.masked_array(primary, mask=mask).filled(secondary)

def imshow(img: ndarray, cmap='gist_rainbow'):
	pyplot.imshow(img, alpha=1, cmap=cmap)
	pyplot.gca().invert_yaxis()
	pyplot.show()

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
		raise FileNotFoundError("file '%s' does not exist" % filepath)

def streaming_std_dev_start(shape, dtype=numpy.float64):
	count = numpy.zeros(shape, dtype=numpy.int32)
	mean = numpy.zeros(shape, dtype=dtype)
	M2 = numpy.zeros(shape, dtype=dtype)
	return (count, mean, M2)

def streaming_std_dev_update(existingAggregate, newValue):
	(count, mean, M2) = existingAggregate
	mask = numpy.logical_not(numpy.isfinite(newValue)) # use mask to avoid changing values where new-val is nan
	newValue = numpy.ma.masked_array(newValue, mask=mask)
	count = numpy.ma.masked_array(count, mask=mask)
	mean = numpy.ma.masked_array(mean, mask=mask)
	M2 = numpy.ma.masked_array(M2, mask=mask)
	count += 1
	delta = newValue - mean
	mean += delta / count
	delta2 = newValue - mean
	M2 += delta * delta2
	return (numpy.asarray(count), numpy.asarray(mean), numpy.asarray(M2))

def streaming_std_dev_finalize(existingAggregate):
	(count, mean, M2) = existingAggregate
	mask = count < 2
	mean_mask = count <= 0
	c = numpy.ma.masked_array(count, mask=mask, dtype=float32).filled(nan)
	(mean, variance, sampleVariance) = (mean, M2 / c, M2 / (c - 1))
	return (numpy.ma.masked_array(mean, mask=mean_mask).filled(nan), variance, sampleVariance)

def lat_lon_to_singrid_YX(lat_lon, height_width):
	# X(lat,lon) = (w/2)*(1 + cos(lat)*sin(lon))
	# Y(lat,lon) = (h/2)*(1 + sin(lat))
	# lat(X,Y) = 90*((Y/(h/2)) - 1)
	# lon(X,Y) = 180*((X/(w/2)) - 1)/cos(lat(X,Y))
	deg2rad = numpy.pi/180
	lat = lat_lon[0]
	lon = lat_lon[1]
	h = height_width[0]
	w = height_width[1]
	y = int((lat + 90) * h / 180)
	circ = w * numpy.cos(lat * deg2rad)
	dx = int((lon + 180) * circ / 360)
	left_margin = int((w-circ)/2)
	x = left_margin + dx
	return numpy.asarray([y,x])


	half_width = 0.5*height_width[1]
	half_height = 0.5*height_width[0]
	x = half_width * (1 + numpy.cos(lat * deg2rad)*numpy.sin(lon * deg2rad))
	y = half_height * (1 + numpy.sin(lat))
	return numpy.asarray([int(y),int(x)])


def up_sample(src: ndarray, dst_shape) -> ndarray:
	# increase number of pixels
	cols = numpy.arange(dst_shape[1]) * src.shape[1] // dst_shape[1]
	rows = numpy.arange(dst_shape[0]) * src.shape[0] // dst_shape[0]
	output = src.take(numpy.outer(rows,src.shape[1]) + cols)
	return output

def sub_sample(src: ndarray, dst_shape, subsample_strat='mean') -> ndarray:
	if not (subsample_strat == 'mean' or subsample_strat == 'median' or subsample_strat == 'mode' or subsample_strat == 'nearest'):
		raise Exception(
			'Sub-sampling strategy subsample_strat = "%s" not supported. Must be one of: mean, median, mode, nearest' % subsample_strat)
	if subsample_strat == 'mean':
		def sample(src_data: ndarray, src_x: int, src_y: int, ssize_x: int, ssize_y: int, dest_data: ndarray, dest_x: int, dest_y: int):
			dest_data[dest_y][dest_x] = numpy.nanmean(src_data[src_y:src_y + ssize_y, src_x:src_x + ssize_x])
	elif subsample_strat == 'median':
		def sample(src_data: ndarray, src_x: int, src_y: int, ssize_x: int, ssize_y: int, dest_data: ndarray, dest_x: int, dest_y: int):
			dest_data[dest_y][dest_x] = numpy.nanmedian(src_data[src_y:src_y + ssize_y, src_x:src_x + ssize_x])
	elif subsample_strat == 'mode':
		def sample(src_data: ndarray, src_x: int, src_y: int, ssize_x: int, ssize_y: int, dest_data: ndarray, dest_x: int, dest_y: int):
			vals, counts = numpy.unique(src_data[src_y:src_y + ssize_y, src_x:src_x + ssize_x], return_counts=True)
			_mode = vals[numpy.argmax(counts)]
			dest_data[dest_y][dest_x] = _mode
	else:  # nearest
		def sample(src_data: ndarray, src_x: int, src_y: int, size_x: int, ssize_y: int, dest_data: ndarray, dest_x: int, dest_y: int):
			dest_data[dest_y][dest_x] = src_data[src_y][src_x]
	dst = numpy.ones(dst_shape, dtype=src.dtype)
	for dest_y in range(0, dst_shape[0]):
		src_y = int(src.shape[0] * dest_y / dst_shape[0])
		ss_y = int(src.shape[0] / dst_shape[0])
		for dest_x in range(0, dst_shape[1]):
			src_x = int(src.shape[1] * dest_x / dst_shape[1])
			ss_x = int(src.shape[1] / dst_shape[1])
			sample(src, src_x, src_y, ss_x, ss_y, dst, dest_x, dest_y)
	return dst

def mercator_to_singrid(merc: ndarray, dtype=None, nodata=-1, strat='mean') -> ndarray:
	if not (strat == 'mean' or strat == 'median' or strat == 'mode' or strat == 'nearest'):
		raise Exception(
			'Sub-sampling strategy strat = "%s" not supported. Must be one of: mean, median, mode, nearest' % strat)
	if strat == 'mean':
		def combine(sector: ndarray):
			return numpy.nanmean(sector)
	elif strat == 'median':
		def combine(sector: ndarray):
			return numpy.nanmedian(sector)
	elif strat == 'mode':
		def combine(sector: ndarray):
			vals, counts = numpy.unique(sector, return_counts=True)
			_mode = vals[numpy.argmax(counts)]
			return _mode
	if dtype is None:
		singrid = numpy.zeros_like(merc) + nodata
	else:
		singrid = numpy.zeros_like(merc, dtype=dtype) + nodata
	x_offset = merc.shape[1] / 2
	for src_y in range(merc.shape[0]):
		dst_y = src_y
		lat_rad = ((src_y / (merc.shape[0])) - 0.5) * numpy.pi
		cos_lat = numpy.cos(lat_rad)
		circ = merc.shape[1] * cos_lat
		if cos_lat < 0.66667:
			## more source pixels than dest pixels
			chunks = (numpy.linspace(0,1, int(max(1, circ))+1)*merc.shape[1]).astype(numpy.int32)
			for i in range(0, len(chunks)-1):
				src_x_left = chunks[i]
				src_x_right = chunks[i+1]
				dst_x = int(x_offset - (circ/2) + i)
				singrid[dst_y][dst_x] = combine(merc[src_y][src_x_left:src_x_right])
		else:
			## roughly 1:1 srd to dest
			resample = (numpy.linspace(0,1,int(circ+0.5)-1)*(merc.shape[1]-1)).astype(numpy.int32)
			L_margin = int((singrid.shape[1]-len(resample))/2)
			singrid[dst_y][L_margin:L_margin+len(resample)] = merc[src_y].take(resample)
	return singrid



def download_landcover_for_year(year, http_session):
	download_URL = get_landcover_URL_for_year(year)
	#download_URL = 'https://e4ftl01.cr.usgs.gov//MODV6_Cmp_C/MOTA/MCD12C1.006/2018.01.01/MCD12C1.A2018001.006.2019200161458.hdf'
	local_filename = path.join('data', 'landcover-%s.hdf' % year)
	print('Downloading %s to %s...' % (download_URL, local_filename))
	with http_session.get(download_URL, stream=True) as r:
		print('download status code: ', r.status_code)
		r.raise_for_status()
		with open(local_filename, 'wb') as f:
			for chunk in r.iter_content(chunk_size=2**20):
				f.write(chunk)
				print('.')
	print('...Download complete!')


def retrieve_MODIS_global_product(
		short_name, version, subset_indices, start_date, end_date,
		dest_dirpath, username, password,
		delete_files=False,
		dtype=numpy.float32, nodata=numpy.nan,
		retry_limit=5, retry_delay=10
):
	## NOTE: y=0 is north, positive y is south direction, x=0 is west, positive x is east direction
	## NOTE: ndarray dimension order = data[y][x]
	output_maps: [ndarray] = []

	os.makedirs(dest_dirpath, exist_ok=True)
	modis_session = ModisSession(username=username, password=password)
	# Query the MODIS catalog for collections
	collection_client = CollectionApi(session=modis_session)
	collections = collection_client.query(short_name=short_name, version=version)
	granule_client = GranuleApi.from_collection(collections[0], session=modis_session)
	granules = granule_client.query(start_date=start_date, end_date=end_date)
	print('Downloading %s from %s to %s to data directory %s...' % (short_name, start_date, end_date, dest_dirpath))
	for g in granules:
		# print('links:')
		# for L in g.links:
		# 	print('\t',L.href)
		filename = g.links[0].href[g.links[0].href.rfind('/')+1:]
		print('\t','downloading ',filename)
		filepath=path.join(dest_dirpath, filename)
		if not path.exists(filepath):
			for attempt in range(0, retry_limit):
				try:
					GranuleHandler.download_from_granules(g, modis_session, path=dest_dirpath)
				except ssl.SSLEOFError as e:
					print('SSL error while communicating with server:', e, file=sys.stderr)
					if attempt < retry_limit-1:
						print('Retrying in %s seconds...' % retry_delay, file=sys.stderr)
						time.sleep(retry_delay)
				else:
					break

		if not path.exists(filepath):
			print('failed to download %s' % filename)
			exit(1)
		ds: gdal.Dataset = gdal.Open(filepath)
		#print_modis_structure(ds)
		row=[]
		for i in range(0,len(subset_indices)):
			subset_index = subset_indices[i]
			tile_ds: gdal.Dataset = gdal.Open(ds.GetSubDatasets()[subset_index][0])
			tile_meta: {} = tile_ds.GetMetadata_Dict()
			del tile_ds
			json_fp = path.join(dest_dirpath, '%s_%s_subset-%s.json' % (short_name, version, subset_index))
			tile_data = extract_data_from_ds(ds, subset_index, metadata_filepath=json_fp, dtype=dtype, nodata=nodata)
			if len(subset_indices) == 1:
				output_maps.append(tile_data)
			else:
				row.append(tile_data)
			del tile_data
			del tile_meta
			#
		if len(subset_indices) > 1:
			output_maps.append(row)
		## clean-up to conserve memory and resources for next iteration
		del ds
		if delete_files:
			os.remove(filepath)
			print('\t','extraction complete, file deleted.')
	#GranuleHandler.download_from_granules(granules, modis_session, path='data')
	print('...Download complete!')
	return output_maps

def retrieve_MODIS_500m_product(short_name, version, subset_indices, start_date, end_date, dest_dirpath, username, password,
								downsample: int = 10, sample_strat='mean', delete_files=False,
								dtype=numpy.float32, nodata=numpy.nan,
								zpickle_file=None, retry_limit=5, retry_delay=10):
	## NOTE: MODIS tile grid explained at https://modis-land.gsfc.nasa.gov/MODLAND_grid.html
	if zpickle_file is not None and path.exists(zpickle_file):
		print('%s already exists. Skipping download.' % zpickle_file)
		return zunpickle(zpickle_file)
	MODIS_grid_hori_count = 36
	MODIS_grid_vert_count = 18
	tile_size = 2400

	sample_strat = sample_strat.lower()
	if not(sample_strat == 'mean' or sample_strat == 'median' or sample_strat == 'mode' or sample_strat == 'nearest'):
		raise Exception('Sub-sampling strategy sample_strat = "%s" not supported. Must be one of: mean, median, mode, nearest' % sample_strat)

	## subsample to output array
	if sample_strat == 'mean':
		def sample(src_data: ndarray, src_x: int, src_y: int, ssize: int, dest_data: ndarray, dest_x: int, dest_y: int):
			dest_data[dest_y][dest_x] = numpy.nan_to_num(numpy.nanmean(src_data[src_y:src_y + ssize, src_x:src_x + ssize]), nan=nodata).astype(dtype)
	elif sample_strat == 'median':
		def sample(src_data: ndarray, src_x: int, src_y: int, ssize: int, dest_data: ndarray, dest_x: int, dest_y: int):
			dest_data[dest_y][dest_x] = numpy.nan_to_num(numpy.nanmedian(src_data[src_y:src_y + ssize, src_x:src_x + ssize]), nan=nodata).astype(dtype)
	elif sample_strat == 'mode':
		def sample(src_data: ndarray, src_x: int, src_y: int, ssize: int, dest_data: ndarray, dest_x: int, dest_y: int):
			vals, counts = numpy.unique(src_data[src_y:src_y + ssize, src_x:src_x + ssize], return_counts=True)
			_mode = numpy.asarray(vals[numpy.argmax(counts)])
			dest_data[dest_y][dest_x] = numpy.nan_to_num(_mode, nan=nodata).astype(dtype)
	else:  # nearest
		def sample(src_data: ndarray, src_x: int, src_y: int, ssize: int, dest_data: ndarray, dest_x: int, dest_y: int):
			dest_data[dest_y][dest_x] = numpy.nan_to_num(src_data[src_y][src_x], nan=nodata).astype(dtype)

	downsample = int(downsample)
	if downsample < 1: raise Exception('downsample must be a positive integer');

	## NOTE: y=0 is north, positive y is south direction, x=0 is west, positive x is east direction
	## NOTE: ndarray dimension order = data[y][x]
	w=int(tile_size * MODIS_grid_hori_count / downsample)
	h=int(tile_size * MODIS_grid_vert_count / downsample)
	output_maps: [ndarray] = []
	for _ in subset_indices:
		output_maps.append(numpy.ones((h, w), dtype=dtype) * nodata)

	os.makedirs(dest_dirpath, exist_ok=True)
	modis_session = ModisSession(username=username, password=password)
	# Query the MODIS catalog for collections
	collection_client = CollectionApi(session=modis_session)
	collections = collection_client.query(short_name=short_name, version=version)
	granule_client = GranuleApi.from_collection(collections[0], session=modis_session)
	granules = granule_client.query(start_date=start_date, end_date=end_date)
	print('Downloading %s from %s to %s to data directory %s...' % (short_name, start_date, end_date, dest_dirpath))
	for g in granules:
		# print('links:')
		# for L in g.links:
		# 	print('\t',L.href)
		filename = g.links[0].href[g.links[0].href.rfind('/')+1:]
		print('\t','downloading ',filename)
		filepath=path.join(dest_dirpath, filename)
		if not path.exists(filepath):
			for attempt in range(0, retry_limit):
				try:
					GranuleHandler.download_from_granules(g, modis_session, path=dest_dirpath)
				except ssl.SSLEOFError as e:
					print('SSL error while communicating with server:', e, file=sys.stderr)
					if attempt < retry_limit-1:
						print('Retrying in %s seconds...' % retry_delay, file=sys.stderr)
						time.sleep(retry_delay)
				else:
					break

		if not path.exists(filepath):
			print('failed to download %s' % filename)
			exit(1)
		ds: gdal.Dataset = gdal.Open(filepath)
		#print_modis_structure(ds)
		for i in range(0,len(subset_indices)):
			subset_index = subset_indices[i]
			output_map = output_maps[i]
			tile_ds: gdal.Dataset = gdal.Open(ds.GetSubDatasets()[subset_index][0])
			tile_meta: {} = tile_ds.GetMetadata_Dict()
			del tile_ds
			json_fp = path.join(dest_dirpath, '%s_%s_subset-%s.json' % (short_name, version, subset_index))
			tile_hori_pos = int(tile_meta['HORIZONTALTILENUMBER'])
			tile_vert_pos = int(tile_meta['VERTICALTILENUMBER'])
			tile_data = extract_data_from_ds(ds, subset_index, metadata_filepath=json_fp)
			#print('Data shape:',tile_data.shape)
			# pyplot.imshow(tile_data, aspect='auto')
			# pyplot.show()
			for y in range(0, tile_size, downsample):
				dest_y = int((tile_size * tile_vert_pos + y) / downsample)
				for x in range(0, tile_size, downsample):
					dest_x = int((tile_size * tile_hori_pos + x) / downsample)
					#if dest_x == output_map.shape[1]: print('(tile_size, tile_vert_pos, tile_hori_pos, downsample, x, y, dest_x, dest_y)',(tile_size, tile_vert_pos, tile_hori_pos, downsample, x, y, dest_x, dest_y));
					sample(tile_data, x, y, downsample, output_map, dest_x, dest_y)
			#
		## clean-up to conserve memory and resources for next iteration
		del tile_data
		del tile_meta
		del ds
		if delete_files:
			os.remove(filepath)
			print('\t','extraction complete, file deleted.')
	#GranuleHandler.download_from_granules(granules, modis_session, path='data')
	print('...Download complete!')
	if zpickle_file is not None:
		if len(subset_indices > 1):
			for subset_index in subset_indices:
				suffix = str(zpickle_file)[str(zpickle_file).rfind("."):]
				zf = zpickle_file.replace(suffix, '_%s%s' % (subset_index, suffix))
				zpickle(output_maps[0], zf)
				print('Saved %s' % zpickle_file)
		else:
			zpickle(output_maps[0], zpickle_file)
			print('Saved %s' % zpickle_file)
	return output_maps

def extract_data_from_ds(ds: gdal.Dataset, subset_index: int, valid_range=(-numpy.inf, numpy.inf), dtype=numpy.float32, nodata=numpy.nan, metadata_filepath=None) -> ndarray:
	tile_ds: gdal.Dataset = gdal.Open(ds.GetSubDatasets()[subset_index][0])
	tile_meta: {} = tile_ds.GetMetadata_Dict()
	if metadata_filepath is not None:
		json_fp = metadata_filepath
		if not path.exists(json_fp):
			with open(json_fp, 'w') as fout:
				print('\t', 'writing meta data to', json_fp)
				json.dump(tile_meta, fout, indent='  ')
	if 'scale_factor' in tile_meta:
		scale_factor = float(tile_meta['scale_factor'])
	else:
		scale_factor = 1
	if valid_range is None:
		if 'valid_range' in tile_meta:
			valid_range = [float(n) for n in tile_meta['valid_range'].split(', ')]
		else:
			valid_range = [-numpy.inf, numpy.inf]
	tile_data_raw: ndarray = tile_ds.ReadAsArray()
	## mask and scale
	tile_data = numpy.ma.array(
		tile_data_raw,
		mask=numpy.logical_or(tile_data_raw < valid_range[0],tile_data_raw > valid_range[1])
	).astype(dtype).filled(nodata) * scale_factor
	del tile_data_raw
	del tile_ds
	return tile_data


def print_modis_structure(dataset: gdal.Dataset):
	metadata_dict = dict(dataset.GetMetadata_Dict())
	metadata_dict['Subsets'] = dataset.GetSubDatasets()
	print(dataset.GetDescription(), json.dumps(metadata_dict, indent="  "))


def download_GPM_final_product(year, month, day, dest_dirpath, username, password, delete_file=False, dtype=float32, nodata=nan):
	# wget --load-cookies /.urs_cookies --save-cookies /root/.urs_cookies --auth-no-challenge=on --user=your_user_name --ask-password --content-disposition -i <url text file>
	http_session = requests.session()
	src_url = 'https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGDF.06/%s/%s/3B-DAY.MS.MRG.3IMERG.%s%s%s-S000000-E235959.V06.nc4' % (
			year, left_pad(month, '0', 2), year, left_pad(month, '0', 2), left_pad(day, '0', 2)
	)
	http_session.auth = (username, password)
	# note: URL gets redirected
	redirect = http_session.request('get', src_url)
	filename = src_url.split('/')[-1]
	dest_filepath = path.join(dest_dirpath, filename)
	# NOTE the stream=True parameter below
	print('Downloading %s to %s...' % (redirect.url, dest_filepath))
	with http_session.get(redirect.url, auth=(username, password), stream=True) as r:
		r.raise_for_status()
		with open(dest_filepath, 'wb') as f:
			for chunk in r.iter_content(chunk_size=1048576):
				f.write(chunk)
	print('...Download complete!')
	gpm_ds = gdal.Open(dest_filepath)
	gpm_data = extract_data_from_ds(gpm_ds, subset_index=0, dtype=dtype, nodata=nodata)
	del gpm_ds
	if delete_file:
		os.remove(dest_filepath)
		print('\t','extraction complete, file deleted.')
	return gpm_data


def http_download(url, filepath, show_dots=False):
	print('Downloading %s to %s...' % (url, filepath))
	http_session = requests.session()
	with http_session.get(url, stream=True) as r:
		print('download status code: ', r.status_code)
		r.raise_for_status()
		with open(filepath, 'wb') as f:
			for chunk in r.iter_content(chunk_size=2 ** 20): # 1 MB chunks
				f.write(chunk)
				if show_dots:
					print('.', end='')
		print()
	print('...Download complete!')


def get_landcover_URL_for_year(year):
	html = requests.get('https://e4ftl01.cr.usgs.gov/MOTA/MCD12C1.006/%s.01.01/' % year).content.decode('UTF-8')
	filename = re.findall('MCD12C1.*?\\.hdf', html)[0]
	return 'https://e4ftl01.cr.usgs.gov/MOTA/MCD12C1.006/%s.01.01/%s' % (year, filename)

def left_pad(t, p, n):
	s = str(t)
	while len(s) < int(n):
		s = str(p) + s
	return s

if __name__ == '__main__':
	main()