
	
def vectorize_by_scene(P_out_scene,dic_data_path):
	P_out_scene = P_out_scene + '/'

	name_wi = dic_data_path['water_index']
	f_wi = P_out_scene + name_wi

	f_amerl = P_out_scene + 'ws_' + name_wi
	f_fill = P_out_scene + 'fill_' + name_wi

	f_vct = P_out_scene + 'lakes_' + name_wi[:-4] + '.shp'
	lib_vectorize.polygonize_scene(f_fill,f_vct)
	

	return
	

import time,sys
import lib_IO
import lib_vectorize

