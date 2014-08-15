import ogr,gdal,osr
import os,csv
import geo_shape as GS
import math
#----------------------------------------------------------
G_dic_metrics = {0:'Area',1:'Perimeter',2:'Thickness',3:'inCompacity',4:'SDI',5:'Compacity'}
G_dic_km_vi = {}
#----------------------------------------------------------------------- single
def shapefile_analysis(f_ref,f_rst,nms_data):
	p_analysis = './txt_analysis/'
	global G_dic_km_vi
	G_dic_km_vi = {v:k for k, v in G_dic_metrics.items()}
	
	dic_cm_ref = do_csv_metrics(f_ref,p_analysis,nms_data)
	dic_cm_rst = do_csv_metrics(f_rst,p_analysis,nms_data)
	
	#n = len(dic_cm_rst[dic_cm_rst.keys()[0]])
	lst_metrics = ['Area']#,'Perimeter','Thickness','inCompacity','SDI','Compacity']
	for m in lst_metrics:
		dic_diff = compare_metric(nms_data,dic_cm_ref,dic_cm_rst,m,p_analysis)
		analysis_on_factors(dic_diff,p_analysis)
		

		
		
#-------------------------------------------------------------------------------------------
def compare_metric(nms_data,dic_cm_ref,dic_cm_rst,metric,p_analysis):
	i = G_dic_km_vi[metric]
	
	nm_ref,nm_wi = nms_data
	f_csv = p_analysis + nm_wi + '_' + metric + '.csv'
	writer = csv.writer(file(f_csv, 'wb'))
	writer.writerow(['Code_uniq','ref_'+metric,'rst_'+metric,'diff_'+metric])
	
	ks = dic_cm_rst.keys()
	ks.sort()
	dic_diff = {}
	for k in ks:
		r_ref = dic_cm_ref[k][i]
		r_rst = dic_cm_rst[k][i]
		#r_diff = math.fabs(r_rst - r_ref) / r_ref
		r_diff = (r_rst - r_ref) / r_ref
		
		s_ref = '%10f'%r_ref
		s_rst = '%10f'%r_rst
		s_diff = '%10f'%r_diff
		#dic_diff[k] = [s_ref,s_rst,s_diff]
		dic_diff[k] = [r_ref,r_rst,r_diff]
		writer.writerow([k,s_ref,s_rst,s_diff])
	return dic_diff

#---------------------------------------------------------------------------------------------------	
def sub__get_rectangle(geom):
	env = geom.GetEnvelope()
	r_area_rect = float((env[1] - env[0])) * (env[3] - env[2]) / 1000000.0
	return r_area_rect

	
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
	
#----------------------------------------------------------------------- double
def shapefile_analysis_double(f_ref,f_rst_m,f_rst_n,nms_data):
	p_analysis = './txt_analysis/'
	
	dic_cm_ref = do_csv_metrics(f_ref,p_analysis,nms_data)
	dic_cm_mndwi = do_csv_metrics(f_rst_m,p_analysis,nms_data)
	dic_cm_ndwi = do_csv_metrics(f_rst_n,p_analysis,nms_data)
	
	#n = len(dic_cm_rst[dic_cm_rst.keys()[0]])
	n = 4
	for i in range(n):
		compare_metric_double(nms_data,dic_cm_ref,dic_cm_mndwi,dic_cm_ndwi,i,p_analysis)
		
		
def compare_metric_double(nms_data,dic_cm_ref,dic_cm_mndwi,dic_cm_ndwi,i,p_analysis):
	metric = G_dic_metrics[i]
	
	nm_ref,nm_mndwi,nm_ndwi = nms_data
	f_csv = p_analysis + nm_ref + '_' + metric + '.csv'
	writer = csv.writer(file(f_csv, 'wb'))
	writer.writerow(['Code_uniq','ref_'+metric,'mndwi_'+metric,'ndwi_'+metric,'e_mndwi_'+metric,'e_ndwi_'+metric])
	
	ks = list(set(dic_cm_mndwi.keys() + dic_cm_ndwi.keys()))
	ks.sort()
	dic_diff = {}
	for k in ks:
		r_ref = dic_cm_ref[k][i]
		r_mndwi = dic_cm_mndwi[k][i] if k in dic_cm_mndwi else 0.0
		r_ndwi = dic_cm_ndwi[k][i] if k in dic_cm_ndwi else 0.0
		#r_diff = math.fabs(r_rst - r_ref) / r_ref
		r_d_mndwi = (r_mndwi - r_ref) / r_ref
		r_d_ndwi = (r_ndwi - r_ref) / r_ref
		
		s_ref = '%10f'%r_ref
		s_mndwi = '%10f'%r_mndwi
		s_ndwi = '%10f'%r_ndwi
		s_d_mndwi = '%10f'%r_d_mndwi
		s_d_ndwi = '%10f'%r_d_ndwi
		#dic_diff[k] = [s_ref,s_rst,s_diff]
		dic_diff[k] = [r_ref,r_mndwi,r_ndwi,r_d_mndwi,r_d_ndwi]
		writer.writerow([k,s_ref,s_mndwi,s_ndwi,s_d_mndwi,s_d_ndwi])

#----------------------------------------------------------------------- 5 factors for chart
def analysis_on_factors(dic_diff):
	pass













