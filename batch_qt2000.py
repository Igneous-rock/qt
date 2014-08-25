def fix_vector(p_vector):
	import geo_shape as GS
	import ogr
	f_shp = p_vector + lib_Global_const.G_base_shp
	f_shp_ui = p_vector + lib_Global_const.G_base_shp[:-4] + '_ui.shp'
	
	if not os.path.isfile(f_shp_ui): 
		GS.unifying_code(f_shp, f_shp_ui)
		
	f_csv_dem = './data/itpcas2000_dem.csv'
	dic_info,lst_vname = lib_IO.csv2dic(f_csv_dem,'ui',sw_key_int = True)
	
	ref_shp = GS.geo_shape.open(f_shp_ui,updating=True)
	lyr_ref = ref_shp.get_layer(0)
	
	dic_nm_setting = {}
	dic_nm_setting['type'] = ogr.OFTInteger
	dic_nm_setting['width'] = 10
	dic_nm_setting['precision'] = 10
	lyr_ref.add_field('Altitude','Code_uniq',dic_info,0,dic_nm_setting)
	
			
def copy_dem(pathrow,p_out_scene):
	nms_dem = ['dem_30m_slope.img', 'dem_30m.img']
	p_in_pr = '/mnt/data_3t_a/jiangh/data/' + pathrow
	p_reserve = '/mnt/data_3t_a/jiangh/DEM/dem_pr'
	
	for nm_dem in nms_dem:
		print pathrow,nm_dem
	
		f_in_dem = p_in_pr + '/' + nm_dem
		f_out_dem = p_out_scene + '/' + nm_dem
		if os.path.isfile(f_out_dem): continue
		if os.path.isfile(f_in_dem + '.gz'):
			_rs = lib_IO.run_exe('gzip -d ' + f_in_dem + '.gz')
		elif not os.path.isfile(f_in_dem):
			f_in_dem = p_reserve + '/' + pathrow + '/' + nm_dem
		f_sr = p_out_scene + '/sr_band2_30m.img'
		ref_sr = GR.geo_raster.open(f_sr)
		ulx,offx,tmp,uly,tmp,offy = ref_sr.geo_transform
		xx = ref_sr.width
		yy = ref_sr.height
		lrx = ulx + xx * offx
		lry = uly + yy * offy
		ls_ext = ['%.1f'%ulx,'%.1f'%uly,'%.1f'%lrx,'%.1f'%lry]
		str_ext = ' '.join(ls_ext)
		
		
		cmd_gdal = 'gdal_translate -of HFA -projwin ' + str_ext + ' -a_nodata -9999 ' + f_in_dem + ' ' + f_out_dem
		_rs = lib_IO.run_exe(cmd_gdal)
		print f_out_dem

		_rs = lib_IO.run_exe('gzip ' + f_in_dem)
	
def copy_images(f_hdf,p_out_scene):
	import geo_raster as GR
	ref_hdf = GR.geo_raster.open(f_hdf)
	#print ref_img.sub_datasets()
	#---- images
	for i in [2,4,5]:
	#for i in [1,2,3,4,5,6,7]:
		name_image = 'sr_band' + str(i) + '_30m.img'
		f_image = p_out_scene  + '/' + name_image
		if not os.path.isfile(f_image):
			ref_img = ref_hdf.get_subdataset(str(i))
			m_band = ref_img.get_band().read()
			
			GR.write_raster(f_image, ref_img.geo_transform, ref_img.projection,m_band, 3)
			print f_image
	

def batch_run(p_in,p_out,f_list_images,p_vector):
	#---- prepare_dir
	ls_hdf = lib_IO.getFileList(p_in,'lndsr.*\.hdf')
	'''
	while True:
		f_hdf = ls_hdf[0]
		name_f = f_hdf.split('/')[-1]
		pathrow = 'p' + name_f[9:12] + 'r' + name_f[12:15]
		#if pathrow <> 'p144r037':
		if pathrow <> 'p146r035':
			ls_hdf.pop(0)
		else:
			break
	ls_hdf = [ls_hdf[0]]
	'''
	
	for f_hdf in ls_hdf:
		#'lndsr.LE71480382000296SGS00.hdf'
		name_f = f_hdf.split('/')[-1]
		sensor = 'L' + name_f[8]
		pathrow = 'p' + name_f[9:12] + 'r' + name_f[12:15]
		t_dates = time.strptime( name_f[15:22], '%Y%j' )
		ymd = time.strftime( '%Y%m%d', t_dates )
		p_scene = sensor + '_' + pathrow + '_' + ymd

		p_out_pr = p_out + pathrow
		if not os.path.isdir(p_out_pr):
			os.mkdir(p_out_pr)
		p_out_scene = p_out_pr + '/' + p_scene
		if not os.path.isdir(p_out_scene): 
			os.mkdir(p_out_scene)
			
		copy_images(f_hdf,p_out_scene)
		copy_dem(pathrow,p_out_scene)
		
		#---- step1: extract lakes
		seed_lakes.seed_lakes(p_out_scene,p_vector)
		run_amerl.extract_water(p_out_scene)
		#---- step2: convertion
		vectorize_lake.vectorize_by_scene(p_out_scene)
		'''
		'''
		#return
	


import lib_IO
import os,sys
import csv
import time
import geo_raster as GR
import lib_Global_const
import lib_vectorize
import run_amerl,seed_lakes,vectorize_lake

#--------------------------------------------------------------
if __name__ == '__main__':
	a = time.clock()
	#fix_vector(lib_Global_const.G_path_vector)
	#batch_run(lib_Global_const.G_path_in,lib_Global_const.G_path_out,lib_Global_const.G_path_list_image,lib_Global_const.G_path_vector)
	lib_vectorize.merge_lakes_shp(lib_Global_const.G_path_out, lib_Global_const.G_path_vector)


	print time.clock() -a
	print 'done'
