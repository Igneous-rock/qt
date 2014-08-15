import pycuda.compiler as nvcc
import pycuda.gpuarray as gpu
import pycuda.driver as cuda
import pycuda.autoinit
import numpy as np
import geo_raster as GR
import time

#print "Compiling CUDA kernels..."
kernel_source = open("kernel_dip.cu").read()
main_module = nvcc.SourceModule(kernel_source)
kernel_sobel = main_module.get_function("kernel_sobel")

def cuda_sobel(m_wi):
	m_sobel = np.zeros_like(m_wi, np.float32)
	
	# Transfer image asynchronously.
	cu_m_wi = gpu.to_gpu_async(m_wi)
	cu_m_sobel = gpu.to_gpu_async(m_sobel)

	# Get block/grid size for steps 1-3.
	height, width = m_wi.shape

	block_hw = 32
	block_size =	(block_hw,block_hw,1)

	filter_radius = 1
	tile_size  = block_hw  - filter_radius * 2

	grid_width  = (width  + tile_size - 1) / tile_size
	grid_height = (height + tile_size- 1) / tile_size
	grid_size = (grid_width, grid_height)
	
	width	= np.int32(width)
	height = np.int32(height)

	kernel_sobel(cu_m_wi,cu_m_sobel, width, height, block=block_size, grid=grid_size)
	
	m_sobel = cu_m_sobel.get()
	return m_sobel


if __name__ == '__main__':
	a = time.clock()
	f_wi = './mndwi_gpu.tif'
	ref_img = GR.geo_raster.open(f_wi)
	m_wi = ref_img.get_band().read()
	cuda_sobel(m_wi)
	print 'cpu+gpu time is:',time.clock() -a
