
def seed_lakes(P_out_scene,p_vector):
	str_pathrow = P_out_scene.split('/')[-2]
	sn_pr = str_pathrow[1:4] + str_pathrow[-3:]

	P_out_scene = P_out_scene + '/'
	#---- generate mndwi
	f_b1 = P_out_scene + 'sr_band1_30m.img'
	f_b2 = P_out_scene + 'sr_band2_30m.img'
	f_b3 = P_out_scene + 'sr_band3_30m.img'
	f_b4 = P_out_scene + 'sr_band4_30m.img'
	f_b5 = P_out_scene + 'sr_band5_30m.img'
	f_b6 = P_out_scene + 'sr_band6_30m.img'
	f_b7 = P_out_scene + 'sr_band7_30m.img'
	
	name_wi = lib_Global_const.G_water_index
	if name_wi == 'mndwi.img':
		f_band_ir = f_b5
	elif name_wi == 'ndwi.img':
		f_band_ir = f_b4
	f_wi = P_out_scene + name_wi
	if not os.path.isfile(f_wi):
		lib_amerl_c.gen_vi(f_b2,f_band_ir,f_wi)
	
	#---- generate seeds
	f_tile = P_out_scene + 'tile.shp'
	f_china_tile = p_vector + 'wrs2_tile_proj.shp'

	ref_ct = GS.geo_shape.open(f_china_tile)
	layer_ct = ref_ct.get_layer(0)
	layer_ct.select_by_pathrow(sn_pr,f_tile)
	
	f_lakes = p_vector + lib_Global_const.G_base_shp[:-4] + '_ui.shp'
	f_lk_sel = P_out_scene + 'lake_sel.shp'
	ref_lake = GS.geo_shape.open(f_lakes)
	layer_lk = ref_lake.get_layer(0)
	layer_lk.select_by_shapefile(f_tile,f_lk_sel)

	f_lk2k_r = P_out_scene + 'lake_ras.img'
	ref_tile_lake = GS.geo_shape.open(f_lk_sel)
	layer_tlk = ref_tile_lake.get_layer(0)
	layer_tlk.fill_by_shapefile(f_wi,f_lk2k_r,0,field='code_uniq')
	
	f_mask = P_out_scene + 'mask.img'
	ref_tile = GS.geo_shape.open(f_tile)
	layer_tile = ref_tile.get_layer(0)
	layer_tile.fill_by_shapefile(f_wi,f_mask,0)
	
	lib_amerl_c.gen_seeds_grid(f_lk2k_r,f_wi,f_mask,nodata = -9999)





import lib_Global_const
import time,sys,os
import geo_raster as GR
import geo_shape as GS
import lib_amerl_c

def usage():
	import optparse

	_p = optparse.OptionParser()
	_p.add_option('-i', '--path_in', dest='path_in', default = lib_Global_const.G_path_in)
	_p.add_option('-o', '--path_out', dest='path_out', default = lib_Global_const.G_path_out)
	_p.add_option('-o', '--G_path_vector', dest='G_path_vector', default = lib_Global_const.G_path_v)
	
	_opts = _p.parse_args(sys.argv[1:])[0]

	return _opts
	
if __name__ == '__main__':
	a = time.clock()
	_opts = usage()
	seed_lakes(_opts.path_out, _opts.G_path_v)
	print time.clock() -a
	print 'done'
