import numpy as np
import geo_raster as GR
import ogr,gdal,osr
import os
import lib_IO, lib_Global_const
import geo_shape as GS
#----------------------------------------------------------------------  by scene
def polygonize_scene(f_img,f_vct):
	#-------------- generate original shaplefile, complex polygon and in a UTM projection
	f_temp = os.path.split(f_vct)[0] + '/lakes_ori.shp'
	ds_img = gdal.Open(f_img)
	band = ds_img.GetRasterBand(1)
	
	projection = ds_img.GetProjection()
	geo_transform = ds_img.GetGeoTransform()

	driver = ogr.GetDriverByName("ESRI Shapefile")
	if os.path.exists(f_temp):
		driver.DeleteDataSource(f_temp)
		
	ds_out = driver.CreateDataSource(f_temp)
	layer_out = ds_out.CreateLayer("polygonized", srs=None)
	field_new = ogr.FieldDefn('Code_uniq', ogr.OFTInteger)
	layer_out.CreateField(field_new)
	
	gdal.Polygonize( band, None, layer_out, 0, [], callback=None )
	
	ds_out.Destroy()
	del ds_img
	
	f_prj = f_temp[:-3] + 'prj'
	fo_prj = open(f_prj,'w')
	fo_prj.write(projection)
	fo_prj.close()
	#-------------- simplify and reprojct
	cmd_ogr = 'ogr2ogr -overwrite -simplify 30 -where \"Code_uniq>0\"  -t_srs "+proj=aea +lat_1=25.0 +lat_2=47.0 +lon_0=105.0 +x_0=0 +y_0=0 +datum=WGS84" ' + f_vct + ' ' + f_temp

	_rs = lib_IO.run_exe(cmd_ogr)
	print f_vct

	driver = ogr.GetDriverByName("ESRI Shapefile")
	driver.DeleteDataSource(f_temp)
	
#---------------------------------------------------------------------- by region
def dissolve_polygons_cmd(f_merged,f_final):
	cmd_ogr = 'ogr2ogr -f "ESRI Shapefile" ' + f_final + ' ' + f_merged + ' -dialect sqlite -sql "select ST_union(Geometry),Code_uniq from input GROUP BY Code_uniq"'
	_rs = lib_IO.run_exe(cmd_ogr)
	print f_final

def sub__index_feature_by_field(_lyr):
	n_ft_m = _lyr.layer.GetFeatureCount()

	dic_code_num = {}
	for i in xrange(n_ft_m):
		ft_mg = _lyr.layer.GetFeature(i)
		code_u = ft_mg.GetField('Code_uniq')
		if code_u in dic_code_num:
			dic_code_num[code_u].append(i)
		else:
			dic_code_num[code_u] = [i]
		ft_mg.Destroy()
	return dic_code_num
	
def dissolve_polygons(f_merged,f_ref,f_final):
	ref_merge = GS.geo_shape.open(f_merged)
	lyr_merge = ref_merge.get_layer(0)
	proj_in = lyr_merge.spatial_ref

	ref_ref = GS.geo_shape.open(f_ref)
	lyr_ref = ref_ref.get_layer(0)
	
	#---- create new
	ogr.RegisterAll()
	driver = ogr.GetDriverByName("ESRI Shapefile")
	if os.access(f_final, os.F_OK):
		driver.DeleteDataSource(f_final)
		
	ds_out = driver.CreateDataSource(f_final)
	layer_out = ds_out.CopyLayer(lyr_ref.layer,'dissolved')
	
	dic_merge_cn = sub__index_feature_by_field(lyr_merge)
	dic_ref_cn   = sub__index_feature_by_field(lyr_ref)

	ks = dic_merge_cn.keys()
	ks.sort()
	for k in ks:
		ls_i = dic_merge_cn[k]
		print k,len(ls_i)
		i_ft = ls_i.pop(0)
		
		ft_mgs = lyr_merge.layer.GetFeature(i_ft)
		geom_dsv = ft_mgs.GetGeometryRef()
		while ls_i:
			i_ft = ls_i.pop(0)
			ft_mg = lyr_merge.layer.GetFeature(i_ft)
			geom_mg = ft_mg.GetGeometryRef()
			geom_dsv = geom_dsv.Union(geom_mg)
			ft_mg.Destroy()

		i_ft_ref = dic_ref_cn[k]
		ft_out = layer_out.GetFeature(i_ft_ref[0])
		ft_out.SetGeometry(geom_dsv)
		layer_out.SetFeature(ft_out)

		ft_mgs.Destroy()
		ft_out.Destroy()

	ds_out.Destroy()

	'''
def dissolve_polygons(f_merged,f_ref,f_final):
	ref_merge = GS.geo_shape.open(f_merged)
	lyr_merge = ref_merge.get_layer(0)
	proj_in = lyr_merge.spatial_ref

	ref_ref = GS.geo_shape.open(f_ref)
	lyr_ref = ref_ref.get_layer(0)
	
	#---- create new
	ogr.RegisterAll()
	driver = ogr.GetDriverByName("ESRI Shapefile")
	if os.access(f_final, os.F_OK):
		driver.DeleteDataSource(f_final)
		
	ds_out = driver.CreateDataSource(f_final)
	layer_out = ds_out.CreateLayer("dissolved", srs = proj_in)
	dfn_field = ogr.FieldDefn('Code_uniq', ogr.OFTInteger)
	layer_out.CreateField(dfn_field)
	
	dfn_layer = layer_out.GetLayerDefn()

	dic_merge_cn = sub__index_feature_by_field(lyr_merge)

	ks = dic_merge_cn.keys()
	ks.sort()
	for k in ks:
		ls_i = dic_merge_cn[k]
		print k,len(ls_i)
		i_ft = ls_i.pop(0)
		
		ft_mgs = lyr_merge.layer.GetFeature(i_ft)
		geom_dsv = ft_mgs.GetGeometryRef()
		while ls_i:
			i_ft = ls_i.pop(0)
			ft_mg = lyr_merge.layer.GetFeature(i_ft)
			geom_mg = ft_mg.GetGeometryRef()
			geom_dsv = geom_dsv.Union(geom_mg)
			ft_mg.Destroy()
		ft_out = ogr.Feature(dfn_layer)
		ft_out.SetGeometry(geom_dsv)
		ft_out.SetField('Code_uniq', k)
		layer_out.CreateFeature(ft_out)

		ft_mgs.Destroy()
		ft_out.Destroy()

	ds_out.Destroy()
	'''
	

def merge_lakes_shp(p_out,p_vector):
	f_merged = p_vector + 'lakes_merged.shp'
	f_ref = p_vector + '2000_Merge_unicd.shp'
	'''
	ls_pr = lib_IO.getDirList( p_out ,'p...r...')
	name_wi = lib_Global_const.G_water_index

	fs_lake_shp = []
	for pr in ls_pr:
		p_pr = p_out + pr
		name_scene = lib_IO.getDirList(p_pr ,'L.*')[0]
		p_out_scene = p_pr + '/' + name_scene
		f_lake_shp = p_out_scene + '/lakes_' + name_wi[:-4] + '.shp'
		if os.path.isfile(f_lake_shp):
			fs_lake_shp.append(f_lake_shp)
		else:
			print 'failure on ',f_lake_shp
	
	
	cmd_ogr = 'ogr2ogr -overwrite ' + f_merged + ' ' + fs_lake_shp[0]
	_rs = lib_IO.run_exe(cmd_ogr)
	print fs_lake_shp[0]
	
	for f in fs_lake_shp[1:]:
		cmd_ogr = 'ogr2ogr -update -append ' + f_merged + ' ' + f
		_rs = lib_IO.run_exe(cmd_ogr)
		print f
	'''

	f_final = p_vector + 'lakes_final.shp'
	'''
	try:
		dissolve_polygons_cmd(f_merged,f_final)
	except:
	'''
	dissolve_polygons(f_merged,f_ref,f_final)
	

	
	
	
	
	
