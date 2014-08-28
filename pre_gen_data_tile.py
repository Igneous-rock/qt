import ogr,gdal,osr
import os
import lib_IO, lib_Global_const
import geo_shape as GS
import geo_raster as GR
import numpy as np
from scipy.ndimage.morphology import binary_fill_holes
import lib_amerl_c

def get_dic_pr_pscene(p_out):
	dic_pr_pscene = {}
	pathrows = os.listdir(p_out)
	for pathrow in pathrows:
		p_pr = p_out + '/' + pathrow
		scenes = os.listdir(p_pr)
		p_out_scene = p_pr + '/' + scenes[0]
		dic_pr_pscene[pathrow] = p_out_scene
	return dic_pr_pscene
#-------------------------------------------------------------- scene
def sub__add_fields(layer_out):
	field_new = ogr.FieldDefn('PValue', ogr.OFTInteger)
	layer_out.CreateField(field_new)
	
	field_new = ogr.FieldDefn('PathRow', ogr.OFTString)
	field_new.SetWidth(10)
	layer_out.CreateField(field_new)
	
def sub__update_field_value(f_vct,layer_out,pathrow):
	pr = pathrow[1:4] + pathrow[-3:]

	n_ft = layer_out.GetFeatureCount()
	for i in range(n_ft):
		ft_i = layer_out.GetFeature(i)
		
		ft_i.SetField('PathRow', pr)
		layer_out.SetFeature(ft_i)

def gen_tmp_extent(f_wi,f_temp):
	ref_wi = GR.geo_raster.open(f_wi)
	bnd_wi = ref_wi.get_band()
	m_wi = bnd_wi.read()

	m_out = np.zeros_like(m_wi)
	m_out[m_wi > -9999] = 1
	m_fill = binary_fill_holes(m_out)
	m_out = lib_amerl_c.remove_small_objects(m_fill.astype(np.int16),100,0,4)
	GR.write_raster(f_temp, ref_wi.geo_transform, ref_wi.projection, m_out.astype(np.int8),1)
	return ref_wi.geo_transform,ref_wi.projection



		
		
def get_data_extent(pathrow,p_scene):
	f_img = p_scene + '/mask.img'
	f_img_tmp = p_scene + '/data_ext_tmp.img'
	geo_transform,projection = gen_tmp_extent(f_img,f_img_tmp)

	f_vct_tmp = p_scene + '/data_extent_ori.shp'
	f_vct = p_scene + '/data_extent.shp'
	
	ds_img = gdal.Open(f_img_tmp)
	band = ds_img.GetRasterBand(1)
	
	driver = ogr.GetDriverByName("ESRI Shapefile")
	if os.path.exists(f_vct_tmp):
		driver.DeleteDataSource(f_vct_tmp)
		
	sr_in = osr.SpatialReference()
	sr_in.ImportFromWkt(projection)
	ds_out = driver.CreateDataSource(f_vct_tmp)
	layer_out = ds_out.CreateLayer("polygonized", srs=sr_in)
	sub__add_fields(layer_out)
	
	gdal.Polygonize( band, None, layer_out, 0, [], callback=None )
	
	sub__update_field_value(f_vct,layer_out,pathrow)
	
	ds_out.Destroy()
	del ds_img

	#-------------- simplify and reprojct
	cmd_ogr = 'ogr2ogr -overwrite -where \"PValue=1\"  -t_srs "+proj=aea +lat_1=25.0 +lat_2=47.0 +lon_0=105.0 +x_0=0 +y_0=0 +datum=WGS84" ' + f_vct + ' ' + f_vct_tmp

	_rs = lib_IO.run_exe(cmd_ogr)
	print f_vct
	
	driver = ogr.GetDriverByName("ESRI Shapefile")
	driver.DeleteDataSource(f_vct_tmp)
	os.remove(f_img_tmp)
	
	
def gen_extent_scene(dic_pr_pscene):
	pathrows = dic_pr_pscene.keys()
	pathrows.sort()
	for pathrow in pathrows:
		p_scene = dic_pr_pscene[pathrow]
		#if pathrow<>'p139r036':continue
		get_data_extent(pathrow,p_scene)
		#return


#-------------------------------------------------------------------- all scenes
def combine_all_extent(dic_pr_pscene,p_vector):
	f_vct_ext = p_vector + '/requires/image_extent.shp'
	f_ref = p_vector + '/2000_Merge_ui.shp'
	
	ref_ref = GS.geo_shape.open(f_ref)
	lyr_ref = ref_ref.get_layer(0)
	proj_in = lyr_ref.spatial_ref
	#---- create new
	ogr.RegisterAll()
	driver = ogr.GetDriverByName("ESRI Shapefile")
	if os.access(f_vct_ext, os.F_OK):
		driver.DeleteDataSource(f_vct_ext)
		
	ds_out = driver.CreateDataSource(f_vct_ext)
	layer_out = ds_out.CreateLayer("data_extent", srs = proj_in)

	#---- generate new field
	dfn_field = ogr.FieldDefn('PR', ogr.OFTInteger)
	layer_out.CreateField(dfn_field)
	dfn_layer = layer_out.GetLayerDefn()
	
	#---- batch 
	pathrows = dic_pr_pscene.keys()
	pathrows.sort()
	for pathrow in pathrows:
		p_scene = dic_pr_pscene[pathrow]
		f_vct = p_scene + '/data_extent.shp'
		
		ref_scn = GS.geo_shape.open(f_vct)
		lyr_scn = ref_scn.get_layer(0)
		
		'''
		count = lyr_scn.layer.GetFeatureCount()
		print pathrow,count
		continue
		'''
		ft = lyr_scn.layer.GetFeature(0)
		geom = ft.GetGeometryRef()
		pr = pathrow[1:4] + pathrow[-3:]
		
		#print pathrow,geom.IsSimple()
		geom_simp = geom.Simplify(100)
		
		ft_out = ogr.Feature(dfn_layer)
		ft_out.SetGeometry(geom_simp)
		ft_out.SetField('PR', pr)
		layer_out.CreateFeature(ft_out)
		ft_out.Destroy()
	ds_out.Destroy()
	print f_vct_ext



def gen_data_tile(dic_data_path):
	p_out = dic_data_path['path_out']
	p_vector = dic_data_path['path_vector']
	
	dic_pr_pscene = get_dic_pr_pscene(p_out)
	gen_extent_scene(dic_pr_pscene)
	
	combine_all_extent(dic_pr_pscene,p_vector)




#--------------------------------------------------------------
if __name__ == '__main__':
	import time
	a = time.clock()
	dic_data_path = lib_Global_const.G_dic_data_path
	gen_data_tile(dic_data_path)
	print time.clock() -a
	print 'done'
