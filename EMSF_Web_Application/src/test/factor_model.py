'''
Title: factor_model.py
Author: Shoujun Feng
DEscription: Generate expected mean and variance and covariance of different assets in the investment universe.
			 The main function is generate_factor()
'''


# import numpy as np 
# from numpy.linalg import inv
# from numpy import matmul
import matrix_helper
import copy
from scipy.stats.mstats import gmean
import numpy as np
from numpy import matmul
from numpy.linalg import inv


def generate_factor(factor_returns, asset_returns):
	'''
		Input:
			factor_returns: a matrix of factor returns in the specified period, without the first column being 1.
							For example, a two day three-factor factor returns is 
							[[0.1, 0.2, 0.5],
							 [-0.2, 0.3, -0.02]]
							Note that the date is not present, the first element is just day 1. 
							The caller of the function is responsible for matching the date between the asset return
							and the factor return.
			
			asset_returns: 	This is asset's excess return with respect to risk-free rate. Each column is the asset's
							excess return for example, a universe with three stocks and two days may look like
							[[0.05,0.02,-0.08],
							 [0.1, -0.2, 0.25]]
							each column is a stock's excess return in these two days, again, day is relative and is 
							caller's reponsibility.

		Output:
			expected_return: n x 1 vector standing for asset expected returns, n being the number of assets
			covariance_matrix: n x n matrix representing the covariance matrix for n assets.
	'''
	factor_returns_w_1 = copy.deepcopy(factor_returns)
	matrix_helper.add_to_each_row(factor_returns_w_1, 0, 1)
	factor_returns_w_1 = np.array(factor_returns_w_1)
	factor_returns_w_1_T = factor_returns_w_1.transpose()
	try:
		reg_res = matmul(matmul(inv(matmul(factor_returns_w_1_T, factor_returns_w_1)), factor_returns_w_1_T), asset_returns)
	except:
		import pdb; pdb.set_trace()
	alphas = reg_res[0]
	betas = reg_res[1:]
	expected_factor_return = get_expected_factor_return(factor_returns)
	factor_returns_T = np.array(factor_returns).transpose()
	factor_covariance = np.cov(factor_returns_T)
	epsilon = np.subtract(asset_returns, matmul(factor_returns_w_1, reg_res))
	epsilon = epsilon.transpose()
	residual_var_matrix = np.diag(np.diag(np.cov(epsilon)))
	expected_return = np.add(alphas, matmul(betas.transpose(), expected_factor_return))
	covariance_matrix = np.add(matmul(matmul(betas.transpose(), factor_covariance), betas), residual_var_matrix)
	return expected_return, covariance_matrix
	

def get_expected_factor_return(factor_returns):
	factor_returns_added_1 = copy.deepcopy(factor_returns)
	matrix_helper.add_to_each_ele(factor_returns_added_1, 1)
	expected_factor_return = []
	factor_returns_added_1 = np.array(factor_returns_added_1).transpose()
	for i in range(len(factor_returns_added_1)):
		expected_factor_return.append(gmean(factor_returns_added_1[i]) - 1)
	return expected_factor_return
