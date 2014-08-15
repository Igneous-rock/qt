#-*- coding: UTF-8 -*- 


####-*- coding: cp936 -*- 


# coding=gbk
def plot_scatter(dic_cm_ref,dic_cm_rst):
	fontsize_big = 22
	fontsize_small = 16
	#x = ['1','2','3','4','5']
	i_plot = [221,222,223,224]
	ks = dic_cm_rst.keys()
	
	fig = plt.figure()
	color_rl = 'b'
	color_p = 'r'

	#============================================================================= 221
	ax1 = fig.add_subplot(221)#, sharey=ax2)
	i_plot = 0
	x1 = [dic_cm_ref[k][i_plot] for k in ks]
	y1 = [dic_cm_rst[k][i_plot] for k in ks]
	ls_area = y1

	v_intcpt,v_slope,v_R2 = linear_regress.linear_regress_ols(x1,y1)

	from mpl_toolkits.axes_grid.anchored_artists import AnchoredText
	name_anno = G_dic_metrics[i_plot]
	at = AnchoredText(name_anno,prop=dict(size=fontsize_big), frameon=False,loc=4, )
	ax1.add_artist(at)
	#ax1.text(0.85, 0.05, name_anno, transform=ax1.transAxes, fontsize=fontsize_big,verticalalignment='bottom')#, bbox=props)

	_plus = r'$\it{x - }$' if v_intcpt < 0.0 else r'$\it{x + }$'
	str_formula = r'$\it{y = %.5f}$'%v_slope + _plus + r'$\it{%.5f}$'%abs(v_intcpt) + '\n' + r'$\it{R^2 = %.5f}$'%v_R2
	#props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
	ax1.text(0.05, 0.95, str_formula, transform=ax1.transAxes, fontsize=fontsize_small,verticalalignment='top')#, bbox=props)

	
	ax1.plot([min(x1), max(x1)], [v_intcpt + v_slope * min(x1), v_intcpt + v_slope * max(x1)], color=color_rl)#,linewidth=3)
	ax1.scatter(x1,y1,s=ls_area,c=ks,alpha=0.5)

	#labels = d_set[1]
	#ax1.set_xticklabels(labels, rotation=30)

	ax1.xaxis.get_label().set_size(fontsize_big)
	ax1.yaxis.get_label().set_size(fontsize_big)
	
	for label in ax1.xaxis.get_ticklabels():
		#label.set_visible(False)
		label.set_fontsize(fontsize_small)
	for label in ax1.yaxis.get_ticklabels():
		label.set_fontsize(fontsize_small)
	plt.ylabel('Result')
		
	#============================================================================= 222
	i_plot = 1
	ax2 = fig.add_subplot(222)
	x2 = [dic_cm_ref[k][i_plot] for k in ks]
	y2 = [dic_cm_rst[k][i_plot] for k in ks]


	from mpl_toolkits.axes_grid.anchored_artists import AnchoredText
	name_anno = G_dic_metrics[i_plot]
	at = AnchoredText(name_anno,prop=dict(size=fontsize_big), frameon=False,loc=4, )
	ax2.add_artist(at)
	
	v_intcpt,v_slope,v_R2 = linear_regress.linear_regress_ols(x2,y2)
	_plus = r'$\it{x - }$' if v_intcpt < 0.0 else r'$\it{x + }$'
	str_formula = r'$\it{y = %.5f}$'%v_slope + _plus + r'$\it{%.5f}$'%abs(v_intcpt) + '\n' + r'$\it{R^2 = %.5f}$'%v_R2
	#props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
	ax2.text(0.05, 0.95, str_formula, transform=ax2.transAxes, fontsize=fontsize_small,verticalalignment='top')#, bbox=props)
	
	ax2.plot([min(x2), max(x2)], [v_intcpt + v_slope * min(x2), v_intcpt + v_slope * max(x2)], color=color_rl)#,linewidth=3)
	ax2.scatter(x2,y2,s=ls_area,c=ks,alpha=0.5)

	#l = plt.axhline(y=0, color='k', alpha=0.5,linestyle=':')

	#labels = d_set[1]
	#ax2.set_xticklabels(labels, rotation=30)

	ax2.xaxis.get_label().set_size(fontsize_big)
	ax2.yaxis.get_label().set_size(fontsize_big)
	
	for label in ax2.xaxis.get_ticklabels():
		#label.set_visible(False)
		label.set_fontsize(fontsize_small)
	for label in ax2.yaxis.get_ticklabels():
		#label.set_visible(False)
		label.set_fontsize(fontsize_small)
		
	#plt.subplots_adjust(left = 0.15,right = 0.7,bottom = 0.35)
	
			
	#============================================================================= 223
	ax3 = fig.add_subplot(223)
	i_plot = 2
	x3 = [dic_cm_ref[k][i_plot] for k in ks]
	y3 = [dic_cm_rst[k][i_plot] for k in ks]

	from mpl_toolkits.axes_grid.anchored_artists import AnchoredText
	name_anno = G_dic_metrics[i_plot]
	at = AnchoredText(name_anno,prop=dict(size=fontsize_big), frameon=False,loc=4, )
	ax3.add_artist(at)

	v_intcpt,v_slope,v_R2 = linear_regress.linear_regress_ols(x3,y3)
	_plus = r'$\it{x - }$' if v_intcpt < 0.0 else r'$\it{x + }$'
	str_formula = r'$\it{y = %.5f}$'%v_slope + _plus + r'$\it{%.5f}$'%abs(v_intcpt) + '\n' + r'$\it{R^2 = %.5f}$'%v_R2
	#props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
	ax3.text(0.05, 0.95, str_formula, transform=ax3.transAxes, fontsize=fontsize_small,verticalalignment='top')#, bbox=props)
	
	ax3.plot([min(x3), max(x3)], [v_intcpt + v_slope * min(x3), v_intcpt + v_slope * max(x3)], color=color_rl)#,linewidth=3)
	ax3.scatter(x3,y3,s=ls_area,c=ks,alpha=0.5)

	ax3.xaxis.get_label().set_size(fontsize_big)
	ax3.yaxis.get_label().set_size(fontsize_big)
	
	for label in ax3.xaxis.get_ticklabels():
		label.set_fontsize(fontsize_small)
	for label in ax3.yaxis.get_ticklabels():
		label.set_fontsize(fontsize_small)
		
	plt.xlabel('Reference')

	#============================================================================= 224
	ax4 = fig.add_subplot(224)#, sharey=ax3)
	i_plot = 3
	x4 = [dic_cm_ref[k][i_plot] for k in ks]
	y4 = [dic_cm_rst[k][i_plot] for k in ks]

	from mpl_toolkits.axes_grid.anchored_artists import AnchoredText
	name_anno = G_dic_metrics[i_plot]
	at = AnchoredText(name_anno,prop=dict(size=fontsize_big), frameon=False,loc=4, )
	ax4.add_artist(at)
	
	v_intcpt,v_slope,v_R2 = linear_regress.linear_regress_ols(x4,y4)
	_plus = r'$\it{x - }$' if v_intcpt < 0.0 else r'$\it{x + }$'
	str_formula = r'$\it{y = %.5f}$'%v_slope + _plus + r'$\it{%.5f}$'%abs(v_intcpt) + '\n' + r'$\it{R^2 = %.5f}$'%v_R2
	#props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
	ax4.text(0.05, 0.95, str_formula, transform=ax4.transAxes, fontsize=fontsize_small,verticalalignment='top')#, bbox=props)
	
	ax4.plot([min(x4), max(x4)], [v_intcpt + v_slope * min(x4), v_intcpt + v_slope * max(x4)], color=color_rl)#,linewidth=3)
	ax4.scatter(x3,y3,s=ls_area,c=ks,alpha=0.5)

	#labels = d_set[1]
	#ax4.set_xticklabels(labels, rotation=30)

	ax4.xaxis.get_label().set_size(fontsize_big)
	ax4.yaxis.get_label().set_size(fontsize_big)
	
	
	for label in ax4.xaxis.get_ticklabels():
		label.set_fontsize(fontsize_small)
	for label in ax4.yaxis.get_ticklabels():
		#label.set_visible(False)
		label.set_fontsize(fontsize_small)
		

	plt.subplots_adjust(bottom = 0.2)

	plt.show()

	return

def chart_scatter_plot(P_shp):
	f_ref = P_shp + '2000_Merge_ui.shp'
	f_rst = P_shp + 'lakes_combined.shp'
	p_csv = './'
	
	dic_cm_ref = lib_analysis.do_csv_metrics(f_ref,None)
	dic_cm_rst = lib_analysis.do_csv_metrics(f_rst,None)
	
	lib_analysis.compare_metric(dic_cm_ref,dic_cm_rst,2,p_csv)
	plot_scatter(dic_cm_ref,dic_cm_rst)


import os,sys
import numpy as np
import time
import matplotlib.pyplot as plt
import lib_analysis
import linear_regress
#-----------------------------------------------------
G_dic_metrics = lib_analysis.G_dic_metrics


#--------------------------------------------------------------
if __name__ == '__main__':
	a = time.clock()
	P_shp = 'D:/water/qt/lakes/'
	chart_scatter_plot(P_shp)
	print time.clock() -a

	print 'done'
