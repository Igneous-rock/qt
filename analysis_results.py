
	
def results_analysis(p_vector):
	f_ref = p_vector + '2000_Merge_ui.shp'
	#nm_ref = lib_Global_const.G_base_shp[:-4]
	#f_ref = p_vector + nm_ref + '_ui.shp'
	
	#f_vct = p_vector + 'lakes_final.shp'
	#nm_wi = lib_Global_const.name_wi[:-4]
	
	f_rst_m = p_vector + 'itpcas2000/lakes_sift.shp'#lakes_combined.shp'##
	nm_ref = 'itpcas2000' #'niglas2005'
	lib_analysis.shapefile_analysis(f_ref,f_rst_m,nm_ref)
	return 
	
	nm_ndwi = 'ndwi'
	f_rst_n = p_vector + 'itpcas2000/dissolved_' + nm_ndwi + '.shp'
	nm_ref = 'itpcas2000' #'niglas2005'
	#lib_analysis.shapefile_analysis_double(f_ref,f_rst_m,f_rst_n,nms_data)
	

	return
	

import time,sys
import lib_IO
import lib_analysis
import lib_Global_const


if __name__ == '__main__':
	a = time.clock()
	results_analysis(lib_Global_const.G_path_vector)
	print time.clock() -a
	print 'done'

