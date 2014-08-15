
	
def extract_water(P_out_scene):
	P_out_scene = P_out_scene + '/'
	f_b1 = P_out_scene + 'sr_band1_30m.img'
	f_b2 = P_out_scene + 'sr_band2_30m.img'
	f_b3 = P_out_scene + 'sr_band3_30m.img'
	f_b4 = P_out_scene + 'sr_band4_30m.img'
	f_b5 = P_out_scene + 'sr_band5_30m.img'
	f_b6 = P_out_scene + 'sr_band6_30m.img'
	f_b7 = P_out_scene + 'sr_band7_30m.img'
	
	f_qa = P_out_scene + 'sr_band_qa_30m.img'
	f_slope = P_out_scene + 'dem_30m_slope.img'
	
	name_wi = lib_Global_const.G_water_index
	f_wi = P_out_scene + name_wi

	f_amerl = P_out_scene + 'ws_' + name_wi
	f_mask = P_out_scene + 'mask.img'
	
	if os.path.isfile(f_slope):
		lib_amerl_slope_c.amerl_slope(f_wi,f_mask, f_b4,f_slope,G_dic_para,f_amerl)
	else:
		lib_amerl_c.amerl(f_wi,f_mask, f_b4,G_dic_para,f_amerl)

	#f_mndwi = P_out_scene + 'mndwi.img'
	f_fill_hole = P_out_scene + 'fill_' + name_wi
	lib_amerl_c.fill_hole(G_dic_para,f_amerl,f_wi,f_fill_hole)

	return
	

import time,sys,os
import lib_IO
import lib_amerl_c,lib_amerl_slope_c
import lib_Global_const


G_dic_para = {
'np':100,
'nodata':-9999,
'snow':4000,
'slope':16,
'pure_water':1300,
'land':900
}

def usage():
	import optparse

	_p = optparse.OptionParser()
	_p.add_option('-i', '--path_in', dest='path_in', default = lib_Global_const.G_path_in)
	_p.add_option('-o', '--path_out', dest='path_out', default = lib_Global_const.G_path_out)
	
	_opts = _p.parse_args(sys.argv[1:])[0]

	return _opts
	
if __name__ == '__main__':
	a = time.clock()
	_opts = usage()
	extract_water(_opts.path_in, _opts.path_out)
	print time.clock() -a
	print 'done'

