
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
	

def batch_run(p_in,p_out):
	#---- prepare_dir
	ls_hdf = lib_IO.getFileList(p_in,'lndsr.*\.hdf')
	'''
	while True:
		f_hdf = ls_hdf[0]
		name_f = f_hdf.split('/')[-1]
		pathrow = 'p' + name_f[9:12] + 'r' + name_f[12:15]
		#if pathrow <> 'p144r037':
		if pathrow <> 'p141r036':
			ls_hdf.pop(0)
		else:
			break
	ls_hdf = [ls_hdf[0]]
	'''
	
	for f_hdf in ls_hdf:
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
			
		#copy_images(f_hdf,p_out_scene)
		colorate_lake.colorate_lake(p_out_scene)
	


import lib_IO
import os,sys
import csv
import time
import geo_raster as GR
import lib_Global_const
import colorate_lake

#--------------------------------------------------------------
if __name__ == '__main__':
	a = time.clock()
	batch_run(lib_Global_const.G_path_in,lib_Global_const.G_path_out)


	print time.clock() -a
	print 'done'
