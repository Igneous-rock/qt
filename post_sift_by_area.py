#-*- coding: cp936 -*- 

def retrieve_area_by_ui(f_ref):
	ref_ref = GS.geo_shape.open(f_ref)
	lyr_ref = ref_ref.get_layer(0)
	n_ft_m = lyr_ref.layer.GetFeatureCount()

	dic_ui_area = {}
	for i in xrange(n_ft_m):
		ft_mg = lyr_ref.layer.GetFeature(i)
		ui = ft_mg.GetField('Code_uniq')
		geom = ft_mg.GetGeometryRef()
		r_area = geom.Area() / 1000000.0
		dic_ui_area[ui] = r_area
	return dic_ui_area


def sub__resotre_fields(lyr_ref,layer_out):
	dfn_lyr_ref = lyr_ref.layer.GetLayerDefn()  
	n_field_ref = dfn_lyr_ref.GetFieldCount()

	ls_fields = []
	for i in range(n_field_ref):
		#---- retrieve old field
		fd_ref =dfn_lyr_ref.GetFieldDefn(i)
		
		name_fd = fd_ref.GetNameRef()
		type_field = fd_ref.GetType()
		width_fd = fd_ref.GetWidth()
		prcn_fd = fd_ref.GetPrecision()
		ls_fields.append(name_fd)
		#---- generate new field
		dfn_field = ogr.FieldDefn(name_fd, type_field)
		dfn_field.SetWidth(width_fd)
		dfn_field.SetPrecision(prcn_fd)
		layer_out.CreateField(dfn_field)
	return layer_out.GetLayerDefn(),ls_fields
	
	
def sift_by_area(f_in,f_ref,f_sift):
	ref_mndwi = GS.geo_shape.open(f_in)
	lyr_mndwi= ref_mndwi.get_layer(0)
	proj_in = lyr_mndwi.spatial_ref

	dic_ui_area__ref = retrieve_area_by_ui(f_ref)
	dic_ui_area__rst = retrieve_area_by_ui(f_in)
	
	#---- create new
	ogr.RegisterAll()
	driver = ogr.GetDriverByName("ESRI Shapefile")
	if os.access(f_sift, os.F_OK):
		driver.DeleteDataSource(f_sift)
		
	ds = driver.CreateDataSource(f_sift)
	layer_sift = ds.CreateLayer("sift", srs = proj_in)
	
	dfn_layer, ls_fields = sub__resotre_fields(lyr_mndwi,layer_sift)

	n_ft = lyr_mndwi.layer.GetFeatureCount()
	for i in xrange(n_ft):
		ft_m = lyr_mndwi.layer.GetFeature(i)
		ui = ft_m.GetField('Code_uniq')
		if dic_ui_area__rst[ui] > G_t_area or dic_ui_area__ref[ui] > G_t_area:
			geom = ft_m.GetGeometryRef()
			
			ft_sift = ogr.Feature(dfn_layer)
			ft_sift.SetGeometry(geom)

			for fd in ls_fields:
				cnt_fd = ft_m.GetField(fd)
				ft_sift.SetField(fd, cnt_fd)

			layer_sift.CreateFeature(ft_m)
			#ft_m.Destroy()
			#ft_sift.Destroy()

	ds.Destroy()


	


def post_sift_by_area(p_vector):
	f_in = p_vector + '/itpcas2000/lakes_combined.shp'#dissolved_mndwi.shp'
	f_ref = p_vector + '/2000_Merge_ui.shp'
	#f_sift = p_vector + '/itpcas2000/sift_mndwi.shp'
	p_in,name_in = os.path.split(f_in)
	f_sift = p_in + '/' + name_in.split('_')[0] + '_sift.shp'
	
	sift_by_area(f_in,f_ref,f_sift)

G_t_area = 1.0

import ogr,gdal,osr
import os
import lib_IO
import geo_shape as GS
import time

#--------------------------------------------------------------
if __name__ == '__main__':
	a = time.clock()
	p_vector = '/mnt/data_3t_a/jiangh/vector'
	post_sift_by_area(p_vector)
	print time.clock() -a
	print 'done'