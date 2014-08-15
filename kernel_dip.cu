#define BLOCK_WIDTH 32
#define BLOCK_HEIGHT 32
#define TILE_WIDTH 30
#define TILE_HEIGHT 30
#define NODATA -9999
#define FILTER_RADIUS 1

// -------------------------------------------------Neighbours access order is 			// 1 2 3
__constant__ int off_x[8] = {-1, 0, 1,1,1,0,-1,-1};		// 8    4
__constant__ int off_y[8] = {-1,-1,-1,0,1,1, 1, 0};		// 7 6 5

__global__ void kernel_ndvi( short *m_l,short *m_r,short *m_wi, const int w, const int h)
{
	int x = blockIdx.x * TILE_WIDTH  + threadIdx.x - FILTER_RADIUS;
	int y = blockIdx.y * TILE_HEIGHT + threadIdx.y - FILTER_RADIUS;
	//Clamp to the center
	x = max(FILTER_RADIUS, x);
	x = min(x, w - FILTER_RADIUS - 1);
	y = max(FILTER_RADIUS, y);
	y = min(y, h - FILTER_RADIUS - 1);

	unsigned int i_img = y * w + x;
	
	short v_l, v_r;
	float vf_ndvi;
	
	v_l = m_l[i_img];
	v_r = m_r[i_img];

	if (v_l != NODATA && v_r != NODATA)
	{
		vf_ndvi = __int2float_rn ( v_l - v_r ) / __int2float_rn ( v_l + v_r );
		m_wi[i_img] = __float2int_rz	(vf_ndvi * 1000.0) + 1000;
	}else{
		m_wi[i_img] = NODATA;
	}

}


__global__ void kernel_sobel( short *m_wi, float *m_sobel, const int w, const int h)
{
	__shared__ short sh_wi[BLOCK_WIDTH * BLOCK_HEIGHT];
	
	int x = blockIdx.x * TILE_WIDTH  + threadIdx.x - FILTER_RADIUS;
	int y = blockIdx.y * TILE_HEIGHT + threadIdx.y - FILTER_RADIUS;
	//Clamp to the center
	x = max(FILTER_RADIUS, x);
	x = min(x, w - FILTER_RADIUS - 1);
	y = max(FILTER_RADIUS, y);
	y = min(y, h - FILTER_RADIUS - 1);

	unsigned int i_img = y * w + x;
	unsigned int i_sh = threadIdx.y * blockDim.y + threadIdx.x;

	sh_wi[i_sh] =  m_wi[i_img];
	__syncthreads();
	
	//m_sobel[i_img] = __int2float_rn (sh_wi[i_sh]);
	if ( threadIdx.x == 0 || threadIdx.x == BLOCK_WIDTH -1 || threadIdx.y == 0 || threadIdx.y == BLOCK_HEIGHT - 1) 
	{}else{
	float sobel_x = __int2float_rn (
	   -sh_wi[i_sh - blockDim.x - 1] + sh_wi[i_sh - blockDim.x + 1]
	   -sh_wi[i_sh - 1] * 2          + sh_wi[i_sh + 1] * 2
	   -sh_wi[i_sh + blockDim.x - 1] + sh_wi[i_sh + blockDim.x + 1] );
	   
	float sobel_y = __int2float_rn (
		sh_wi[i_sh - blockDim.x - 1] + sh_wi[i_sh - blockDim.x] * 2 + sh_wi[i_sh - blockDim.x + 1] 
	   -sh_wi[i_sh + blockDim.x - 1] - sh_wi[i_sh + blockDim.x] * 2 - sh_wi[i_sh + blockDim.x + 1] );
	  
	m_sobel[i_img] = sqrtf ( sobel_x * sobel_x + sobel_y * sobel_y ) ;
	}
	/*   */


}





















