'''def copy_rename(p_in,nm_scene,p_out):	nms_lake = ['lakes_mndwi.' + _suffix for _suffix in ['shp','prj','dbf','shx']]	for nm_lake in nms_lake:		f_in = p_in + '/' + nm_scene + '/' + nm_lake		f_out = p_out + '/' + nm_scene + nm_lake[-4:]		cmd_cp = 'cp ' + f_in + ' ' + p_out		_rs = lib_IO.run_exe(cmd_cp)				f_old = p_out + '/' + nm_lake		f_new = p_out + '/' + nm_scene + nm_lake[-4:]		os.rename(f_old,f_new)'''		def copy_rename_render(p_in_pr,nm_scene,nms_lake,p_out):	for nm_lake in nms_lake:		f_in = p_in_pr + '/' + nm_scene + '/render/' + nm_lake		cmd_cp = 'cp ' + f_in + ' ' + p_out		_rs = lib_IO.run_exe(cmd_cp)				f_old = p_out + '/' + nm_lake		f_new = p_out + '/' + nm_scene + '_' + nm_lake		os.rename(f_old,f_new)def batch_copy_rename(p_in,p_out):	ps_pr = os.listdir(p_in)		nms_lake = ['542.png','result.png']	for p_pr in ps_pr:		p_in_pr = p_in + '/' + p_pr		nms_scene = os.listdir(p_in_pr)		nms_scene.sort()				for nm_scene in nms_scene:			copy_rename_render(p_in_pr,nm_scene,nms_lake,p_out)			print 'copying ',nm_scene	def gather_results():	p_in  = '/mnt/data_3t_a/jiangh/result/lake_typical'	p_out = '/mnt/data_3t_a/jiangh/temp/png'		batch_copy_rename(p_in,p_out)import time,osimport lib_IOif __name__ == '__main__':	a = time.clock()	gather_results()	print time.clock() -a	print 'done'