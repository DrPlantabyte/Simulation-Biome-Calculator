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
	pyplot.imshow(numpy.ma.masked_array(sample, mask=sample > 17), alpha=1, cmap='gist_rainbow'); pyplot.gca().invert_yaxis(); pyplot.show()


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
	pyplot.imshow(altitude_1852m_singrid[0::10, 0::10], alpha=1, cmap='terrain'); pyplot.gca().invert_yaxis(); pyplot.show()

	pyplot.imshow(altitude_1852m_singrid[0::10, 0::10], alpha=1, cmap='terrain')
	pyplot.imshow(numpy.ma.masked_array(sample, mask=sample > 17), alpha=0.35, cmap='gist_rainbow')
	pyplot.gca().invert_yaxis(); pyplot.show()

	surface_mean_temp_zp_path = path.join(data_dir, 'surf_temp_mean_1852m_singrid.pickle.gz')
	surface_range_temp_zp_path = path.join(data_dir, 'surf_temp_range_1852m_singrid.pickle.gz')
	if not path.exists(surface_mean_temp_zp_path):
		LST_zpickle = path.join(data_dir, 'LST_1852m_singrid.pickle.gz')
		SST_zpickle = path.join(data_dir, 'SST_1852m_singrid.pickle.gz')
		if not path.exists(LST_zpickle):
			## TODO: download and process LST
			LST_1852m_singrid = None
		else:
			LST_1852m_singrid = zunpickle(LST_zpickle)
		if not path.exists(SST_zpickle):
			## TODO: download and process SST
			SST_1852m_singrid = None
		else:
			SST_1852m_singrid = zunpickle(SST_zpickle)
		## TODO: merge LST and SST into global ST
		surface_temp = None
	else:
		surface_temp = zunpickle(surface_mean_temp_zp_path)

	exit(1)

	print("...Done!")

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
		return None

def lat_lon_to_singrid_XY(lat_lon, width_height):
	# X(lat,lon) = (w/2)*(1 + cos(lat)*sin(lon))
	# Y(lat,lon) = (h/2)*(1 + sin(lat))
	# lat(X,Y) = 90*((Y/(h/2)) - 1)
	# lon(X,Y) = 180*((X/(w/2)) - 1)/cos(lat(X,Y))
	half_width = 0.5*width_height[0]
	half_height = 0.5*width_height[1]
	lat = lat_lon[0]
	lon  = lat_lon[1]
	deg2rad = numpy.pi/180
	x = half_width * (1 + numpy.cos(lat * deg2rad)*numpy.sin(lon * deg2rad))
	y = half_height * (1 + numpy.sin(lat))
	return numpy.asarray([x,y])

def singrid_XY_to_lat_lon(XY, width_height):
	half_width = 0.5*width_height[0]
	half_height = 0.5*width_height[1]
	x = XY[0]
	y = XY[1]
	deg2rad = numpy.pi/180
	lat = 90*((y/half_height) - 1)
	lon = 180*((x/half_width) - 1)/numpy.cos(lat * deg2rad)
	return numpy.asarray([lat,lon])

def singrid_mask(width_height) -> ndarray:
	w = width_height[0]
	h = width_height[1]
	deg2rad = numpy.pi/180
	mask = numpy.zeros((h,w), dtype=numpy.bool)
	for row in range(0,h):
		lat, _ = singrid_XY_to_lat_lon((0,row),width_height=width_height)
		half_row_width = numpy.cos(lat * deg2rad)
		left = 0.5 - half_row_width
		right = 0.5 + half_row_width
		row_data = numpy.linspace(0,1,int(w))-0.5
		mask[row] = numpy.logical_and(row_data >= left, row_data <= right)
	return mask

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
			json_fp = path.join(dest_dirpath, '%s_%s_subset-%s.json' % (short_name, version, subset_index))
			if not path.exists(json_fp):
				with open(json_fp, 'w') as fout:
					print('\t','writing meta data to', json_fp)
					json.dump(tile_meta, fout, indent='  ')
			if 'scale_factor' in tile_meta:
				scale_factor = float(tile_meta['scale_factor'])
			else:
				scale_factor = 1
			valid_range = [float(n) for n in tile_meta['valid_range'].split(', ')]
			tile_hori_pos = int(tile_meta['HORIZONTALTILENUMBER'])
			tile_vert_pos = int(tile_meta['VERTICALTILENUMBER'])
			tile_data_raw: ndarray = tile_ds.ReadAsArray()
			## mask and scale
			tile_data = numpy.ma.array(tile_data_raw, mask=numpy.logical_or(tile_data_raw < valid_range[0], tile_data_raw > valid_range[1])).astype(numpy.float32).filled(numpy.nan) * scale_factor
			del tile_data_raw
			#print('Data shape:',tile_data.shape)
			# pyplot.imshow(tile_data, aspect='auto')
			# pyplot.show()
			for y in range(0, tile_size, downsample):
				dest_y = int((tile_size * tile_vert_pos + y) / downsample)
				for x in range(0, tile_size, downsample):
					dest_x = int((tile_size * tile_hori_pos + x) / downsample)
					if dest_x == output_map.shape[1]: print('(tile_size, tile_vert_pos, tile_hori_pos, downsample, x, y, dest_x, dest_y)',(tile_size, tile_vert_pos, tile_hori_pos, downsample, x, y, dest_x, dest_y));
					sample(tile_data, x, y, downsample, output_map, dest_x, dest_y)
			#
		## clean-up to conserve memory and resources for next iteration
		del tile_data
		del tile_meta
		del tile_ds
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

def print_modis_structure(dataset: gdal.Dataset):
	metadata_dict = dict(dataset.GetMetadata_Dict())
	metadata_dict['Subsets'] = dataset.GetSubDatasets()
	print(dataset.GetDescription(), json.dumps(metadata_dict, indent="  "))

def http_download(url, filepath):
	print('Downloading %s to %s...' % (url, filepath))
	http_session = requests.session()
	with http_session.get(url, stream=True) as r:
		print('download status code: ', r.status_code)
		r.raise_for_status()
		with open(filepath, 'wb') as f:
			for chunk in r.iter_content(chunk_size=2 ** 20): # 1 MB chunks
				f.write(chunk)
				print('.', end='')
		print()
	print('...Download complete!')

def download_GPM_L3_product(short_name, version, year, month, dest_dirpath, username, password):
	# wget --load-cookies /.urs_cookies --save-cookies /root/.urs_cookies --auth-no-challenge=on --user=your_user_name --ask-password --content-disposition -i <url text file>
	http_session = requests.session()
	if(month < 10):
		month_str = '0'+str(month)
	else:
		month_str = str(month)
	src_url = 'https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/%s.%s/%s/3B-MO.MS.MRG.3IMERG.%s%s01-S000000-E235959.%s.V06B.HDF5' % (short_name, version, year, year, month_str, month_str)
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



def get_landcover_URL_for_year(year):
	html = requests.get('https://e4ftl01.cr.usgs.gov/MOTA/MCD12C1.006/%s.01.01/' % year).content.decode('UTF-8')
	filename = re.findall('MCD12C1.*?\\.hdf', html)[0]
	return 'https://e4ftl01.cr.usgs.gov/MOTA/MCD12C1.006/%s.01.01/%s' % (year, filename)

if __name__ == '__main__':
	main()