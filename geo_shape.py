#-*- coding: cp936 -*- 
try:
	from osgeo import gdal, ogr, osr
except ImportError:
	import gdal, ogr, osr
import re,os, numpy
import numpy as np
import geo_raster as GR


class geo_layer():
	def __init__(self, shapefile, layer):
		self.shapefile = shapefile
		self.layer = layer
		layer.ResetReading()
		self.feature_count = layer.GetFeatureCount()
		self.layer_defn = layer.GetLayerDefn()
		self.spatial_ref = layer.GetSpatialRef()
		self.extent = layer.GetExtent()

		
	def select_by_pathrow(self, pathrow,f_out):
		driver = ogr.GetDriverByName("ESRI Shapefile")
		if os.access(f_out, os.F_OK):
			driver.DeleteDataSource(f_out)
		
		sql = '\"PR\" = \"' + pathrow + '\"'
		self.layer.SetAttributeFilter(sql)
		
		data_source = driver.CreateDataSource(f_out)
		layer = data_source.CopyLayer(self.layer,'tile_data_bounding')
		data_source.Destroy()
		self.layer.ResetReading()
		
	def select_by_shapefile(self, f_shp,f_out):
		self.layer.ResetReading()
		driver = ogr.GetDriverByName("ESRI Shapefile")
		if os.access(f_out, os.F_OK):
			driver.DeleteDataSource(f_out)
		
		ds_contour = ogr.Open(f_shp)
		layer_cont = ds_contour.GetLayer()
		feat = layer_cont.GetNextFeature()
		geom_cont = feat.GetGeometryRef()
		self.layer.SetSpatialFilter(geom_cont)
	
		data_source = driver.CreateDataSource(f_out)
		layer = data_source.CopyLayer(self.layer,'data_selected')
		data_source.Destroy()
		self.layer.ResetReading()
		
	def fill_by_shapefile(self, f_img,f_mask,nodata = -9999, field = ''):
		self.layer.ResetReading()

		ref_img = GR.geo_raster.open(f_img)

		size = [ref_img.height, ref_img.width]
		geo_transform = ref_img.geo_transform
		projection = ref_img.projection
		ras_mask = GR.geo_raster.create(f_mask, size, geo_transform, projection, 3).raster
		if field == '':
			gdal.RasterizeLayer(ras_mask, [1], self.layer, burn_values=[1])
			#gdal.RasterizeLayer(ras_mask, [1], self.layer, None, None, [1], ['ALL_TOUCHED=TRUE'])
		else:
			gdal.RasterizeLayer(ras_mask, [1], self.layer,options = ["ATTRIBUTE=" + field])
			
	def dic_all_fields(self,fd_ui,lst_exclude = []):
		dfn_lyr_ref = self.layer.GetLayerDefn()  
		n_fd = dfn_lyr_ref.GetFieldCount()
		lst_fields = []
		lst_exclude.append(fd_ui)
		for i in range(n_fd):
			#---- retrieve old field
			fd_ref =dfn_lyr_ref.GetFieldDefn(i)
			name_fd = fd_ref.GetNameRef()
			if not name_fd in lst_exclude:
				lst_fields.append(name_fd)
			
		dic_ui_other = {}
		n_ft = self.layer.GetFeatureCount()
		for i in xrange(n_ft):
			ft = self.layer.GetFeature(i)
			ui = ft.GetField(fd_ui)
			lst_fd = []
			for name_fd in lst_fields:
				cnt_fd = ft.GetField(name_fd)
				lst_fd.append(cnt_fd)
			dic_ui_other[ui] = lst_fd
		return dic_ui_other,lst_fields
	
	def get_fields_header(self):
		dfn_lyr = self.layer.GetLayerDefn()  
		nfd = dfn_lyr.GetFieldCount()
		lst_fds = []
		for i in range(nfd):
			fd_ref =dfn_lyr.GetFieldDefn(i)
			lst_fds.append(fd_ref.GetNameRef())
		return lst_fds
	
	def add_field(self,field,name_ui,dic_ui_fd,i_dic,dic_nm_setting):
		lst_fds = self.get_fields_header()
		if not field in lst_fds:
			dfn_fd = ogr.FieldDefn(field, dic_nm_setting['type'])
			dfn_fd.SetWidth(dic_nm_setting['width'])
			dfn_fd.SetPrecision(dic_nm_setting['precision'])
			self.layer.CreateField(dfn_fd)
		
		n_ft = self.layer.GetFeatureCount()
		for i in xrange(n_ft):
			ft = self.layer.GetFeature(i)
			k_ui = ft.GetField(name_ui)
			try:
				value = dic_ui_fd[k_ui][i_dic]
			except:
				print name_ui,k_ui,'doesn\'t have',field,'data'
				value = False
			if dic_nm_setting['type'] == ogr.OFTReal:
				cnt_fd = float(value)
			elif dic_nm_setting['type'] == ogr.OFTInteger:
				cnt_fd = int(value)
			else:
				cnt_fd = value
			ft.SetField(field, cnt_fd)
			self.layer.SetFeature(ft)
			ft.Destroy()
	
	
	
	
class geo_shape():
	def __init__(self, f, shapefile):
		self.filepath = f
		self.shapefile = shapefile
		self.layer_num = self.shapefile.GetLayerCount()

	@classmethod
	def open(cls, f,updating=False):
		gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8","NO")
		gdal.SetConfigOption("SHAPE_ENCODING","")
		ogr.RegisterAll()
		return cls(f, ogr.Open(f,update=updating))
	

	def get_layer(self, layer_num=0):
		if isinstance(layer_num, int):
			if not (0 <= layer_num < self.layer_num):
				raise Exception('layer index is not availible (layers %d)' % self.layer_num)
			return geo_layer(self, self.shapefile.GetLayerByIndex(layer_num))
		elif isinstance(layer_num, list):
			return geo_layer(self, self.shapefile.GetLayerByName(layer_num))
		raise Exception('layer index is not availible (layers %d)' % self.layer_num)
		

def unifying_code(f_qtv, f_qtv_fix):
	lyr_ref = geo_shape.open(f_qtv).get_layer(0)
	
	driver = ogr.GetDriverByName("ESRI Shapefile")
	if os.access(f_qtv_fix, os.F_OK):
		driver.DeleteDataSource(f_qtv_fix)
		
	ds_fix = driver.CreateDataSource(f_qtv_fix)
	layer_fix = ds_fix.CopyLayer(lyr_ref.layer,'code_uniq')

	field_df = ogr.FieldDefn('Code_uniq', ogr.OFTInteger)
	layer_fix.CreateField(field_df)
	
	n_ft = layer_fix.GetFeatureCount()
	for i in xrange(n_ft):
		ft_fix = layer_fix.GetFeature(i)
		ft_fix.SetField('Code_uniq',i+1001)
		layer_fix.SetFeature(ft_fix)
	ds_fix.Destroy()
	print f_qtv_fix
	
	

	
	
	
	
	
	
	
	
	

	
	
	