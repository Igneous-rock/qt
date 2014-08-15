
from osgeo import gdal, ogr, osr
import re, numpy

class geo_band():
	'''A raster band'''

	def __init__(self, raster, band):
		self.raster = raster
		self.band = band
		self.description = band.GetDescription()
		self.names = band.GetRasterCategoryNames()
		self.width = band.XSize
		self.height = band.YSize
		self.size = [self.height, self.width]
		self.buf_rows = None
		self.buf_row_start = -1
		self.nodata = band.GetNoDataValue()
		self.pixel_type = band.DataType
		self.color_table = band.GetColorTable()

	def read_location(self, x, y, row_num=6):
		'''Read a cell at given coordinate'''

		_col, _row = self.raster.to_cell(x, y)
		return self.read_cell(_col, _row, row_num)

	def is_cached(self, row):
		if not (0 <= row < self.height):
			return False

		if self.buf_rows == None or self.buf_row_start < 0 or not (self.buf_row_start <= row < self.buf_row_start + self.buf_rows.shape[0]):
			return False

		return True

	def read_cell(self, col, row, row_num=6):
		'''Read a cell at given col/row'''

		if col < 0 or row < 0 or col >= self.width or row >= self.height:
			return None

		if not self.is_cached(row):
			self.read_rows(row, row_num)

		return self.buf_rows[row - self.buf_row_start, col]

	def read_rows(self, row, row_num=6):
		'''Read rows from the raster band and cache them'''

		del self.buf_rows
		self.buf_rows = None

		_rows = row_num
		if row + _rows > self.height:
			_rows = self.height - row

		self.buf_rows = self.band.ReadAsArray(0, row, self.width, _rows, self.width, _rows)
		self.buf_row_start = row

		return self.buf_rows

	def read(self):
		'''Read all the raster data'''
		return self.read_rows(0, self.height)

	def write(self, rows, x_offset=0, y_offset=0):
		'''Write a block to the band'''
		self.band.WriteArray(rows, x_offset, y_offset)
		self.band.FlushCache()


class geo_raster():
	def __init__(self, f, raster):
		self.filepath = f
		self.raster = raster
		self.init_vars()

	@classmethod
	def open(cls, f, update=False):
		if update:
			return cls(f, gdal.Open(f, gdal.GA_Update))

		return cls(f, gdal.Open(f))

	@classmethod
	def create(cls, f, size, geo_transform, proj, pixel_type=gdal.GDT_Byte, driver='GTiff', nodata=None, color_table=None):
		if f.lower().endswith('.img'):
			driver = 'HFA'

		_driver = gdal.GetDriverByName(driver)
		_size = len(size) == 2 and [1] + size or size

		_img = _driver.Create(f, _size[2], _size[1], _size[0], pixel_type)
		for _b in xrange(_size[0]):
			_band = _img.GetRasterBand(_b + 1)

			if nodata != None:
				_band.SetNoDataValue(nodata)
			if color_table != None:
				_band.SetColorTable(color_table)

		_img.SetGeoTransform(geo_transform)
		proj and _img.SetProjection(proj)

		return cls(f, _img)

	def sub_datasets(self):
		return self.raster.GetSubDatasets()

	def get_subdataset(self, band):
		for _n, _d in self.raster.GetSubDatasets():
			if _n.endswith(band):
				return geo_raster.open(_n)

		return None

	def init_vars(self):
		self.geo_transform = self.raster.GetGeoTransform()
		self.band_num = self.raster.RasterCount
		self.width = self.raster.RasterXSize
		self.projection = self.raster.GetProjection()
		self.height = self.raster.RasterYSize
		self.size = [self.band_num, self.height, self.width]
		self.cell_size_x = self.geo_transform[1]
		self.cell_size_y = self.geo_transform[5]
		self.cell_size = self.cell_size_x
		self.projection_obj = osr.SpatialReference()
		self.projection_obj.ImportFromWkt(self.projection)

	def to_cell(self, x, y):
		'''Convert coordinate to col and row'''

		_g = self.geo_transform
		return int((x - _g[0]) / _g[1]), int((y - _g[3]) / _g[5])

	def to_location(self, col, row):
		'''Convert col and row to coordinate'''

		_g = self.geo_transform
		_col = col + 0.5
		_row = row + 0.5

		return _g[0] + _g[1] * _col + _g[2] * _row, _g[3] + _g[4] * _col + _g[5] * _row

	def get_band(self, band_num=1):
		if not (1 <= band_num <= self.band_num):
			raise Exception('band index is not availible (bands %d)' % self.band_num)
		return geo_band(self, self.raster.GetRasterBand(band_num))

	def write_bands(self, img):
		'''Write a 3D block to each band of the image'''
		for _b in xrange(self.band_num):
			_band = self.raster.GetRasterBand(_b + 1)
			_band.WriteArray(img[_b, :, :])
			_band.FlushCache()

	def reproject(self, proj, x, y):
		return self.project_to(proj, x, y)

	def project_to(self, proj, x, y):
		_pt = ogr.Geometry(ogr.wkbPoint)

		_pt.SetPoint_2D(0, x, y)
		_pt.AssignSpatialReference(self.projection_obj)
		_pt.TransformTo(proj)
		_pt = _pt.GetPoint_2D()

		return _pt

	def project_from(self, proj, x, y):
		_pt = ogr.Geometry(ogr.wkbPoint)

		_pt.SetPoint_2D(0, x, y)
		_pt.AssignSpatialReference(proj)
		_pt.TransformTo(self.projection_obj)
		_pt = _pt.GetPoint_2D()

		return _pt

def write_raster(f, geo_transform, proj, img, pixel_type=gdal.GDT_Byte, driver='GTiff', nodata=None, color_table=None):
	if f.lower().endswith('.img'):
		driver = 'HFA'

	_driver = gdal.GetDriverByName(driver)

	_size = img.shape
	if len(_size) == 2:
		_img = _driver.Create(f, _size[1], _size[0], 1, pixel_type)

		_band = _img.GetRasterBand(1)
		if color_table != None:
			_band.SetColorTable(color_table)
		if nodata != None:
			_band.SetNoDataValue(nodata)
		_band.WriteArray(img)
		_band.FlushCache()
	else:
		_img = _driver.Create(f, _size[2], _size[1], _size[0], pixel_type)
		for _b in xrange(_size[0]):
			_band = _img.GetRasterBand(_b + 1)

			if nodata != None:
				_band.SetNoDataValue(nodata)
			if color_table != None:
				_band.SetColorTable(color_table)
			_band.WriteArray(img[_b, :, :])
			_band.FlushCache()

	_img.SetGeoTransform(geo_transform)
	proj and _img.SetProjection(proj)

def map_colortable(cs):
	_color_tables = gdal.ColorTable()
	for i in xrange(256):
		if i in cs:
			_color_tables.SetColorEntry(i, cs[i])

	return _color_tables

def load_colortable(f):
	_colors = {}
	for _l in open(f).read().splitlines():
		_vs = re.split('\s+', _l)
		if len(_vs) != 2:
			print 'ignore', _l
			continue

		_colors[float(_vs[0])] = tuple([int(_v) for _v in _vs[1].split(',')])

	return map_colortable(_colors)

def proj_from_epsg(code=4326):
	_proj = osr.SpatialReference()
	_proj.ImportFromEPSG(code)

	return _proj

if __name__ == '__main__':
	import sys

	_r = geo_raster(sys.argv[1])
	print _r.geo_transform
	print _r.raster.RasterCount, _r.width, _r.height
	print _r.cell_size_x, _r.cell_size_y, _r.cell_size

	_b = _r.get_band(1)
	print _b.read_cell(1, 1)
	print _b.read_cell(0, 0)
	print _b.read_location(-1667939.50, 1770575.03)
	_x, _y = _b.to_location(0, 0)
	print _x, _y
	print _b.to_cell(_x, _y)
	print dir(_b.band)
	print _b.band.GetRasterColorTable().GetCount()
	_color_table = _b.band.GetRasterColorTable()
	print _color_table.GetCount()
	#for i in xrange(_color_table.GetCount()):
		#print str(i) + ':' + str(_color_table.GetColorEntry(i))

	_tt = gdal.ColorTable()
	_tt.SetColorEntry(0, (0, 0, 0, 255))

