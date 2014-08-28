

def auto_gen_all():
	dic_data_path = lib_Global_const.G_dic_data_path
	batch_qt2000.run_region_4_wi(dic_data_path)
	
	
	
	dic_data_path['water_index'] = 'ndwi.img'
	batch_qt2000.run_region_4_wi(dic_data_path)
	













import lib_Global_const
import batch_qt2000
#--------------------------------------------------------------
if __name__ == '__main__':
	import time
	a = time.clock()
	auto_gen_all()
	print time.clock() -a
	print 'done'
	print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  
