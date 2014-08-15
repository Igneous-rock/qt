import numpy as np
cimport numpy as np
DTYPE = np.int16
ctypedef np.int16_t DTYPE_t
import geo_raster as GR
import ogr,gdal,osr
import os
import lib_IO
cimport cython
@cython.boundscheck(False)
#----------------------------------------------------------------------  encoding
def vectorize_scene(f_img,f_ref,f_vct):
	f_temp,proj = polygonize_scene(f_img,f_vct)
	simplify_polygons(proj,f_temp,f_vct)
	transform_proj(proj,f_ref,f_vct)
	

def polygonize_scene(f_img,f_vct):
	f_temp = os.path.split(f_vct)[0] + '/temp.shp'
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
	ds_img = None
	return f_temp,projection
	
def simplify_polygons(projection,f_temp,f_vct):
	driver = ogr.GetDriverByName("ESRI Shapefile")

	cmd_ogr = 'ogr2ogr -overwrite -simplify 30 -where \"Code_uniq>0\" -f \"ESRI Shapefile\" ' + f_vct + ' ' + f_temp
	
	_rs = lib_IO.run_exe(cmd_ogr)
	print f_vct

	f_prj = f_vct[:-3] + 'prj'
	fo_prj = open(f_prj,'w');
	fo_prj.write(projection)
	fo_prj.close()

	driver.DeleteDataSource(f_temp)
	

def transform_proj(proj_srs,f_ref,f_vct):
	import geo_shape as GS
	f_dst = os.path.split(f_vct)[0] + '/test.shp'
	sr_srs = osr.SpatialReference()
	sr_srs.ImportFromWkt(proj_srs)

	#sr_dst = osr.SpatialReference()
	#sr_dst.ImportFromProj4("+proj=aea +lat_1=25.0 +lat_2=47.0 +lon_0=105.0 +x_0=0 +y_0=0 +datum=WGS84") 
	
	lyr_ref = GS.geo_shape.open(f_ref).get_layer(0)
	sr_dst = lyr_ref.spatial_ref

	trans_proj = osr.CoordinateTransformation(sr_srs, sr_dst)

	lyr_srs = GS.geo_shape.open(f_vct).get_layer(0)
	
	driver = ogr.GetDriverByName("ESRI Shapefile")
	if os.access(f_dst, os.F_OK):
		driver.DeleteDataSource(f_dst)

	ds_dst = driver.CreateDataSource(f_dst)
	layer_dst = ds_dst.CreateLayer("tile_albers", geom_type=ogr.wkbPolygon)
	
	# add fields
	lyr_defn_srs = lyr_srs.layer_defn
	n_field = lyr_defn_srs.GetFieldCount()
	for i in range(n_field):
		field_defn = lyr_defn_srs.GetFieldDefn(i)
		layer_dst.CreateField(field_defn)

	# get the output layer's feature definition
	lyr_defn_dst = layer_dst.GetLayerDefn()
	
	n_ft = lyr_srs.feature_count
	for i in xrange(n_ft):
		ft_srs = lyr_srs.layer.GetFeature(i)
		geom_cont = ft_srs.GetGeometryRef()
		geom_cont.Transform(trans_proj)
		
		ft_dst = ogr.Feature(lyr_defn_dst)
		ft_dst.SetGeometry(geom_cont)
		
		for j in range(n_field):
			ft_dst.SetField(lyr_defn_dst.GetFieldDefn(j).GetNameRef(), ft_srs.GetField(j))

		layer_dst.CreateFeature(ft_dst)
		ft_dst.Destroy()
		ft_srs.Destroy()
	

	f_prj = f_dst[:-3] + 'prj'
	fo_prj = open(f_prj,'w')
	#sr_dst.MorphToESRI()
	fo_prj.write(sr_srs.ExportToPrettyWkt())
	fo_prj.close()
	
	ds_dst.Destroy()
	
	
	
	
	
	
	
	
	
	
	
