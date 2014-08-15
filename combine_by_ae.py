#-*- coding: cp936 -*- 
def sub__get_rectangle(geom):
	env = geom.GetEnvelope()
	r_area_rect = float((env[1] - env[0])) * (env[3] - env[2]) / 1000000.0
	return r_area_rect

def gen_dic_ui_metrics(f_rst):
	ref_rst = GS.geo_shape.open(f_rst)
	lyr_rst = ref_rst.get_layer(0)
	
	dic_code_metrics = {}
	n_ft_m = lyr_rst.layer.GetFeatureCount()
	for i in xrange(n_ft_m):
		ft_rst = lyr_rst.layer.GetFeature(i)
		s_code_u = ft_rst.GetField('Code_uniq')

		geom_rst = ft_rst.GetGeometryRef()
		
		r_area = geom_rst.Area() / 1000000.0
		r_perimeter = geom_rst.Boundary().Length() / 1000.0
		
		r_sdi = r_perimeter / (2 * math.sqrt(math.pi * r_area))
		r_thickness = (4 * math.pi * r_area) / (r_perimeter**2)
		
		r_area_rect = sub__get_rectangle(geom_rst)
		r_compacity = r_area_rect / r_area
		
		#r_spreading = (4 * r_area) / (math.pi * r_area_rect)
		r_in_compacity = r_area / r_area_rect

		dic_code_metrics[s_code_u] = [r_area,r_perimeter,r_thickness,r_in_compacity,r_sdi,r_compacity]
		
	return dic_code_metrics
	
def compare_metric_double(f_ref,f_mndwi,f_ndwi,i):
	dic_ua_ref   = gen_dic_ui_metrics(f_ref)
	dic_ua_mndwi = gen_dic_ui_metrics(f_mndwi)
	dic_ua_ndwi  = gen_dic_ui_metrics(f_ndwi)
	
	ks = list(set(dic_ua_mndwi.keys() + dic_ua_ndwi.keys()))
	ks.sort()
	dic_diff = {}
	for k in ks:
		if not k in dic_ua_ref:
			print k, 'not in reference'
			continue
		r_ref = dic_ua_ref[k][i]
		r_mndwi = dic_ua_mndwi[k][i] if k in dic_ua_mndwi else 0.0
		r_ndwi = dic_ua_ndwi[k][i] if k in dic_ua_ndwi else 0.0
		r_d_mndwi = (r_mndwi - r_ref) / r_ref
		r_d_ndwi = (r_ndwi - r_ref) / r_ref
		
		dic_diff[k] = [r_ref,r_mndwi,r_ndwi,r_d_mndwi,r_d_ndwi]
	return dic_diff
#-----------------------------------------------------------------------------
def sub__resotre_fields(layer_ref,layer_out):
	dfn_lyr_ref = layer_ref.GetLayerDefn()  
	n_field_ref = dfn_lyr_ref.GetFieldCount()
	i_area = 9999
	ls_fields = []
	for i in range(n_field_ref):
		#---- retrieve old field
		fd_ref =dfn_lyr_ref.GetFieldDefn(i)
		
		name_fd = fd_ref.GetNameRef()
		if name_fd in ['Altitude','Area','Perimeter','湖泊面积']: continue
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
	
	for name_fd in ['wi','Area','Perimeter']:
		if name_fd in ls_fields: continue
		_type = ogr.OFTReal
		if name_fd in ['wi']:
			_type = ogr.OFTString
			
		dfn_field = ogr.FieldDefn(name_fd, _type)
		ls_fields.append(name_fd)
		dfn_field.SetPrecision(10)
		if name_fd in ['wi']: dfn_field.SetWidth(10)
		layer_out.CreateField(dfn_field)
	
	return layer_out.GetLayerDefn(),ls_fields
	
def sub__index_feature_by_field(layer):
	n_ft_m = layer.GetFeatureCount()

	dic_code_num = {}
	for i in xrange(n_ft_m):
		ft_mg = layer.GetFeature(i)
		code_u = ft_mg.GetField('Code_uniq')
		dic_code_num[code_u] = i
		ft_mg.Destroy()
	return dic_code_num
	
#--------------------------------------------------------------------------------------
def combine_2wi(f_ref,f_mndwi,f_ndwi,f_combo):
	#---- get metrics
	dic_ui_rmnee = compare_metric_double(f_ref,f_mndwi,f_ndwi,0)

	#---- init
	ref_ref = GS.geo_shape.open(f_ref)
	lyr_ref = ref_ref.get_layer(0)
	layer_ref = lyr_ref.layer
	
	ref_mndwi = GS.geo_shape.open(f_mndwi)
	lyr_mndwi= ref_mndwi.get_layer(0)
	proj_in = lyr_mndwi.spatial_ref
	layer_mndwi = lyr_mndwi.layer

	ref_ndwi = GS.geo_shape.open(f_ndwi)
	lyr_ndwi= ref_ndwi.get_layer(0)
	layer_ndwi = lyr_ndwi.layer
	
	layer_rmn = [layer_ref, layer_mndwi, layer_ndwi]
	#'''
	#---- create new
	ogr.RegisterAll()
	driver = ogr.GetDriverByName("ESRI Shapefile")
	if os.access(f_combo, os.F_OK):
		driver.DeleteDataSource(f_combo)
		
	ds_out = driver.CreateDataSource(f_combo)
	layer_out = ds_out.CreateLayer("combine_2wi", srs = proj_in)

	dfn_layer,ls_fields = sub__resotre_fields(layer_ref,layer_out)
	#'''
	dic_cf_ref   = sub__index_feature_by_field(layer_ref)
	dic_cf_mndwi = sub__index_feature_by_field(layer_mndwi)
	dic_cf_ndwi  = sub__index_feature_by_field(layer_ndwi)
	
	dic_cf_rmn = [dic_cf_ref, dic_cf_mndwi, dic_cf_ndwi]
	dic_wi = {0:'ref',1:'mndwi',2:'ndwi'}
	
	ks = dic_ui_rmnee.keys()
	ks.sort()
	for k in ks:
		sw_mndwi = k in dic_cf_mndwi
		sw_ndwi  = k in dic_cf_ndwi
		if (not sw_mndwi) and sw_ndwi: 
			i_rmn = 2
		elif sw_mndwi and (not sw_ndwi):
			i_rmn = 1
		else:
			i_rmn = 1
			r_e_mndwi = dic_ui_rmnee[k][3]
			r_e_ndwi  = dic_ui_rmnee[k][4]
			if r_e_mndwi >= G_t_combo and r_e_mndwi > r_e_ndwi:
				i_rmn = 2
		#print k,dic_wi[i_rmn]
		ft_rmn = layer_rmn[i_rmn].GetFeature(dic_cf_rmn[i_rmn][k])
		geom_rmn = ft_rmn.GetGeometryRef()
		
		ft_out = ogr.Feature(dfn_layer)
		ft_out.SetGeometry(geom_rmn)
		r_area = geom_rmn.Area() / 1000000.0
		r_perimeter = geom_rmn.Boundary().Length() / 1000.0
		
		for fd in ls_fields:
			if fd == 'wi':
				cnt_fd = dic_wi[i_rmn]
			elif fd == 'Area':
				cnt_fd = r_area
			elif fd == 'Perimeter':
				cnt_fd = r_perimeter
			elif i_rmn == 0:
				ft_tmp = layer_rmn[1].GetFeature(dic_cf_rmn[1][k])
				cnt_fd = ft_tmp.GetField(fd)
				ft_tmp.Destroy()
			else:
				cnt_fd = ft_rmn.GetField(fd)
			ft_out.SetField(fd, cnt_fd)
		layer_out.CreateFeature(ft_out)

		ft_rmn.Destroy()
		ft_out.Destroy()

	ds_out.Destroy()
	



def combine_by_ae(p_vector):
	f_mndwi = p_vector + '/itpcas2000/dissolved_mndwi.shp'
	f_ndwi = p_vector + '/itpcas2000/dissolved_ndwi.shp'
	f_ref = p_vector + '/2000_Merge_ui.shp'
	f_combo = p_vector + '/itpcas2000/lakes_combined.shp'
	combine_2wi(f_ref,f_mndwi,f_ndwi,f_combo)
	f_sift = p_vector + '/itpcas2000/lakes_sift.shp'
	#sift_shp(f_combo,f_sift)
	
	
G_t_combo = 0.1
	
import ogr,gdal,osr
import os
import lib_IO, lib_Global_const
import geo_shape as GS
import time
import math

#--------------------------------------------------------------
if __name__ == '__main__':
	a = time.clock()
	p_vector = '/mnt/data_3t_a/jiangh/vector'
	combine_by_ae(p_vector)
	print time.clock() -a
	print 'done'