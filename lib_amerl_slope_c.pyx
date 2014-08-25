import numpy as np
cimport numpy as np
DTYPE = np.int16
ctypedef np.int16_t DTYPE_t
import geo_raster as GR
cimport cython
@cython.boundscheck(False)
	
#------------------------------------------------------------- core of lake extraction
def amerl_slope(f_wi,f_mask, f_snow,f_slope,dic_para,f_amerl):
	import os
	ref_wi = GR.geo_raster.open(f_wi)

	#==== extract by thresholding 
	cdef np.ndarray[DTYPE_t, ndim=2] m_pure = spread_lake_by_seeds(f_wi,f_mask,f_snow,f_slope, dic_para)
	
	#f_ndwi = os.path.split(f_wi)[0] + '/ndwi.img'
	#==== extract by segmentation
	cdef np.ndarray[DTYPE_t, ndim=2] m_lake = seg_by_watershed(m_pure,f_wi, f_snow,f_slope, dic_para)
	
	GR.write_raster(f_amerl, ref_wi.geo_transform, ref_wi.projection, m_lake,3)
	print f_amerl

#============================================================= first step
def spread_lake_by_seeds(f_wi,f_mask, f_snow,f_slope, dic_para):
	cdef np.ndarray[DTYPE_t, ndim=2] m_wi   = GR.geo_raster.open(f_wi).get_band().read()
	cdef np.ndarray[DTYPE_t, ndim=2] m_pure = GR.geo_raster.open(f_mask).get_band().read()
	cdef np.ndarray[DTYPE_t, ndim=2] m_snow = GR.geo_raster.open(f_snow).get_band().read()	
	cdef np.ndarray[DTYPE_t, ndim=2] m_slope = GR.geo_raster.open(f_slope).get_band().read().astype(np.int16)
	
	cdef int v_nodata = dic_para['nodata']  # nodata cannot > 0
	cdef int t_pure = dic_para['pure_water']
	cdef int t_snow = dic_para['snow']# + 2000
	cdef int t_land = dic_para['land']
	cdef int t_slope = dic_para['slope']

	cdef unsigned int ext_row = m_wi.shape[0]
	cdef unsigned int ext_col = m_wi.shape[1]
	cdef unsigned int out_row, out_col
	cdef unsigned int row, col, r,c
	cdef int r_off,c_off
	cdef int v_mask,v_water
	cdef int v_snow
	print 'with DEM'
	for row in xrange(1,ext_row-1):
		for col in xrange(1,ext_col-1):
			v_mask = m_pure[row,col]
			if v_mask == v_nodata: 
				continue
			elif v_mask > 0 and m_wi[row,col] < 1200:#t_land:#t_pure:#
				m_pure[row,col] = 0
				m_wi[row,col] = 1
			elif v_mask == 0:
				if m_slope[row,col] >= t_slope or m_snow[row,col] >= t_snow:
					m_wi[row,col] = 1
	del m_snow
	'''
	ls_rc = [(-1, -1),(-1, 0),(-1, 1),(0, -1),(0, 1),(1, -1),(1, 0),(1, 1)]
	# at first, 11 is oridinary seeds
	#=== ls_ht is pixels meet high thd
	ls_ht = []
	for out_row in xrange(1,ext_row-1):
		for out_col in xrange(1,ext_col-1):
			v_water = m_pure[out_row,out_col]
			if v_water <= 0: continue
			ls_ht.append((out_row,out_col))
			while(ls_ht != []):
				row,col = ls_ht.pop()
				m_pure[row,col] = v_water
				for r_off,c_off in ls_rc:
					r = <unsigned int>(<int>row + r_off)
					c = <unsigned int>(<int>col + c_off)
					if m_pure[r,c] == 0 and m_wi[r,c] >= t_pure:
						ls_ht.append((r,c))
	'''
	return m_pure

#============================================================= second step
def seg_by_watershed(np.ndarray[DTYPE_t, ndim=2] m_pure, f_wi, f_snow,f_slope, dic_para):
	from skimage.morphology import watershed
	
	cdef int v_p 
	cdef np.ndarray[DTYPE_t, ndim=2] m_wi = GR.geo_raster.open(f_wi).get_band().read()

	cdef int v_nodata = dic_para['nodata']
	cdef int t_land = dic_para['land']
	cdef int t_water = dic_para['pure_water']
	cdef int t_snow = dic_para['snow']
	cdef int t_slope = dic_para['slope']
	
	cdef unsigned int ext_row = m_wi.shape[0]
	cdef unsigned int ext_col = m_wi.shape[1]
	cdef unsigned int row, col
	cdef np.ndarray[DTYPE_t, ndim=2] m_mask = np.zeros_like(m_pure)
	cdef np.ndarray[DTYPE_t, ndim=2] m_snow = GR.geo_raster.open(f_snow).get_band().read()
	cdef np.ndarray[DTYPE_t, ndim=2] m_slope = GR.geo_raster.open(f_slope).get_band().read().astype(np.int16)
	
	for row in xrange(1,ext_row-1):
		for col in xrange(1,ext_col-1):
			v_p = m_pure[row,col]
			if v_p == v_nodata:
				continue
			if m_wi[row,col] > t_water: m_wi[row,col] = t_water
			if v_p > 0:
				m_mask[row,col] = 1
			if v_p == 0:
				m_mask[row,col] = 1
				if m_wi[row,col] < t_land or m_snow[row,col] >= t_snow or m_slope[row,col] >= t_slope:
					m_pure[row,col] = 1
			
	try:
		import gpu_dip
		m_sobel = gpu_dip.cuda_sobel(m_wi)
		#print 'gpu'
	except:
		from skimage.filter import sobel
		m_sobel = sobel(m_wi)
		#print 'cpu'
	del m_wi, m_snow

	#cdef np.ndarray[DTYPE_t, ndim=2] m_slope = GR.geo_raster.open(f_slope).get_band().read().astype(np.int16)
	#m_pure[m_slope > t_slope] = 1
	#del m_slope

	cdef np.ndarray[DTYPE_t, ndim=2] m_seg = watershed(m_sobel, m_pure, mask = m_mask)
	m_seg[m_seg <= 1] = v_nodata
	return m_seg
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
