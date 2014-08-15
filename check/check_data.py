def get_in_scene(p_pr_in):
	ls_scene = []
	ls_p = [p_pr_in + p for p in os.listdir(p_pr_in)]
	for p_pr in ls_p:
		#ls_scene.append(os.listdir(p_pr)[0])
		name_scene = os.listdir(p_pr)[0]
		pathrow = name_scene[4:7] + name_scene[8:11]
		ls_scene.append(pathrow)
		
	return ls_scene
	
def get_ref_scene(f_ref):
	ref_ref = GS.geo_shape.open(f_ref)
	lyr_ref = ref_ref.get_layer(0)
	
	ls_scene_ref = {}
	
	n_ft_m = lyr_ref.layer.GetFeatureCount()
	for i in xrange(n_ft_m):
		ft_mg = lyr_ref.layer.GetFeature(i)
		pathrow = ft_mg.GetField('PathRow')#'PathRow','Day','Source'
		#_pr = 'p' + pathrow[:3] + 'r' + pathrow[3:]
		
		date = ft_mg.GetField('Day')
		if date <> None: date = date[:4] + date[5:7] + date[8:]
		
		scene = pathrow# + '_' + date
		
		ls_scene_ref[pathrow] = date
		
	return ls_scene_ref

def get_incomplete(ls_scene_ref,ls_scene):
	f_csv = './data_not_instock.csv'
	writer = csv.writer(file(f_csv, 'wb'))
	writer.writerow(['scence','date'])
	
	ls_empty = {}
	ks = ls_scene_ref.keys()
	for scene in ls_scene_ref:
		if not scene in ls_scene:
			ls_empty[scene] = ls_scene_ref[scene]
			writer.writerow([scene,ls_scene_ref[scene]])
	print ls_empty
			
	
def check_complete(p_pr_in, p_vector):

	f_ref = p_vector + '2000_Merge_unicd.shp'
	ls_scene_ref = get_ref_scene(f_ref)
	
	#f_vct = p_vector + '2000_Merge_unicd.shp'
	ls_scene = get_in_scene(p_pr_in)
	
	get_incomplete(ls_scene_ref,ls_scene)
	
	



import time,sys,os
import lib_IO
import lib_Global_const
import geo_shape as GS
import csv

if __name__ == '__main__':
	a = time.clock()
	check_complete(lib_Global_const.G_path_out, lib_Global_const.G_path_vector)
	print time.clock() -a
	print 'done'

