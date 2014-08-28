import numpy as np
cimport numpy as np
DTYPE = np.int16
ctypedef np.int16_t DTYPE_t
import geo_raster as GR
cimport cython
@cython.boundscheck(False)
	
#------------------------------------------------------------- core of lake extraction
def amerl(f_wi,f_mask, f_snow,dic_para,f_amerl):
	import os
	ref_wi = GR.geo_raster.open(f_wi)

	#==== extract by thresholding 
	cdef np.ndarray[DTYPE_t, ndim=2] m_pure = spread_lake_by_seeds(f_wi,f_mask,f_snow, dic_para)
	
	#f_ndwi = os.path.split(f_wi)[0] + '/ndwi.img'
	#==== extract by segmentation
	cdef np.ndarray[DTYPE_t, ndim=2] m_lake = seg_by_watershed(m_pure,f_wi, f_snow, dic_para)
	cdef np.ndarray[DTYPE_t, ndim=2] m_out = remove_small_objects(m_lake,10,-9999)
	
	GR.write_raster(f_amerl, ref_wi.geo_transform, ref_wi.projection, m_out,3)
	print f_amerl

#============================================================= first step
def spread_lake_by_seeds(f_wi,f_mask, f_snow, dic_para):
	cdef np.ndarray[DTYPE_t, ndim=2] m_wi   = GR.geo_raster.open(f_wi).get_band().read()
	cdef np.ndarray[DTYPE_t, ndim=2] m_pure = GR.geo_raster.open(f_mask).get_band().read()
	cdef np.ndarray[DTYPE_t, ndim=2] m_snow = GR.geo_raster.open(f_snow).get_band().read()	
	
	cdef int v_nodata = dic_para['nodata']  # nodata cannot > 0
	cdef int t_pure = dic_para['pure_water']
	cdef int t_land = dic_para['land']
	cdef int t_snow = dic_para['snow']# + 2000
	
	cdef unsigned int ext_row = m_wi.shape[0]
	cdef unsigned int ext_col = m_wi.shape[1]
	cdef unsigned int out_row, out_col
	cdef unsigned int row, col, r,c
	cdef int r_off,c_off
	cdef int v_mask,v_water
	cdef int v_snow
	print 'without DEM'
	for row in xrange(1,ext_row-1):
		for col in xrange(1,ext_col-1):
			v_mask = m_pure[row,col]
			if v_mask == v_nodata: 
				continue
			elif v_mask > 0 and m_wi[row,col] < 1200:#t_land:#t_pure:
				m_pure[row,col] = 0
				m_wi[row,col] = 1
			elif v_mask == 0 and m_snow[row,col] >= t_snow:
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
def seg_by_watershed(np.ndarray[DTYPE_t, ndim=2] m_pure, f_wi, f_snow, dic_para):
	from skimage.morphology import watershed
	import os
	
	cdef int v_p 
	
	cdef np.ndarray[DTYPE_t, ndim=2] m_wi = GR.geo_raster.open(f_wi).get_band().read()

	cdef int v_nodata = dic_para['nodata']
	cdef int t_land = dic_para['land']
	cdef int t_water = dic_para['pure_water']
	cdef int t_snow = dic_para['snow']
	
	
	cdef unsigned int ext_row = m_wi.shape[0]
	cdef unsigned int ext_col = m_wi.shape[1]
	cdef unsigned int row, col
	cdef np.ndarray[DTYPE_t, ndim=2] m_mask = np.zeros_like(m_pure)

	cdef np.ndarray[DTYPE_t, ndim=2] m_snow = GR.geo_raster.open(f_snow).get_band().read()
	
	for row in xrange(1,ext_row-1):
		for col in xrange(1,ext_col-1):
			v_p = m_pure[row,col]
			if v_p >= 0:
				if m_wi[row,col] > t_water: m_wi[row,col] = t_water
				m_mask[row,col] = 1
				if v_p == 0:
					if m_wi[row,col] < t_land or m_snow[row,col] >= t_snow:
						m_pure[row,col] = 1
			#if v_p >= 0 and m_snow[row,col] < t_snow:
			#	m_mask[row,col] = 1
			#	if v_p == 0 and m_wi[row,col] < t_land: m_pure[row,col] = 1
					
			
		
	try:
		import gpu_dip
		m_sobel = gpu_dip.cuda_sobel(m_wi)
		#print 'gpu'
	except:
		from skimage.filter import sobel
		m_sobel = sobel(m_wi)
		#print 'cpu'
	del m_wi, m_snow

	cdef np.ndarray[DTYPE_t, ndim=2] m_seg = watershed(m_sobel, m_pure, mask = m_mask)
	m_seg[m_seg <= 1] = v_nodata
	return m_seg
	
#------------------------------------------------------------- fix extraction results
def fill_hole(dic_para,f_amerl,f_mndwi,f_fill_hole):
	from scipy.ndimage.morphology import binary_fill_holes
	ref_img = GR.geo_raster.open(f_amerl)
	bnd_img = ref_img.get_band()
	cdef np.ndarray[DTYPE_t, ndim=2] m_lk = bnd_img.read()
	
	cdef int t_water = dic_para['pure_water']
	cdef int t_land = dic_para['land']
	cdef unsigned int ext_row = m_lk.shape[0]
	cdef unsigned int ext_col = m_lk.shape[1]
	cdef unsigned int row, col

	cdef int v_former
	cdef int v_lake
	
	cdef np.ndarray[DTYPE_t, ndim=2] m_fill = np.zeros_like(m_lk)
	for row in xrange(ext_row):
		for col in xrange(ext_col):
			v_lake = m_lk[row,col]
			if v_lake > 0:
				m_fill[row,col] = 1
			else:
				m_fill[row,col] = 0
				
	m_filled = binary_fill_holes(m_fill)
	m_fill = m_filled.astype(np.int16) - m_fill
	del m_filled
	
	cdef np.ndarray[DTYPE_t, ndim=2] m_wi = GR.geo_raster.open(f_mndwi).get_band().read()
	
	for row in xrange(ext_row):
		for col in xrange(ext_col):
			v_lake = m_fill[row,col]
			if v_lake == 0:
				v_former = m_lk[row,col]
			else:
				m_lk[row,col] = v_former if m_wi[row,col] > t_land else 0

	geo_transform = ref_img.geo_transform
	projection = ref_img.projection
	del bnd_img,ref_img
	GR.write_raster(f_fill_hole, geo_transform, projection, m_lk, 3)
	print f_fill_hole

#------------------------------------------------------------- fix extraction results
def gen_vi(f_left,f_right,f_out):
	ref_qa = GR.geo_raster.open(f_left)
	cdef np.ndarray[DTYPE_t, ndim=2] m_left = ref_qa.get_band().read().astype(np.int16)
	cdef np.ndarray[DTYPE_t, ndim=2] m_right = GR.geo_raster.open(f_right).get_band().read().astype(np.int16)
	
	cdef unsigned int ext_row = m_left.shape[0]
	cdef unsigned int ext_col = m_left.shape[1]
	cdef unsigned int row, col
	cdef np.ndarray[DTYPE_t, ndim=2] m_vi = np.zeros((ext_row,ext_col),np.int16)

	cdef int v_left, v_right, v_vi
	
	for row in xrange(ext_row):
		for col in xrange(ext_col):
			v_left  = m_left[row,col]
			v_right = m_right[row,col]
			if v_left == -9999 or v_right == -9999:
				v_vi = -9999
			else:
				try:
					v_vi = <int>((<float>(v_left - v_right) / (v_left + v_right))* 1000.0)+1000
				except:
					v_vi = -9999
				if v_vi < 0: v_vi = -9999
			m_vi[row,col] = v_vi
			
	GR.write_raster(f_out, ref_qa.geo_transform, ref_qa.projection, m_vi, 3)
	print f_out

#---------------------------------------------------------------- generate seeds grid
def gen_seeds_grid(f_lk,f_wi,f_mask,gap = 3, nodata = -9999):
	#----gen extent
	ref_img = GR.geo_raster.open(f_lk)
	cdef np.ndarray[DTYPE_t, ndim=2] m_lk = ref_img.get_band().read()
	
	ref_mask = GR.geo_raster.open(f_mask)
	bnd_mask = ref_mask.get_band()
	cdef np.ndarray[DTYPE_t, ndim=2] m_mask = bnd_mask.read().astype(np.int16)
	cdef np.ndarray[DTYPE_t, ndim=2] m_wi = GR.geo_raster.open(f_wi).get_band().read()
	
	cdef unsigned int ext_row = m_lk.shape[0]
	cdef unsigned int ext_col = m_lk.shape[1]
	cdef unsigned int row, col
	
	cdef int v_code
	
	for row in xrange(ext_row):
		for col in xrange(ext_col):
			if m_mask[row,col] == 0 or m_wi[row,col] == -9999:
				m_mask[row,col] = nodata
			else:
				v_code = m_lk[row,col]
				if v_code > 0:
					m_mask[row,col] = v_code
				else:
					m_mask[row,col] = 0

	GR.write_raster(f_mask, ref_img.geo_transform, ref_img.projection, m_mask, 3)
	print f_mask
	

	
def remove_small_objects(np.ndarray[DTYPE_t, ndim=2] m_in, unsigned int size_min,int nodata,int sw_conn = 8):
	cdef unsigned int ext_row = m_in.shape[0]
	cdef unsigned int ext_col = m_in.shape[1]
	cdef unsigned int out_row, out_col
	cdef unsigned int row, col, r,c
	cdef int r_off,c_off
	
	cdef int v_p,count
	
	cdef np.ndarray[DTYPE_t, ndim=2] m_out = np.zeros_like(m_in)
	m_out[m_in > nodata] = 2
	
	if sw_conn == 4:
		ls_rc = [(-1, 0),(0, -1),(0, 1),(1, 0)]
	else:
		ls_rc = [(-1, -1),(-1, 0),(-1, 1),(0, -1),(0, 1),(1, -1),(1, 0),(1, 1)]

	ls_ht = []
	for out_row in xrange(1,ext_row-1):
		for out_col in xrange(1,ext_col-1):
			ls_i = [[],[]]
			v_p = m_out[out_row,out_col]
			if v_p < 2: continue
			m_out[out_row,out_col] = 1
			ls_ht.append((out_row,out_col))
			count = 0
			while(ls_ht != []):
				row,col = ls_ht.pop()
				ls_i[0].append(row)
				ls_i[1].append(col)
				count += 1
				for r_off,c_off in ls_rc:
					r = <unsigned int>(<int>row + r_off)
					c = <unsigned int>(<int>col + c_off)
					if m_out[r,c] == 2:
						m_out[r,c] = 1
						ls_ht.append((r,c))
			
			if count <= size_min: m_out[ls_i] = 0
			
	for row in xrange(ext_row):
		for col in xrange(ext_col):
			if m_out[row,col] == 0: m_in[row,col] = -9999
	return m_in
	
	
	
	
	
	
	
	
	
	
	
	
