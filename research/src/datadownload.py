#!/usr/bin/python3.9

import os, shutil, sys, re, requests, base64, urllib.parse, numpy, pandas, json
from os import path
from modis_tools.auth import ModisSession
from modis_tools.resources import CollectionApi, GranuleApi
from modis_tools.granule_handler import GranuleHandler
from osgeo import gdal
from numpy import ndarray
from pandas import DataFrame
from matplotlib import pyplot

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
	download_MODIS_product('MYD17A2H', '006', '2015-01-01', '2015-01-08', data_dir, username, password)
	# for year in range(2015, 2018):
	# 	for month in range(1, 13):
	# 		download_GPM_L3_product('GPM_3IMERGM', '06', year, month, data_dir, username, password)
	# 	download_MODIS_product('MOD21C3', '061', '%s-01-01' % year, '%s-12-31' % year, data_dir, username, password)
	# 	download_MODIS_product('MCD12C1', '006', '%s-01-01' % year, '%s-12-31' % year, data_dir, username, password)
	#
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


def download_MODIS_product(short_name, version, start_date, end_date, dest_dirpath, username, password, subsample_shape=(900,1800)):
	## NOTE: MODIS tile grid explained at https://modis-land.gsfc.nasa.gov/MODLAND_grid.html
	earth_radius_m = 6371007.181
	deg_per_m = 180 / (numpy.pi * earth_radius_m)
	deg_per_500m = deg_per_m * 500
	output_map: ndarray = numpy.ones(subsample_shape, dtype=numpy.float32) * numpy.nan
	w=subsample_shape[1]
	h=subsample_shape[0]
	os.makedirs(dest_dirpath, exist_ok=True)
	modis_session = ModisSession(username=username, password=password)
	# Query the MODIS catalog for collections
	collection_client = CollectionApi(session=modis_session)
	collections = collection_client.query(short_name=short_name, version=version)
	granule_client = GranuleApi.from_collection(collections[0], session=modis_session)
	granules = granule_client.query(start_date=start_date, end_date=end_date)
	print('Downloading %s to %s...' % (short_name, dest_dirpath))
	debug_skip = 9
	for g in granules:
		if(debug_skip:=debug_skip-1) != 0: continue
		# print('links:')
		# for L in g.links:
		# 	print('\t',L.href)
		filename = g.links[0].href[g.links[0].href.rfind('/')+1:]
		print(filename)
		filepath=path.join(dest_dirpath, filename)
		if not path.exists(filepath):
			GranuleHandler.download_from_granules(g, modis_session, path=dest_dirpath)
		if not path.exists(filepath):
			print('failed to download %s' % filename)
			exit(1)
		ds: gdal.Dataset = gdal.Open(filepath)
		print_modis_structure(ds)
		metadata: {} = ds.GetMetadata_Dict()
		tile_ds: gdal.Dataset = gdal.Open(ds.GetSubDatasets()[0][0])
		tile_meta: {} = tile_ds.GetMetadata_Dict()
		print(json.dumps(tile_meta, indent='  '))
		scale_factor = float(tile_meta['scale_factor'])
		valid_range = [float(n) for n in tile_meta['valid_range'].split(', ')]
		min_lon = float(tile_meta['WESTBOUNDINGCOORDINATE'])
		min_lat = float(tile_meta['SOUTHBOUNDINGCOORDINATE'])
		max_lon = float(tile_meta['EASTBOUNDINGCOORDINATE'])
		max_lat = float(tile_meta['NORTHBOUNDINGCOORDINATE'])
		tile_data: ndarray = tile_ds.ReadAsArray()
		## mask and scale
		tile_data = numpy.ma.array(tile_data, mask=numpy.logical_or(tile_data < valid_range[0], tile_data > valid_range[1])).astype(numpy.float32).filled(numpy.nan) * scale_factor
		print('Data shape:',tile_data.shape)
		print(tile_data[10][10])
		print(tile_data[800][2300])
		pyplot.imshow(tile_data, aspect='auto')
		pyplot.show()
		dest_bounds = (int(h*(min_lat/180)+0.5), int((w/2)+(w * (min_lon / 360))), int(h*(max_lat/180)+0.5), int((w/2)+(w * (max_lon / 360))))
		for dest_y in range(dest_bounds[1],dest_bounds[3]+1):
			dest_lat = 180*((dest_y/h)-0.5)
			y =
			for dest_x in range(dest_bounds[0],dest_bounds[2]+1):
				dest_lon = 360*((dest_x/(w*numpy.cos(dest_lat*numpy.pi/180)))-0.5)
				x =
				output_map[dest_y][dest_x] = tile_data[y][x]
				if not numpy.isnan(tile_data[y][x]): print('(%s,%s) -> (%s,%s)' % (x, y, dest_x, dest_y))
		pyplot.imshow(output_map, aspect='auto')
		pyplot.show()
		# TODO: download, then down-sample at 0.05 deg (5.56km), then delete (to save space)
		exit(1)

	#GranuleHandler.download_from_granules(granules, modis_session, path='data')
	print('...Download complete!')

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