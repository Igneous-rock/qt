


def mosaic_band(ls_p_in, p_out, _band):
	fs_img = []
	for p_in_scene in ls_p_in:
		f_img = p_in_scene + '/sr_band'+ str(_band) + '_30m.img'
		fs_img.append(f_img)
	
	f_mosic = p_out + 'qt2000_band' + str(_band) + '.img'
	str_imgs = ' '.join(fs_img)
	cmd_gdal = 'gdalwarp -of HFA -t_srs "+proj=aea +lat_1=25.0 +lat_2=47.0 +lon_0=105.0 +x_0=0 +y_0=0 +datum=WGS84" -overwrite  -srcnodata -9999 -tr 150 150 -multi ' + str_imgs + ' ' + f_mosic
	_rs = lib_IO.run_exe(cmd_gdal)
	print f_mosic
	
		
def prepare_inlist(p_in):
	ls_p_in = []
	ls_p = [p_in + p for p in os.listdir(p_in)]
	for p_pr in ls_p:
		p_scene = p_pr + '/' + os.listdir(p_pr)[0] + '/'
		ls_p_in.append(p_scene)
	
	return ls_p_in
		
def mosaic_image(p_in,p_out):
	ls_p_in = prepare_inlist(p_in)
	#print ls_p_in
	for b in [2,4,5]:
		mosaic_band(ls_p_in,p_out,b)




import lib_IO
import os,sys,time
import lib_Global_const

#--------------------------------------------------------------
if __name__ == '__main__':
	a = time.clock()
	p_out = '/mnt/sdb/data/'
	mosaic_image(lib_Global_const.G_path_out, p_out)

	print time.clock() -a
	print 'done'