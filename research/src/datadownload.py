#!/usr/bin/python3.9

import os, shutil, sys, re, requests, base64, urllib.parse, numpy, pandas, json, pickle, ssl, time
from os import path
from modis_tools.auth import ModisSession
from modis_tools.resources import CollectionApi, GranuleApi
from modis_tools.granule_handler import GranuleHandler
from osgeo import gdal
from numpy import ndarray
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
	modis_session = ModisSession(username=username, password=password)
	collection_client = CollectionApi(session=modis_session)
	collections = collection_client.query(short_name='MYD17A2H', version='006')
	print('collections size:', len(collections))
	# GPP
	count = 0
	for doy in range(1,365, 8):
		count += 1
		dstart = datetime(2015,1,1) + timedelta(days=doy)
		dend = datetime(2015,1,1) + timedelta(days=doy+8)
		aq_gpp_map = retrieve_MODIS_500m_product(
			'MYD17A2H', '006', 0, dstart.isoformat()[:10], dend.isoformat()[:10], data_dir, username, password,
			downsample=10, sample_strat='mean', delete_files=True, pickle_file=path.join(data_dir,'GPP-aqua_2015_%s.pickle' % count)
		)
		pyplot.imshow(aq_gpp_map, aspect='auto')
		pyplot.savefig('GPP-aqua_2015_%s.png' % count)
		pyplot.clf()
		terra_gpp_map = retrieve_MODIS_500m_product(
			'MOD17A2H', '006', 0, dstart.isoformat()[:10], dend.isoformat()[:10], data_dir, username, password,
			downsample=5, sample_strat='mean', delete_files=True, pickle_file=path.join(data_dir,'GPP-terra_2015_%s.pickle' % count)
		)
		pyplot.imshow(terra_gpp_map, aspect='auto')
		pyplot.savefig('GPP-terra_2015_%s.png' % count)
		pyplot.clf()
		all_gpp_map = numpy.nanmean(numpy.stack([aq_gpp_map, terra_gpp_map]), axis=0)
		with open(path.join(data_dir,'GPP_2015_%s.pickle' % count), 'wb') as fout: pickle.dump(all_gpp_map, fout);
		pyplot.imshow(all_gpp_map, aspect='auto')
		pyplot.savefig('GPP_2015_%s.png' % count)
		pyplot.clf()

	print("...Done!")

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
								pickle_file=None, retry_limit=5, retry_delay=10):
	## NOTE: MODIS tile grid explained at https://modis-land.gsfc.nasa.gov/MODLAND_grid.html
	if pickle_file is not None and path.exists(pickle_file):
		print('%s already exists. Skipping download.' % pickle_file)
		with open(pickle_file, 'rb') as fin:
			return pickle.load(fin)
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
	if pickle_file is not None:
		with open(pickle_file, 'wb') as fout:
			pickle.dump(output_map, fout)
			print('Saved %s' % pickle_file)
	return output_map

def print_modis_structure(dataset: gdal.Dataset):
	metadata_dict = dict(dataset.GetMetadata_Dict())
	metadata_dict['Subsets'] = dataset.GetSubDatasets()
	print(dataset.GetDescription(), json.dumps(metadata_dict, indent="  "))


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