#-*- coding: cp936 -*- 
import ogr,gdal,osr
import os
import lib_IO, lib_Global_const
import geo_shape as GS
#------------------ global variable
G_dic_sensor = {'L5':'TM','L7':'ETM+','L8':'OLI'}
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
		
	sr_in = osr.SpatialReference()
	sr_in.ImportFromWkt(projection)
	ds_out = driver.CreateDataSource(f_temp)
	layer_out = ds_out.CreateLayer("polygonized", srs=sr_in)
	sub__add_fields(layer_out)
	
	gdal.Polygonize( band, None, layer_out, 0, [], callback=None )
	
	sub__update_field_value(f_vct,layer_out)
	
	ds_out.Destroy()
	del ds_img
	
	#-------------- simplify and reprojct
	#cmd_ogr = 'ogr2ogr -overwrite -simplify 30 -where \"Code_uniq>0\"  -t_srs "+proj=aea +lat_1=25.0 +lat_2=47.0 +lon_0=105.0 +x_0=0 +y_0=0 +datum=WGS84" ' + f_vct + ' ' + f_temp
	cmd_ogr = 'ogr2ogr -overwrite -simplify 25 -where \"Code_uniq>0\"  -t_srs "+proj=aea +lat_1=25.0 +lat_2=47.0 +lon_0=105.0 +x_0=0 +y_0=0 +datum=WGS84" ' + f_vct + ' ' + f_temp

	_rs = lib_IO.run_exe(cmd_ogr)
	print f_vct
	
	driver = ogr.GetDriverByName("ESRI Shapefile")
	driver.DeleteDataSource(f_temp)
	

def sub__add_fields(layer_out):
	field_new = ogr.FieldDefn('Code_uniq', ogr.OFTInteger)
	layer_out.CreateField(field_new)

	field_new = ogr.FieldDefn('PathRow', ogr.OFTString)
	field_new.SetWidth(10)
	layer_out.CreateField(field_new)

	field_new = ogr.FieldDefn('Day', ogr.OFTDate)
	field_new.SetWidth(10)
	layer_out.CreateField(field_new)

	field_new = ogr.FieldDefn('Source', ogr.OFTString)
	field_new.SetWidth(10)
	layer_out.CreateField(field_new)
	
def sub__update_field_value(f_vct,layer_out):
	#ls_nfd = ['PathRow','Day','Source']
	name_scene = f_vct.split('/')[-2]
	snr,pr,dt = name_scene.split('_')
	sensor = G_dic_sensor[snr]
	pathrow = pr[1:4] + pr[-3:]
	date = dt[:4] + '-' + dt[4:6] + '-' + dt[-2:]
	#print sensor,pathrow,date

	n_ft = layer_out.GetFeatureCount()
	
	for i in range(n_ft):
		ft_i = layer_out.GetFeature(i)
		
		ft_i.SetField('PathRow', pathrow)
		ft_i.SetField('Source', sensor)
		ft_i.SetField('Day', date)
		layer_out.SetFeature(ft_i)
	
	
	
#---------------------------------------------------------------------- by region
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
	
	
def sub__resotre_fields(lyr_ref,layer_out):
	dfn_lyr_ref = lyr_ref.layer.GetLayerDefn()  
	n_field_ref = dfn_lyr_ref.GetFieldCount()
	i_area = 9999
	ls_fields = []
	for i in range(n_field_ref):
		#---- retrieve old field
		fd_ref =dfn_lyr_ref.GetFieldDefn(i)
		
		name_fd = fd_ref.GetNameRef()
		if name_fd in ['Area','Altitude','�������']: continue
		type_field = fd_ref.GetType()#fd_ref.GetFieldTypeName(fd_ref.GetType())
		
		width_fd = fd_ref.GetWidth()
		prcn_fd = fd_ref.GetPrecision()
		ls_fields.append(name_fd)
		#print name_fd,fd_ref.GetFieldTypeName(fd_ref.GetType()),width_fd,prcn_fd
		
		#---- generate new field
		dfn_field = ogr.FieldDefn(name_fd, type_field)
		dfn_field.SetWidth(width_fd)
		dfn_field.SetPrecision(prcn_fd)
		layer_out.CreateField(dfn_field)
	
	for name_fd in ['PathRow','Day','Source','Area','Perimeter']:
		if name_fd in ls_fields: continue
		_type = ogr.OFTReal
		if name_fd in ['PathRow','Day','Source']:
			_type = ogr.OFTString
			
		dfn_field = ogr.FieldDefn(name_fd, _type)
		ls_fields.append(name_fd)
		dfn_field.SetPrecision(10)
		if name_fd in ['PathRow','Day','Source']: dfn_field.SetWidth(10)
		layer_out.CreateField(dfn_field)
	
	return layer_out.GetLayerDefn(),ls_fields
	
	
def dissolve_polygons_shp(f_merged,f_ref,f_dislv):
	ref_merge = GS.geo_shape.open(f_merged)
	lyr_merge = ref_merge.get_layer(0)
	proj_in = lyr_merge.spatial_ref

	ref_ref = GS.geo_shape.open(f_ref)
	lyr_ref = ref_ref.get_layer(0)
	
	#---- create new
	ogr.RegisterAll()
	driver = ogr.GetDriverByName("ESRI Shapefile")
	if os.access(f_dislv, os.F_OK):
		driver.DeleteDataSource(f_dislv)
		
	ds_out = driver.CreateDataSource(f_dislv)
	layer_out = ds_out.CreateLayer("dissolved", srs = proj_in)

	dfn_layer,ls_fields = sub__resotre_fields(lyr_ref,layer_out)

	dic_merge_cn = sub__index_feature_by_field(lyr_merge)
	dic_ref_cn = sub__index_feature_by_field(lyr_ref)

	ks = dic_merge_cn.keys()
	ks.sort()
	for k in ks:
		ls_i = dic_merge_cn[k]
		#print k,len(ls_i)
		i_ft = ls_i.pop(0)
		
		#---- dissolve
		ft_mgs = lyr_merge.layer.GetFeature(i_ft)
		geom_dsv = ft_mgs.GetGeometryRef()

		i_max = i_ft
		area_max = 0.0
		while ls_i:
			i_ft = ls_i.pop(0)
			ft_mg = lyr_merge.layer.GetFeature(i_ft)
			geom_mg = ft_mg.GetGeometryRef()

			if not geom_mg.IsValid(): 
				geom_mg = geom_mg.Buffer(0.0)
				print 'fixing geom at ui =',k
			r_area = geom_mg.Area()
			if area_max < r_area:
				i_max = i_ft
				area_max = r_area
			geom_dsv = geom_dsv.Union(geom_mg)

			ft_mg.Destroy()
		#---- make new feature(geometry, field)
		ft_out = ogr.Feature(dfn_layer)
		ft_out.SetGeometry(geom_dsv)

		r_area = geom_dsv.Area() / 1000000.0
		r_perimeter = geom_dsv.Boundary().Length() / 1000.0
		
		i_ft_ref = dic_ref_cn[k]
		ft_ref = lyr_ref.layer.GetFeature(i_ft_ref[0])
		ft_mg_tmp = lyr_merge.layer.GetFeature(i_max)
		for fd in ls_fields:
			if fd == 'Area':
				cnt_fd = r_area
			elif fd == 'Perimeter':
				cnt_fd = r_perimeter
			elif fd in ['PathRow','Day','Source']:
				cnt_fd = ft_mg_tmp.GetField(fd)
			else:
				cnt_fd = ft_ref.GetField(fd)
			ft_out.SetField(fd, cnt_fd)
		ft_mg_tmp.Destroy()
		layer_out.CreateFeature(ft_out)

		ft_mgs.Destroy()
		ft_out.Destroy()

	ds_out.Destroy()

def merge_lakes_shp(p_out,p_vector):
	name_wi = lib_Global_const.G_water_index
	f_merged = p_vector + 'merged_' + name_wi[:-4] + '.shp'
	f_ref = p_vector + lib_Global_const.G_base_shp[:-4] + '_ui.shp'
	#'''
	ls_pr = lib_IO.getDirList( p_out ,'p...r...')

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
	#print fs_lake_shp[0]
	
	for f in fs_lake_shp[1:]:
		cmd_ogr = 'ogr2ogr -update -append ' + f_merged + ' ' + f
		_rs = lib_IO.run_exe(cmd_ogr)
		#print f
	print f_merged
	#'''

	f_dislv = p_vector + 'dissolved_' + name_wi[:-4] + '.shp'
	dissolve_polygons_shp(f_merged,f_ref,f_dislv)
	

	
	
	
	
	
