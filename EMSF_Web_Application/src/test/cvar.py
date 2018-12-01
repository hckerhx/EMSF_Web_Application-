'''
	Title: CVaR
	Author: Leo Feng
	Description: This investment strategy use CVaR as the metric for portfolio and 
				 and seeks the optimal portfolio by minimizing the CVaR	
'''
import matrix_helper
from numpy import matmul, exp
import numpy as np
from scipy.optimize import linprog


def get_optimal_weight_by_CVaR(mu, Q, current_prices, num_paths = 2, T = 20, N = 1, c_l = 0.95):
	'''
		Inputs:
			mu: the assets expected return, n x 1 vector, a list of n elements.
			Q: the assets' covariance matrix, n x n matrix.
			current_prices: the current prices of n assets.
			num_paths: the number of simulated asset price paths
			T: the time length of simulation in the unit of estimation of mu and Q. If mu is expected weekly
				return, then T = 26  represent half a year (26 weeks). If mu is yearly, T = 26 is 26 years.
			N: is the number of time steps to take in the simulation.
			c_l: confident level for the VaR 

		Output:
			weight: a n x 1 vector representing the weight of the portfolio assets.
	'''
	num_assets = len(mu)
	rho = matrix_helper.get_correlation_from_covariance_matrix(Q)
	L = np.linalg.cholesky(rho)
	dt = T / N
	stock_price = np.ones((num_assets, num_paths))
	for i in range(num_assets):
		for j in range(num_paths):
			stock_price[i][j] = current_prices[i]
	for j in range(num_paths):
		for i in range(N):
			ran = np.random.normal(0, 1, num_assets)
			x = matmul(L, ran)			
			for k in range(num_assets):
				stock_price[k][j] = stock_price[k][j] * exp( (mu[k] - 0.5 * Q[k][k]) * dt \
										+ ((Q[k][k] * dt)**0.5) * x[k])
	returns_sample = np.ones((num_assets, num_paths))
	for i in range(num_assets):
		for j in range(num_paths):
			returns_sample[i][j] = stock_price[i][j] / current_prices[i] - 1
	f = [1 / ((1 - c_l) * num_paths)] * num_paths + [0] * num_assets + [1]
	A = np.zeros((2 * num_paths, num_paths + num_assets + 1))
	for i in range(num_paths):
		A[i][i] = -1
		A[num_paths + i][i] = -1
		A[num_paths + i][-1] = -1
		for j in range(num_assets):
			A[num_paths + i][j + num_paths] = -returns_sample[j][i]
	Aeq = np.zeros((1, num_paths + num_assets + 1))
	for i in range(num_assets):
		Aeq[0][i + num_paths] = 1
	beq = np.ones((1,1))
	b = np.zeros((2 * num_paths, 1))
	bds = [None] * (num_paths + num_assets + 1)
	for i in range(num_paths):
		bds[i] = (None, None)
	for i in range(num_paths, num_paths + num_assets, 1):
		bds[i] = (0, None)
	bds[-1] = (None, None)
	weight = linprog(f, A_ub = A, b_ub = b, A_eq = Aeq, b_eq = beq, bounds = bds)
	return weight.x[num_paths: num_paths + num_assets]
