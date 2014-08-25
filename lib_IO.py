import geo_raster as GR
#---------------------------------------------- file path 
def getDirList( _p ,_pattern):
	import re,os

	_p = str( _p )
	if _p=="":
		return [ ]

	_dirs = os.listdir( _p )

	_match = []
	for _dir in _dirs:
		#if os.path.isdir(_dir):
		if re.search(_pattern,_dir):
			_match.append(_dir)
			
	_match.sort()
	return _match

def getFileList(_dir,_pattern):
	import os,re

	_files = os.listdir(_dir)
	_match = []
	for _file in _files:
		#if os.path.isfile(_dir):
		if re.search(_pattern,_file):
			_match.append(_dir + '/' + _file)
			
	_match.sort()
	return _match
	
def generateDIR(_root,_pattern_dir = '(lndsr.*)|(result)',_pattern_data = '^band[1-57].*\.tif'):
	import os 
	
	_dirs = []
	_dirlist = getDirList(_root,_pattern_dir)
	for _dir in _dirlist: 
		_path = _root + '/' + _dir
		_filelist = getFileList(_path,_pattern_data)

		for _list in _filelist:
			_dirs.append( _list)

	return _dirs

def run_exe(cmd):
	import subprocess
	_p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	_rs = _p.communicate()[0]
	if _p.returncode != 0:
		import logging
		logging.error('Failed running cmd: %s %s\n' % (cmd, _p.returncode))
		logging.error('Output message:%s\n' % _rs[0])
		logging.error('Error message:%s' % _rs[1])
		raise Exception('Failed running cmd:' + cmd)

	if _rs == None or len(_rs) == 0:
		return None
	return _rs

def csv2dic(f_csv,k_ui,sw_key_int = False):
	import csv
	dic_info = {}
	reader=csv.reader(open(f_csv, 'rb'))
	header = reader.next()
	n_head = len(header)

	lst_vname = []
	for i in range(n_head):
		if header[i] == k_ui:
			i_k = i
		else:
			lst_vname.append(header[i])

	for item in reader:
		k = item[i_k] if sw_key_int == False else int(item[i_k])
		del item[i_k]
		dic_info[k] = item

	return dic_info,lst_vname
	

#----------------------------------- img type
_str_GDALconst = '''GDT_Byte = 1
	GDT_Uint8 = 1
	GDT_CFloat32 = 10
	GDT_CFloat64 = 11
	GDT_CInt16 = 8
	GDT_CInt32 = 9
	GDT_Float32 = 6
	GDT_Float64 = 7
	GDT_Int16 = 3
	GDT_Int32 = 5
	GDT_TypeCount = 12
	GDT_UInt16 = 2
	GDT_UInt32 = 4
	GDT_Unknown = 0'''
def dic_imgType(_input_type):
	_dic = {}
	_list = _str_GDALconst.split('\n\t')
	for _str in _list:
		_item = _str.split(' ')
		_type = _item[0][4:].lower()
		_code = int(_item[2])
		_dic[_type] = _code
		
	return _dic[str(_input_type).lower()]

