
	
def results_analysis(p_vector):
	p_vector = dic_data_path['path_vector']
	f_ref = p_vector + '/2000_Merge_ui.shp'

	f_rst_m = p_vector + '/itpcas2000/lakes_sift.shp'#lakes_combined.shp'##
	nm_ref = 'itpcas2000' #'niglas2005'
	lib_analysis.shapefile_analysis(f_ref,f_rst_m,nm_ref)

	

import time,sys
import lib_IO
import lib_analysis
import lib_Global_const


if __name__ == '__main__':
	a = time.clock()
	dic_data_path = lib_Global_const.G_dic_data_path
	results_analysis(dic_data_path)
	print time.clock() -a
	print 'done'

