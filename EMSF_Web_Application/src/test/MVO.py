'''
Title MVO
Author: Leo Feng
Description: utilize MVO investment strategy to generate portfolio weight
'''

import matrix_helper
import copy
from scipy.stats.mstats import gmean
import numpy as np
from numpy import matmul, dot, array
from numpy.linalg import inv


def get_weight_from_MVO(mu, Q, target_return):
	'''
		Inputs:
			mu: the assets expected return, n x 1 vector, a list of n elements
			Q: the assets' covariance matrix, n x n matrix
			target_return: the target the portfolio needs to exceed

		Output:
			weight: a n x 1 vector representing the weight of the portfolio assets 
	'''
	arr_Q = array(Q)
	q = array([0.0] * len(mu)).reshape((len(mu),))
	G = -array(mu).reshape((1,len(mu)))
	h = array([-target_return])
	A = array([1.0] * len(mu)).reshape((1,len(mu)))
	b = array([1.0])
	return matrix_helper.cvxopt_solve_qp(arr_Q, q, G, h, A, b)