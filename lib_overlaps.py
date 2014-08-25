import osimport ogr,gdal,osrimport geo_shape as GSdef get_lake_pr_ori(f_ref):	ref_ref = GS.geo_shape.open(f_ref)	lyr_ref = ref_ref.get_layer(0)		sw_have = False	dfn_lyr_ref = lyr_ref.layer.GetLayerDefn()	n_field = dfn_lyr_ref.GetFieldCount()	for i in range(n_field):		fd_ref = dfn_lyr_ref.GetFieldDefn(i)		name_fd = fd_ref.GetNameRef()		if name_fd == 'PathRow':			sw_have = True				if sw_have == False: return None	dic_ui_pr = {}		n_ft = lyr_ref.layer.GetFeatureCount()	for i in xrange(n_ft):		ft_lake = lyr_ref.layer.GetFeature(i)		pr = ft_lake.GetField('PathRow')		ui = ft_lake.GetField('Code_uniq')		dic_ui_pr[ui] = pr	return dic_ui_pr	def decide_within_or_overlaps(dic_ui_wo,dic_ui_pr_ori):	dic_ui_combmethod = {}	ks = dic_ui_wo.keys()	for k in ks:		if k in dic_ui_pr_ori:			pr_ori = dic_ui_pr_ori[k]		else:			pr_ori = None		if dic_ui_wo[k][0] <> []:			if pr_ori in dic_ui_wo[k][0]:				dic_ui_combmethod[k] = ['within',[pr_ori]]			else:				dic_ui_combmethod[k] = ['within',[dic_ui_wo[k][0][0]]]		else:			dic_ui_combmethod[k] = ['overlaps',dic_ui_wo[k][1]]	return dic_ui_combmethod	def analysis_choose_or_union(f_ref,f_pr):	dic_ui_pr_ori = get_lake_pr_ori(f_ref)	dic_ui_wo = mkdic_ui_pr(f_ref,f_pr)	dic_ui_combmethod = decide_within_or_overlaps(dic_ui_wo,dic_ui_pr_ori)	return dic_ui_combmethod	#-----------------------------------------------------------------------	def mkdic_ui_pr(f_ref,f_pr):	dic_ui_wo = {}		ref_ref = GS.geo_shape.open(f_ref)	lyr_ref = ref_ref.get_layer(0)	nft_lake = lyr_ref.layer.GetFeatureCount()		ref_pr = GS.geo_shape.open(f_pr)	lyr_pr = ref_pr.get_layer(0)		print 'checking lakes located on pathrow'	p10 = nft_lake/10	_e = nft_lake%10		for i in xrange(nft_lake):		ft_lake = lyr_ref.layer.GetFeature(i)		ui = ft_lake.GetField('Code_uniq')		#if ui <> 1966:continue		geom_lake = ft_lake.GetGeometryRef()		#minx,maxx,miny,maxy = geom_lake.GetEnvelope()				count = i+1		if count%p10 == _e: print '{:.1%}'.format(float(count)/nft_lake),'ui =',ui		lyr_pr.layer.SetSpatialFilter(geom_lake)		#lyr_pr.layer.SetSpatialFilterRect(minx,miny,maxx,maxy)		ft_pr = lyr_pr.layer.GetNextFeature() 		lst_within = []		lst_overlap = []		while ft_pr:			pr = str(ft_pr.GetField('PR'))			geom_pr = ft_pr.GetGeometryRef()			if geom_lake.Within(geom_pr):				lst_within.append(pr)			elif geom_lake.Overlaps(geom_pr):				lst_overlap.append(pr)			ft_pr = lyr_pr.layer.GetNextFeature() 		dic_ui_wo[ui] = [lst_within,lst_overlap]		lyr_pr.layer.SetSpatialFilter(None)	return dic_ui_wo																						