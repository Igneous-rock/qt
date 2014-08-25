
def get_dic_pr_scene(p_pr_in):
	dic_pr_pscene = {}
	for pathrow in os.listdir(p_pr_in):
		p_pathrow = p_pr_in + '/' + pathrow
		pr = pathrow[1:4] + pathrow[5:]
		name_scene = os.listdir(p_pathrow)[0]
		
		dic_pr_pscene[pr] = p_pathrow + '/' + name_scene
		
	return dic_pr_pscene
	
	'''
def get_pf_scene(p_pr_in,name_f = ''):
	if name_f <> '':name_f = '/' + name_f
	ps_scene = []
	ls_p = [p_pr_in + p for p in os.listdir(p_pr_in)]
	for p_pr in ls_p:
		name_scene = os.listdir(p_pr)[0]
		p_scene = p_pr + '/' + name_scene + name_f
		ps_scene.append(p_scene)
		
	return ps_scene
	'''
def add_dic_overlaps(dic_ui_dem,dic_ui_overlaps):
	uis = dic_ui_overlaps.keys()
	for ui in uis:
		dic_ui_dem[ui] = dic_ui_overlaps[ui][0]
		
	
def csv_dic(dic_ui_dem):
	p_analysis = './txt_analysis/'
	f_csv = p_analysis + 'itpcas2000_dem.csv'
	writer = csv.writer(file(f_csv, 'wb'))
	writer.writerow(['ui','dem'])
	
	ks = dic_ui_dem.keys()
	ks.sort()
	for k in ks:
		writer.writerow([k,str(dic_ui_dem[k])])


	
def batch_run(p_out,p_vector):
	f_ref = p_vector + lib_Global_const.G_base_shp[:-4] + '_ui.shp'
	f_pr = p_vector + 'qt2000_tile.shp'
	dic_ui_wopr = lib_overlaps.analysis_choose_or_union(f_ref,f_pr)

	
	#==== init dic
	dic_ui_dem = {}
	dic_ui_overlaps = {}
	#for k in dic_ui_wopr.keys():
	#	dic_ui_dem[k] = 0

	dic_pr_pscene = get_dic_pr_scene(p_out)
	prs = dic_pr_pscene.keys()
	prs.sort()
	for pr in prs:
		print pr
		f_dem  = dic_pr_pscene[pr] + '/dem_30m.img'
		f_mask = dic_pr_pscene[pr] + '/mask.img'
		lib_get_lake_dem_c.get_lake_dem(pr,f_dem,f_mask,dic_ui_wopr,dic_ui_dem,dic_ui_overlaps)
		
	add_dic_overlaps(dic_ui_dem,dic_ui_overlaps)
	csv_dic(dic_ui_dem)


import lib_IO
import os,sys
import csv
import time
import geo_raster as GR
import lib_Global_const
import lib_overlaps
import lib_get_lake_dem_c
#--------------------------------------------------------------
if __name__ == '__main__':
	a = time.clock()
	batch_run(lib_Global_const.G_path_out,lib_Global_const.G_path_vector)
	print time.clock() -a
	print 'done'
