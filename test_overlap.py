def test_overlaps(p_vector):
	f_pr = p_vector + 'qt2000_tile.shp'
	f_ref = p_vector + lib_Global_const.G_base_shp[:-4] + '_ui.shp'
	dic_ui_wo = lib_overlaps.mkdic_ui_pr(f_ref,f_pr)
	
	
	return
	
	dic_ui_combmethod = lib_overlaps.analysis_choose_or_union(f_ref,f_pr)

	print dic_ui_combmethod
	
	

import time,os
import lib_IO
import lib_Global_const
import lib_overlaps
if __name__ == '__main__':
	a = time.clock()
	test_overlaps(lib_Global_const.G_path_vector)
	print time.clock() -a
	print 'done'

