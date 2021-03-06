#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------- from mfeng
'''
File: visualize_bands.py
Author: Min Feng
Version: 0.1
Create: 2014-04-03 16:40:03
Description: convert raster data to visualiable image
'''
import os
import lib_IO
import gdal,ogr,osr
import geo_raster as GR
#python visualize_bands.py -i pct.tif -b 1 2 3 -o rgb.png -sr
def search_threshold(vs, ls, sh):
	_sum = int(sum(vs) * sh)

	_t = 0
	for i in xrange(len(vs)):
		_t += vs[i]
		if _t > _sum:
			return ls[i]

	raise Exception('failed to find threshold')

def convert_band_sr(bnd, row, line, ref, sh=0.2):
	import numpy as np

	if bnd.nodata == None:
		bnd.nodata = 0

	# _bnd = bnd.cache()
	_dat = bnd.read_rows(row, line)

	import math
	_low = math.log(150)
	_top = math.log(5000)

	_dat[_dat > 0] = (np.log(_dat.astype(np.float32)[_dat > 0]) - _low) * (256.0 / (_top - _low))

	_dat[_dat > 255] = 255
	_dat[_dat < 0] = 0

	return _dat
	# return bnd.from_grid(_dat, nodata=0)

def convert_band(bnd, row, line, ref, sh=0.2):
	import numpy as np

	if bnd.nodata == None:
		bnd.nodata = 0

	#_bnd = bnd.cache()
	bnd.read_rows(row, line)
	#_dat = bnd.cached.data_ma
	_dat = bnd.read_rows(row, line)
	
	_ddd = _dat

	_min = _dat.min()
	_max = _dat.max()

	_bin = int(_max - _min)
	_bin = max(_bin, 10)

	_vs, _ls = np.histogram(_ddd, bins=_bin, range=(_min, _max))

	_low = search_threshold(_vs, _ls, sh)
	_top = search_threshold(_vs[::-1], _ls[::-1], sh)

	if _top <= _low:
		raise Exception('failed to find threshold %s - %s' % (_low, _top))

	_dat = (_dat.astype(np.float32) - _low) * (256.0 / (_top - _low))

	_dat[_dat > 255] = 255
	_dat[_dat < 0] = 0

	return _dat
	# return bnd.from_ma_grid(_dat, nodata=0)

def three_bands_to_rgb(f_bands,bs,f_rgb,conv_sr=True):
	import geo_raster as GR

	_bnds = []

	if f_bands.endswith('hdf'):
		ref_img = GR.geo_raster.open(f_bands)
		for _b in bs:
			_bnds.append(ref_img.get_subdataset(_b).get_band())
			
	else:
		ref_img = GR.geo_raster.open(f_bands)
		for _b in bs:
			_bnds.append(ref_img.get_band(int(_b)))

	if len(_bnds) not in [1, 3]:
		raise Exception('Incorrect band numbers %s' % len(_bnds))

	_bnd = _bnds[0]

	ref_img = GR.geo_raster.create(f_rgb, [len(_bnds), _bnd.height, _bnd.width],
				ref_img.geo_transform, ref_img.projection, 1)

	_line = 1024
	for i in xrange(len(_bnds)):
		print ' + band', bs[i], 'sr' if conv_sr else 'dn'

		_bbb = ref_img.get_band(i + 1)
		_fun = convert_band_sr if conv_sr else convert_band

		for _row in xrange(0, _bnd.height, _line):
			_bbb.write(_fun(_bnds[i], _row, _line, _bnd), 0, _row)

	ref_img = None
	print f_rgb
#---------------------------------------------------------------------- /from mfeng


#--------------------------------------------------- vectorize lake with original utm projection
def upscaling_raster(fs_use,p_render,resolution):
	fs_out = []
	for f_in in fs_use:
		name_img = os.path.split(f_in)[-1]
		if f_in[-5] == 'm':
			f_out = p_render + '/' + name_img[:-7] + str(resolution)+ 'm.tif'
		else:
			f_out = p_render + '/' + name_img[:-4] + '_' + str(resolution)+ 'm.tif'
	
		cmd_gdal = 'gdalwarp -tr ' + str(resolution) + ' ' + str(resolution) + ' -r average -overwrite -multi -srcnodata -9999 -dstnodata -9999 ' + f_in + ' ' + f_out
		if not os.path.isfile(f_out):
			_rs = lib_IO.run_exe(cmd_gdal)
		print f_out
		fs_out.append(f_out)
	if len(fs_use) == 1:
		return f_out,fs_out
	
	f_pct = p_render + '/pct.tif'
	str_files = ' '.join(fs_out)
	cmd_merge = 'gdal_merge.py -separate -pct -o ' + f_pct + ' ' + str_files
	_rs = lib_IO.run_exe(cmd_merge)
	print f_pct
	return f_pct,fs_out

	
		
def sub__add_fields(layer_out):
	field_new = ogr.FieldDefn('Code_uniq', ogr.OFTInteger)
	layer_out.CreateField(field_new)

	field_new = ogr.FieldDefn('PathRow', ogr.OFTString)
	field_new.SetWidth(10)
	layer_out.CreateField(field_new)

	field_new = ogr.FieldDefn('Day', ogr.OFTDate)
	field_new.SetWidth(10)
	layer_out.CreateField(field_new)

	field_new = ogr.FieldDefn('Source', ogr.OFTString)
	field_new.SetWidth(10)
	layer_out.CreateField(field_new)
	
def sub__update_field_value(f_vct,layer_out):
	G_dic_sensor = {'L5':'TM','L7':'ETM+','L8':'OLI'}
	name_scene = f_vct.split('/')[-3]
	snr,pr,dt = name_scene.split('_')
	sensor = G_dic_sensor[snr]
	pathrow = pr[1:4] + pr[-3:]
	date = dt[:4] + '-' + dt[4:6] + '-' + dt[-2:]

	n_ft = layer_out.GetFeatureCount()
	
	for i in range(n_ft):
		ft_i = layer_out.GetFeature(i)
		
		ft_i.SetField('PathRow', pathrow)
		ft_i.SetField('Source', sensor)
		ft_i.SetField('Day', date)
		layer_out.SetFeature(ft_i)
	
def polygonize_scene(p_render,f_img,f_vct):
	#-------------- generate original shaplefile, complex polygon and in a UTM projection
	f_temp = p_render + '/lakes_ori.shp'
	ds_img = gdal.Open(f_img)
	band = ds_img.GetRasterBand(1)
	
	projection = ds_img.GetProjection()
	geo_transform = ds_img.GetGeoTransform()

	driver = ogr.GetDriverByName("ESRI Shapefile")
	if os.path.exists(f_temp):
		driver.DeleteDataSource(f_temp)
		
	sr_in = osr.SpatialReference()
	sr_in.ImportFromWkt(projection)
	ds_out = driver.CreateDataSource(f_temp)
	layer_out = ds_out.CreateLayer("polygonized", srs=sr_in)
	sub__add_fields(layer_out)
	
	gdal.Polygonize( band, None, layer_out, 0, [], callback=None )
	
	sub__update_field_value(f_vct,layer_out)
	
	ds_out.Destroy()
	del ds_img
	
	#-------------- simplify and reprojct
	cmd_ogr = 'ogr2ogr -overwrite -simplify 25 -where \"Code_uniq>0\" ' + f_vct + ' ' + f_temp

	_rs = lib_IO.run_exe(cmd_ogr)
	print f_vct
	
	driver = ogr.GetDriverByName("ESRI Shapefile")
	#driver.DeleteDataSource(f_temp)
		
#---------------------------------------------------------------------- mapnik2 rendering	
def mapnik_rendering(f_pct,f_vct,f_render):
	import mapnik2 as mapnik

	ref_pct = GR.geo_raster.open(f_pct)
	proj = ref_pct.projection
	tr = ref_pct.geo_transform
	width = ref_pct.width
	height = ref_pct.height
	size_p = tr[1]
	minx = tr[0]
	maxy = tr[3]
	miny = tr[3] - height * size_p
	maxx = tr[0] + width * size_p
	bbox = (minx, miny, maxx, maxy)

	#---- init
	_map = mapnik.Map(width,height)
	_map.background = mapnik.Color('black')
	#----==== raster
	style_gdal = mapnik.Style() # style object to hold rules
	rule_gdal = mapnik.Rule() # rule object to hold symbolizers
	symbol_gdal = mapnik.RasterSymbolizer()
	#symbol_gdal.opacity = 0.5
	#$symbol_gdal.colorizer = mapnik.RasterColorizer(mapnik.COLORIZER_INHERIT, mapnik.Color(255,255,255))
	c = mapnik.RasterColorizer( mapnik.COLORIZER_LINEAR , mapnik.Color(0,0,0) )
	
	c.epsilon = 0.001
	c.add_stop(0)
	c.add_stop(900, mapnik.COLORIZER_LINEAR, mapnik.Color("#F3DDB4"))
	c.add_stop(1300, mapnik.COLORIZER_LINEAR, mapnik.Color("cyan"))
	c.add_stop(2000, mapnik.COLORIZER_LINEAR, mapnik.Color("white"))
	#c.get_color(2000)
	#c.stops[1].color
	#'''
	symbol_gdal.colorizer = c
	
	rule_gdal.symbols.append(symbol_gdal)
	style_gdal.rules.append(rule_gdal)
	_map.append_style("Raster Style", style_gdal)
	mlyr_gdal = mapnik.Layer('TM_images')
	mlyr_gdal.datasource = mapnik.Gdal(file=f_pct,band=1,bbox=bbox)
	#mlyr_gdal.srs = '+proj=utm +zone=46 +ellps=WGS84 +units=m +no_defs '
	mlyr_gdal.styles.append('Raster Style')
	_map.layers.append(mlyr_gdal)
	
	#'''
	#----==== shape
	style_vct = mapnik.Style() # style object to hold rules
	rule_vct = mapnik.Rule() # rule object to hold symbolizers
	
	#==== ==== add labels
	symbol_text = mapnik.TextSymbolizer(mapnik.Expression('[Code_uniq]'), 'DejaVu Sans Book', 20, mapnik.Color('black'))
	symbol_text.halo_fill = mapnik.Color('white')
	symbol_text.halo_radius = 1
	symbol_text.avoid_edges = True 
	#symbol_text.allow_overlap = False
	symbol_text.vertical_alignment = mapnik.vertical_alignment.TOP
	symbol_text.label_placement = mapnik.label_placement.POINT_PLACEMENT #LINE_PLACEMENT # is default
	rule_vct.symbols.append(symbol_text)
	
	#==== ==== 1.add polygon
	symbol_vct = mapnik.PolygonSymbolizer(mapnik.Color('#059BFF'))
	symbol_vct.opacity = 1#0.6
	rule_vct.symbols.append(symbol_vct) # add the symbolizer to the rule object
	#==== ==== 2.add outlines
	line_symbolizer = mapnik.LineSymbolizer(mapnik.Color('black'),0.3)
	rule_vct.symbols.append(line_symbolizer) # add the symbolizer to the rule object
	
	
	style_vct.rules.append(rule_vct) # now add the rule to the style and we're done
	_map.append_style('vector',style_vct) # Styles are given names only as they are applied to the map
	ds_shp = mapnik.Shapefile(file=f_vct)
	mlyr_shp = mapnik.Layer('lakes') 

	mlyr_shp.datasource = ds_shp
	mlyr_shp.styles.append('vector')
	_map.layers.append(mlyr_shp)
	

	#'''
	_map.zoom_all()
	
	# Write the data to a png image called world.png the current directory
	mapnik.render_to_file(_map,f_render, 'png')
	print f_render


	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	