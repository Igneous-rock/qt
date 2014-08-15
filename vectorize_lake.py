
	
def vectorize_by_scene(P_out_scene):
	P_out_scene = P_out_scene + '/'

	name_wi = lib_Global_const.G_water_index
	f_wi = P_out_scene + name_wi

	f_amerl = P_out_scene + 'ws_' + name_wi

	#f_fill = P_out_scene + 'ws_filled.img'
	f_fill = P_out_scene + 'fill_' + name_wi
	#f_ref = p_vector + lib_Global_const.G_base_shp[:-4] + '_ui.shp'
	
	f_vct = P_out_scene + 'lakes_' + name_wi[:-4] + '.shp'
	lib_vectorize.polygonize_scene(f_fill,f_vct)
	

	return
	

import time,sys
import lib_IO
import lib_vectorize
import lib_Global_const

def usage():
	import optparse

	_p = optparse.OptionParser()
	_p.add_option('-o', '--path_out', dest='path_out', default = lib_Global_const.G_path_out)
	_p.add_option('-o', '--G_path_vector', dest='G_path_vector', default = lib_Global_const.G_path_v)
	
	_opts = _p.parse_args(sys.argv[1:])[0]

	return _opts
	
if __name__ == '__main__':
	a = time.clock()
	vectorize_by_scene(_opts.path_out, _opts.G_path_v)
	print time.clock() -a
	print 'done'

