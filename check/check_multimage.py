	def index_by_key(f_pr,_field):	ref_pr = GS.geo_shape.open(f_pr)	lyr_pr = ref_pr.get_layer(0)		n_ft_m = lyr_pr.layer.GetFeatureCount()	dic_code_num = {}	for i in xrange(n_ft_m):		ft_mg = lyr_pr.layer.GetFeature(i)		code_u = str(ft_mg.GetField(_field))		if code_u in dic_code_num:			dic_code_num[code_u].append(i)		else:			dic_code_num[code_u] = [i]		ft_mg.Destroy()	return dic_code_num		def get_neighbor_pr(pathrow,dic_pr_i):	path = int(pathrow[:3])	row  = int(pathrow[3:])		ls_test = []	ls_test.append(str(path + 1) + '0' + str(row - 1))    		# 1 2 3	ls_test.append(str(path) + '0' + str(row - 1))    		    # 4   5	ls_test.append(str(path - 1) + '0' + str(row - 1))          # 6 7 8		ls_test.append(str(path + 1) + '0' + str(row))	ls_test.append(str(path - 1) + '0' + str(row))	ls_test.append(str(path + 1) + '0' + str(row + 1))	ls_test.append(str(path) + '0' + str(row + 1))	ls_test.append(str(path - 1) + '0' + str(row + 1))		ls_neighbor_pr = []	for pr in ls_test:		if pr in dic_pr_i: ls_neighbor_pr.append(pr)		return ls_neighbor_pr	def get_overlap_pr(geom_lake,lyr_pr,ls_neighbor_pr,dic_pr_i):	lst_overlap = []	for pr in ls_neighbor_pr:		li_ft = dic_pr_i[pr]		ft_pr = lyr_pr.layer.GetFeature(li_ft[0])		geom_pr = ft_pr.GetGeometryRef()				if geom_lake.Overlaps(geom_pr) or geom_lake.Within(geom_pr):			lst_overlap.append(pr)	return lst_overlapdef check_lakes_o_pr(f_rst,f_pr,nm_ref):	dic_pr_i = index_by_key(f_pr,'PR')			ref_rst = GS.geo_shape.open(f_rst)	lyr_rst = ref_rst.get_layer(0)		ref_pr = GS.geo_shape.open(f_pr)	lyr_pr = ref_pr.get_layer(0)		dic_ui_overlap = {}		n_ft = lyr_rst.layer.GetFeatureCount()	for i in xrange(n_ft):		ft_lake = lyr_rst.layer.GetFeature(i)		pathrow = ft_lake.GetField('PathRow')		ui = ft_lake.GetField('Code_uniq')		#if ui <> 2000:continue		ls_neighbor_pr = get_neighbor_pr(pathrow,dic_pr_i)				geom_lake = ft_lake.GetGeometryRef()		lst_overlap = get_overlap_pr(geom_lake,lyr_pr,ls_neighbor_pr,dic_pr_i)		dic_ui_overlap[ui] = lst_overlap			write_to_csv(f_rst,nm_ref,dic_ui_overlap)	def write_to_csv(f_rst,nm_ref,dic_ui_overlap):	p_analysis = '../txt_analysis/' 	name_rst = os.path.split(f_rst)[-1].split('_')[-1][:-4]	f_csv = p_analysis + nm_ref + '_'+ name_rst + '_multimage.csv'	writer = csv.writer(file(f_csv, 'wb'))	writer.writerow(['ui','count_multimage','pathrow...'])		ks = dic_ui_overlap.keys()	ks.sort()	for k in ks:		count = len(dic_ui_overlap[k])		writer.writerow([k,str(count)]+dic_ui_overlap[k])	print f_csv	def lake_touch_pathrow(p_vector):	f_ref = p_vector + '2000_Merge_ui.shp'	f_rst = p_vector + 'itpcas2000/lakes_sift.shp'#lakes_combined.shp'##	f_pr = p_vector + 'qt2000_tile.shp'		nm_ref = 'itpcas2000' #'niglas2005'			check_lakes_o_pr(f_rst,f_pr,nm_ref)						import time,os,csvimport lib_IOimport lib_Global_constimport ogr,gdal,osrimport geo_shape as GSif __name__ == '__main__':	a = time.clock()	lake_touch_pathrow(lib_Global_const.G_path_vector)	print time.clock() -a	print 'done'