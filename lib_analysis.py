import ogr,gdal,osr
import os,csv
import geo_shape as GS
import math,time
#----------------------------------------------------------
#G_dic_metrics = {0:'Area',1:'Perimeter',2:'Thickness',3:'inCompacity',4:'SDI',5:'Compacity'}
#G_dic_km_vi = {}
#----------------------------------------------------------------------- single
def shapefile_analysis(f_ref,f_rst,nm_ref):
	p_analysis = './txt_analysis/'
	#global G_dic_km_vi
	#G_dic_km_vi = {v:k for k, v in G_dic_metrics.items()}
	
	nm_wi = os.path.split(f_rst)[-1].split('_')[-1][:-4]
	nm_data = [nm_ref,nm_wi]
	
	dic_cm_ref = gen_dic_ui_metrics(f_ref)
	dic_cm_rst = gen_dic_ui_metrics(f_rst,sw_ref = False)

	lst_metrics = ['Area','Perimeter','Thickness','inCompacity']#,'SDI','Compacity']
	for metric in lst_metrics:
		dic_Kc_DICms = compare_single_metric(nm_data,dic_cm_ref,dic_cm_rst,metric,p_analysis)
		analysis_on_factors(dic_Kc_DICms,metric,p_analysis,nm_wi)
		
	
#----------------------------------------------------------------------- 5 factors for chart
def analysis_on_factors(dic_Kc_DICms,metric,p_analysis,nm_wi):
	lst_factor = ['PathRow','path','row','year','month']
	p_interest = 0.1
	for factor in lst_factor:
		dic_f_count = sub__info_2_count(dic_Kc_DICms,metric,p_analysis,factor,p_interest)
		sub__write_csv(dic_f_count,factor,p_analysis,nm_wi,p_interest)
		
def sub__info_2_count(dic_Kc_DICms,metric,p_analysis,factor,p_interest):
	uis = dic_Kc_DICms.keys()
	dic_f_m = {}
	metric_diff = 'diff_' + metric
	for ui in uis:
		k_f = dic_Kc_DICms[ui][factor]
		if not k_f in dic_f_m:
			dic_f_m[k_f] = [dic_Kc_DICms[ui][metric_diff]]
		else:
			dic_f_m[k_f].append(dic_Kc_DICms[ui][metric_diff])
	
	
	dic_f_count = {}
	ks = dic_f_m.keys()
	for k in ks:
		dic_f_count[k] = [0,0]
		for area in dic_f_m[k]:
			#print area
			if abs(area) < p_interest:
				dic_f_count[k][0] += 1
			else:
				dic_f_count[k][1] += 1
	return dic_f_count
	
def sub__write_csv(dic_f_count,factor,p_analysis,nm_wi,p_interest):
	f_csv = p_analysis + nm_wi + '_' + factor +'.csv'
	writer = csv.writer(file(f_csv, 'wb'))
	
	writer.writerow([factor,'total','num(error>%.1f)'%p_interest,'percent'])
	ks = dic_f_count.keys()
	ks.sort()
	for k in ks:
		n_error = dic_f_count[k][1]
		total = dic_f_count[k][0] + n_error
		r_p = float(n_error) / float(total) #* 100.0
		writer.writerow([k,str(total),str(n_error), format(r_p, '.2%')])#'%5.2f\%'%r_p])
	'''
	'''
#-------------------------------------------------------------------------------------------
def compare_single_metric(nm_data,dic_cm_ref,dic_cm_rst,metric,p_analysis):
	nm_ref,nm_wi = nm_data
	
	f_csv = p_analysis + nm_ref + '_' + nm_wi + '_' + metric + '.csv'
	writer = csv.writer(file(f_csv, 'wb'))
	print f_csv
	lst_info = ['Id','Name','PathRow','path','row','year','month']
	lst_new = ['ref_'+metric,'rst_'+metric,'diff_'+metric]
	head = ['Code_uniq'] + lst_info + lst_new
	writer.writerow(head)
	
	ks = dic_cm_rst.keys()
	ks.sort()
	for k in ks:
		r_ref = dic_cm_ref[k][metric]
		r_rst = dic_cm_rst[k][metric]
		#r_diff = math.fabs(r_rst - r_ref) / r_ref
		r_diff = (r_rst - r_ref) / r_ref
		
		s_ref = '%10f'%r_ref
		s_rst = '%10f'%r_rst
		s_diff = '%10f'%r_diff
		lst_temp = []
		for info in lst_info:
			lst_temp.append(dic_cm_rst[k][info])
		lst_r_new = [r_ref,r_rst,r_diff]
		for j in range(3):
			dic_cm_rst[k][lst_new[j]] = lst_r_new[j]
		line = [k] + lst_temp + [s_ref,s_rst,s_diff]
		writer.writerow(line)
	return dic_cm_rst
	
#---------------------------------------------------------------------------------------------------	
def sub__get_rectangle(geom):
	env = geom.GetEnvelope()
	r_area_rect = float((env[1] - env[0])) * (env[3] - env[2]) / 1000000.0
	return r_area_rect
	
def gen_dic_ui_metrics(f_rst,sw_ref = True):
	ref_rst = GS.geo_shape.open(f_rst)
	lyr_rst = ref_rst.get_layer(0)
	
	lst_metrics = ['Area','Perimeter','Thickness','inCompacity']
	lst_info = ['Id','Name','PathRow','Day']
	
	dic_code_metrics = {}
	n_ft_m = lyr_rst.layer.GetFeatureCount()
	for i in xrange(n_ft_m):
		dic_temp = {}
		ft_rst = lyr_rst.layer.GetFeature(i)
		s_code_u = ft_rst.GetField('Code_uniq')

		geom_rst = ft_rst.GetGeometryRef()
		
		r_area = geom_rst.Area() / 1000000.0
		r_perimeter = geom_rst.Boundary().Length() / 1000.0
		
		r_thickness = (4 * math.pi * r_area) / (r_perimeter**2)
		
		r_area_rect = sub__get_rectangle(geom_rst)		
		r_in_compacity = r_area / r_area_rect
		
		lst_temp = [r_area,r_perimeter,r_thickness,r_in_compacity]
		for j in range(len(lst_metrics)):
			dic_temp[lst_metrics[j]] = lst_temp[j]
		if sw_ref == False:
			for info in lst_info:
				s_fd = ft_rst.GetField(info)
				if info == 'PathRow':
					dic_temp['path'] = s_fd[:3]
					dic_temp['row']  = s_fd[3:]
					dic_temp[info] = s_fd
				elif info == 'Day':
					y,m,d = s_fd.split('/')
					dic_temp['year']  = y#time.strptime('%Y', s_fd )
					dic_temp['month'] = m#time.strptime('%m', s_fd )
				else:
					dic_temp[info] = s_fd

		dic_code_metrics[s_code_u] = dic_temp
		#del dic_temp
	return dic_code_metrics
	
	
def do_csv_metrics(f_rst,p_analysis,nms_data):
	if p_analysis <> None:
		name_csv = os.path.split(f_rst)[-1][:-4]
		f_csv = p_analysis + name_csv + '.csv'
		writer = csv.writer(file(f_csv, 'wb'))
		writer.writerow(['Code_uniq','Area','Perimeter','Thickness','inCompacity','SDI','Compacity'])

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

		s_area = '%10f'%r_area
		s_perimeter = '%10f'%r_perimeter
		
		s_sdi = '%10f'%r_sdi
		s_thickness = '%10f'%r_thickness
		s_compacity = '%10f'%r_compacity
		s_in_compacity = '%10f'%r_in_compacity
		#s_spreading = '%10f'%r_spreading
		#s_spreading = format(r_spreading, 'e')
		
		if p_analysis <> None:
			writer.writerow([s_code_u,s_area,s_perimeter,s_thickness,s_in_compacity,s_sdi,s_compacity])
		dic_code_metrics[s_code_u] = [r_area,r_perimeter,r_thickness,r_in_compacity,r_sdi,r_compacity]
		
	return dic_code_metrics
	













