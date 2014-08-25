import numpy as np
cimport numpy as np
DTYPE = np.int16
ctypedef np.int16_t DTYPE_t
import geo_raster as GR
cimport cython
@cython.boundscheck(False)
#------------------------------------------------------------- 
def get_lake_dem(pr_cur,f_dem,f_mask,dic_ui_wopr,dic_ui_dem,dic_ui_overlaps):
	cdef np.ndarray[DTYPE_t, ndim=2] m_mask = GR.geo_raster.open(f_mask).get_band().read()
	cdef np.ndarray[DTYPE_t, ndim=2] m_dem  = GR.geo_raster.open(f_dem).get_band().read()
	
	cdef unsigned int ext_row = m_mask.shape[0]
	cdef unsigned int ext_col = m_mask.shape[1]
	cdef unsigned int row, col
	
	dic_ui_vs = {}
	cdef int v_snow
	for row in xrange(1,ext_row-1):
		for col in xrange(1,ext_col-1):
			v_mask = m_mask[row,col]
			if v_mask <= 0:continue
			
			if v_mask in dic_ui_vs:
				dic_ui_vs[v_mask].append(m_dem[row,col])
			else:
				dic_ui_vs[v_mask] = [m_dem[row,col]]
	
	del m_mask,m_dem
	uis = dic_ui_vs.keys()
	for ui in uis:
		if dic_ui_wopr[ui][0] == 'within':
			pr_chose = dic_ui_wopr[ui][1][0]
			if pr_cur == pr_chose: dic_ui_dem[ui] = int(np.median(dic_ui_vs[ui]))
		else:
			if ui in dic_ui_overlaps:
				v_dem,v_len = dic_ui_overlaps[ui]
				if v_len < len(dic_ui_vs[ui]):
					dic_ui_overlaps[ui] = [v_dem,v_len]
			else:
				dic_ui_overlaps[ui] = [int(np.median(dic_ui_vs[ui])),len(dic_ui_vs[ui])]
				

	
	
	
	
	
	
	
	
	
	
	
	