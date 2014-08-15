
def sub__cp_gzip(p_in_pr,p_out_pr,nms_dem):
	for nm_dem in nms_dem:
		f_in_dem = p_in_pr + '/' + nm_dem
		cmd_cp = 'cp ' + f_in_dem  + '.gz ' + p_out_pr
		f_out_dem = p_out_pr + '/' + nm_dem
		
		if not os.path.isfile(f_out_dem + '.gz'):
			_rs = lib_IO.run_exe(cmd_cp)
		
		cmd_unzip = 'gzip -d ' + f_out_dem + '.gz'
		if not os.path.isfile(f_out_dem):
			_rs = lib_IO.run_exe(cmd_unzip)
			
		cmd_gdal = 'gdal_translate -of HFA -projwin 449985.000 3458715.000 684915.000 3246585.000 -a_nodata -9999 dem_30m.img dem_fix_30m.img'
			
		print f_out_dem
			
			
def make_dir(p_in,p_out):
	nms_dem = ['dem_30m.img','dem_30m_slope.img']
	ps_out_pr = lib_IO.getFileList(p_out,'p...r...')
	for p_out_pr in ps_out_pr:
		pr = p_out_pr[-8:]
		p_in_pr = p_in + '/' + pr
		
		sub__cp_gzip(p_in_pr,p_out_pr,nms_dem)
		return
		



def restore_dem():
	p_in = '/mnt/data_3t_a/jiangh/data'
	p_out = '/mnt/data_3t_a/jiangh/result/qt2000'
	
	make_dir(p_in,p_out)
	
	


import lib_IO
import os,sys
import csv
import time
import lib_Global_const

#--------------------------------------------------------------
if __name__ == '__main__':
	a = time.clock()
	restore_dem()


	print time.clock() -a
	print 'done'
