#!/usr/bin/python3.9

import os, shutil, sys, re, requests, base64, urllib.parse, numpy, pandas, json, pickle, ssl, time
import gzip, h5py
from os import path
from zipfile import ZipFile
from modis_tools.auth import ModisSession
from modis_tools.resources import CollectionApi, GranuleApi
from modis_tools.granule_handler import GranuleHandler
from osgeo import gdal
from numpy import ndarray, nan
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

	# data resolution: 2 km square pixels (0.018 degrees) on sine grid (20k x 10k pixel image)
	#     X(lat,lon) = 10,000*(1 + cos(lat)*sin(lon)))
	#     Y(lat,lon) = 5,000*(1 + sin(lat))
	#     lat(X,Y) = 90*((Y/5,000) - 1)
	#     lon(X,Y) = 180*((X/10,000) - 1)/cos(lat(X,Y))

	# altitude - https://www.ngdc.noaa.gov/mgg/topo/gltiles.html
	## NOTE: GEBCO data is in mercator projection with y=0 at south pole, 240 pixels per degree
	atl_depth_zpickle_filepath = path.join(data_dir, 'altitude_2km.pickle.gz')
	if not path.exists(atl_depth_zpickle_filepath):
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
		pyplot.imshow(elevation_ds[0::100,0::100]); pyplot.gca().invert_yaxis(); pyplot.show()
	exit(1)
	alt_zip_file = path.join(data_dir, 'NOAA-GLOBE-TOPO_all-tiles.zip')
	if not path.exists(alt_zip_file):
		http_download(url='https://www.ngdc.noaa.gov/mgg/topo/DATATILES/elev/all10g.zip', filepath=alt_zip_file)
	exit(1)

	# GPP
	count = 0
	for doy in range(1,365, 8):
		count += 1
		dstart = datetime(2015,1,1) + timedelta(days=doy)
		dend = datetime(2015,1,1) + timedelta(days=doy+8)
		aq_gpp_map = retrieve_MODIS_500m_product(
			'MYD17A2H', '006', 0, dstart.isoformat()[:10], dend.isoformat()[:10], data_dir, username, password,
			downsample=10, sample_strat='mean', delete_files=True, zpickle_file=path.join(data_dir,'GPP-aqua_2015_%s.pickle.gz' % count)
		)
		fig, ax = pyplot.subplots(1,1)
		ax.imshow(aq_gpp_map, aspect='auto')
		fig.savefig('GPP-aqua_2015_%s.png' % count)
		pyplot.close(fig)
		terra_gpp_map = retrieve_MODIS_500m_product(
			'MOD17A2H', '006', 0, dstart.isoformat()[:10], dend.isoformat()[:10], data_dir, username, password,
			downsample=10, sample_strat='mean', delete_files=True, zpickle_file=path.join(data_dir,'GPP-terra_2015_%s.pickle.gz' % count)
		)
		fig, ax = pyplot.subplots(1, 1)
		ax.imshow(terra_gpp_map, aspect='auto')
		fig.savefig('GPP-terra_2015_%s.png' % count)
		pyplot.close(fig)
		all_gpp_map = numpy.nanmean(numpy.stack([aq_gpp_map, terra_gpp_map]), axis=0)
		zpickle(all_gpp_map, path.join(data_dir,'GPP_2015_%s.pickle.gz' % count))
		fig, ax = pyplot.subplots(1, 1)
		ax.imshow(all_gpp_map, aspect='auto')
		fig.savefig('GPP_2015_%s.png' % count)
		pyplot.close(fig)

	print("...Done!")

def zpickle(obj, filepath):
	parent = path.dirname(path.abspath(filepath))
	if not path.isdir(parent):
		os.makedirs(parent, exist_ok=True)
	with gzip.open(filepath, 'wb') as zout:
		pickle.dump(obj, zout)

def zunpickle(filepath):
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
	# TODO
	if dtype is None:
		singrid = numpy.zeros_like(merc) + nodata
	else:
		singrid = numpy.zeros_like(merc, dtype=dtype) + nodata
	x_offset = merc.shape[1] / 2
	deg2rad = numpy.pi/180
	grid_size_radians = merc.shape[0] / numpy.pi
	for src_y in range(merc.shape[0]):
		dst_y = src_y
		lat_rad = ((src_y / (merc.shape[0])) - 0.5) * numpy.pi
		circ = merc.shape[1] * numpy.cos(lat_rad)
		chunks = (numpy.linspace(0,1, max(1, circ)+1)*merc.shape[1]).astype(numpy.int32)
		for i in range(0, len(chunks)-1):
			src_x_left = chunks[i]
			src_x_right = chunks[i+1]
			dst_x = int(x_offset - (circ/2) + i)


		# TODO


# TODO: mercator to singrid function with resizing

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


def retrieve_MODIS_500m_product(short_name, version, subset_index, start_date, end_date, dest_dirpath, username, password,
								downsample: int = 10, sample_strat='mean', delete_files=False,
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
	downsample = int(downsample)
	if downsample < 1: raise Exception('downsample must be a positive integer');

	## NOTE: y=0 is north, positive y is south direction, x=0 is west, positive x is east direction
	## NOTE: ndarray dimension order = data[y][x]
	w=int(tile_size * MODIS_grid_hori_count / downsample)
	h=int(tile_size * MODIS_grid_vert_count / downsample)
	output_map: ndarray = numpy.ones((h, w), dtype=numpy.float32) * numpy.nan

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
		tile_ds: gdal.Dataset = gdal.Open(ds.GetSubDatasets()[subset_index][0])
		tile_meta: {} = tile_ds.GetMetadata_Dict()
		json_fp = path.join(dest_dirpath, '%s_%s_subset-%s.json' % (short_name, version, subset_index))
		if not path.exists(json_fp):
			with open(json_fp, 'w') as fout:
				print('\t','writing meta data to', json_fp)
				json.dump(tile_meta, fout, indent='  ')
		scale_factor = float(tile_meta['scale_factor'])
		valid_range = [float(n) for n in tile_meta['valid_range'].split(', ')]
		tile_hori_pos = int(tile_meta['HORIZONTALTILENUMBER'])
		tile_vert_pos = int(tile_meta['VERTICALTILENUMBER'])
		tile_data: ndarray = tile_ds.ReadAsArray()
		## mask and scale
		tile_data = numpy.ma.array(tile_data, mask=numpy.logical_or(tile_data < valid_range[0], tile_data > valid_range[1])).astype(numpy.float32).filled(numpy.nan) * scale_factor
		#print('Data shape:',tile_data.shape)
		# pyplot.imshow(tile_data, aspect='auto')
		# pyplot.show()
		## subsample to output array
		if sample_strat == 'mean':
			def sample(src_data: ndarray, src_x: int, src_y: int, ssize: int, dest_data: ndarray, dest_x: int, dest_y: int):
				dest_data[dest_y][dest_x] = numpy.nanmean(src_data[src_y:src_y+ssize,src_x:src_x+ssize])
		elif sample_strat == 'median':
			def sample(src_data: ndarray, src_x: int, src_y: int, ssize: int, dest_data: ndarray, dest_x: int, dest_y: int):
				dest_data[dest_y][dest_x] = numpy.nanmedian(src_data[src_y:src_y+ssize,src_x:src_x+ssize])
		elif sample_strat == 'mode':
			def sample(src_data: ndarray, src_x: int, src_y: int, ssize: int, dest_data: ndarray, dest_x: int, dest_y: int):
				vals, counts = numpy.unique(src_data[src_y:src_y+ssize,src_x:src_x+ssize], return_counts=True)
				_mode = vals[numpy.argmax(counts)]
				dest_data[dest_y][dest_x] = _mode
		else: # nearest
			def sample(src_data: ndarray, src_x: int, src_y: int, ssize: int, dest_data: ndarray, dest_x: int, dest_y: int):
				dest_data[dest_y][dest_x] = src_data[src_y][src_x]
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
		zpickle(output_map, zpickle_file)
		print('Saved %s' % zpickle_file)
	return output_map

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