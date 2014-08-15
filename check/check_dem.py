def check_have_dem(p_out,lst_pr):
	lst_lack = []
	for pr in lst_pr:
		pathrow = 'p' + pr[:3] + 'r' + pr[3:]
		p_pr = p_out + '/' + pathrow
		if not os.path.isdir(p_pr):
			lst_lack.append(pr)
		else:
			sw_have = 0
			for scene in os.listdir(p_pr):
				#p_scene = p_pr + '/' + scene
				f_slope = p_pr + '/' + scene + '/dem_30m_slope.img'
				#print f_slope
				if os.path.isfile(f_slope):
					sw_have = 1
			if sw_have == 0: lst_lack.append(pr)
	return lst_lack

def get_pr_all(f_csv):
	reader=csv.reader(open(f_csv, 'rb'))
	head = reader.next()
	return [pr[0] for pr in reader]
	
	
def check_complete(p_out):

	f_tiles = 'qt_tile_all.csv'
	lst_pr = get_pr_all(f_tiles)

	lst_lack = check_have_dem(p_out,lst_pr)
	print lst_lack
	
	
	
	
	

import time,os
import lib_IO
import lib_Global_const
import csv

if __name__ == '__main__':
	a = time.clock()
	check_complete(lib_Global_const.G_path_out)
	print time.clock() -a
	print 'done'

