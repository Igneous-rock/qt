def test_label():
	import numpy as np
	import geo_raster as GR
	from scipy.ndimage.measurements import find_objects
	f_img = '/mnt/data_3t_a/jiangh/result/qt2000/p142r035/L7_p142r035_20010711/ws_mndwi.img'
	f_out = '/mnt/data_3t_a/jiangh/result/qt2000/p142r035/L7_p142r035_20010711/ws_remove.img'

	ref_wi = GR.geo_raster.open(f_img)
	m_wi = ref_wi.get_band().read()
	
	m_out = lib_amerl_c.remove_small_objects(m_wi,10)
	GR.write_raster(f_out, ref_wi.geo_transform, ref_wi.projection, m_out,3)
	print f_out




def test_overlaps(p_vector):
	f_pr = p_vector + 'requires/image_extent.shp'
	f_ref = p_vector + lib_Global_const.G_base_shp[:-4] + '_ui.shp'
	dic_ui_wo = lib_overlaps.mkdic_ui_pr(f_ref,f_pr)
	
	f_old = p_vector + 'qt2000_tile.shp'
	dic_ui_old = lib_overlaps.mkdic_ui_pr(f_ref,f_old)
	
	ks = dic_ui_old.keys()
	ks.sort()
	for k in ks:
		if dic_ui_wo[k] <> dic_ui_old[k]:print k,dic_ui_wo[k],dic_ui_old[k]
	return
	

	

import time,os
import lib_IO
import lib_Global_const
import lib_overlaps
import lib_amerl_c
if __name__ == '__main__':
	a = time.clock()
	#test_label()
	test_overlaps(lib_Global_const.G_path_vector)
	print time.clock() -a
	print 'done'

