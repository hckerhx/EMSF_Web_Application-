'''
	Title: Main engine
	Author: Leo Feng
	Description: This is in charge of the main flow of the investment machine,
				 from reading data to calling each investment strategy to presenting result.
'''
import sys
sys.path.insert(0, 'C:/Users/hang/source/repos/EMSF_Web_Application-/EMSF_Web_Application/src/test')

import json
import argparse
import datetime
import numpy
import copy
import matplotlib.pyplot as plt
import os

import factor_model
import MVO
import cvar
import matrix_helper


INITIAL_PORFOLIO_VALUE = 1000 # This value in general doesn't matter, just for practical purposes
ORIGINAL_CONSTANT = 0.5 # The extent to which to keep the original portfolio
AMPLIFY_FACTOR = 1.5
LOOK_BACK_L = 48
MAX_LOOK_BACK_L = 2 * LOOK_BACK_L
NUM_DATES_SHOWN = 6


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--asset_data", default = "asset_data.json")
	parser.add_argument("--function", default = "Back-testing", help = "One of Back-testing" \
										+ ", Portfolio-domi, and Portfolio-Construction")
	parser.add_argument("--user_input", default = "user_input.json", help = "The json file defines the user"\
										+ " input")
	parser.add_argument("--id_ticker_mapping", default = "id_ticker_mapping.json")
	parser.add_argument("--ticker_id_mapping", default = "ticker_id_mapping.json")
	parser.add_argument("--factor_data", default = "factor_data.json")
	args = parser.parse_args()
	with open(args.asset_data, "r") as asset_data_in:
		asset_data = json.load(asset_data_in)
	with open(args.user_input, "r") as user_input_in:
		user_input = json.load(user_input_in)
	with open(args.id_ticker_mapping, "r") as id_ticker_mapping_in:
		id_ticker_mapping = json.load(id_ticker_mapping_in)
	with open(args.ticker_id_mapping, "r") as ticker_id_mapping_in:
		ticker_id_mapping = json.load(ticker_id_mapping_in)
	with open(args.factor_data, "r") as factor_data_in:
		factor_data = json.load(factor_data_in)
	#results1 = main_flow(asset_data, "Back-testing", user_input, id_ticker_mapping, ticker_id_mapping, factor_data)
	#results2 = main_flow(asset_data, "Portfolio-domi", user_input, id_ticker_mapping, ticker_id_mapping, factor_data)
	#with open("test_domi_result.json", "w") as results2_out:
	#	json.dump(results2, results2_out, sort_keys = True, indent = 4)
	# import pdb; pdb.set_trace()
	#results3 = main_flow(asset_data, "Portfolio-Construction", user_input, id_ticker_mapping, ticker_id_mapping, factor_data)
	# with open("compound_test_user_input.json", "w") as compound_test_user_input_out:
		# json.dump(results3["port"], compound_test_user_input_out, sort_keys = True, indent = 4)
	# results4 = main_flow(asset_data, "Back-testing", results3["port"], id_ticker_mapping, ticker_id_mapping, factor_data)
	# import pdb; pdb.set_trace()


def main_flow(asset_data, function, user_input, id_ticker_mapping, ticker_id_mapping, factor_data):
	'''
		asset_data: the variable holding all the information about the assets
		function: one of Back-testing, Portfolio-domi, and Portfolio-Construction
		user_input: one example is listed as follows
			user_input = {
				weight: {
					asset_name: weight_percent
				}
				target_return: percent
				start_date: yyyy-mm-dd
				end_date: yyyy-mm-dd
			}
	'''
    if not validate_user_input(user_input, ticker_id_mapping):
        return False

	if function == "Back-testing":
		if not ("start_date" in user_input and "end_date" in user_input and "weight" in user_input):
			print("not sufficient information provided in the user input")
			return False
		return back_testing_procedure(asset_data, user_input, id_ticker_mapping, ticker_id_mapping)
	if function == "Portfolio-domi":
		if not ("start_date" in user_input and "end_date" in user_input and "weight" in user_input):
			print("not sufficient information provided in the user input")
			return False
		return port_domi_procedure(asset_data, user_input, id_ticker_mapping, ticker_id_mapping, factor_data)
	if function == "Portfolio-Construction":
		return port_cont_procedure(asset_data, user_input, id_ticker_mapping, ticker_id_mapping, factor_data)


def validate_user_input(user_input, ticker_id_mapping):
	if "weight" in user_input:
		su = 0
		for ticker in user_input["weight"]:
			if ticker not in ticker_id_mapping and ticker != "SP500" and ticker != "DJIA":
				return False
			su += user_input["weight"][ticker]
		if abs(su - 1) > 0.01:
			return False
	return True

def back_testing_procedure(asset_data, user_input, id_ticker_mapping, ticker_id_mapping):
	'''
		Input: 
			asset_data: the variable holding all the information about the assets
			user_input: the user input must contain start_date, end_date, and weight
		return:
			a tuple of three list:
				portfolio_values
				SP500_values
				dates
				stats
	'''
	feasible_start_date_index = find_next_available_date_index(asset_data, user_input["start_date"], "SP500", +1)
	feasible_end_date_index = find_next_available_date_index(asset_data, user_input["end_date"], "SP500", -1)
	if feasible_start_date_index == -1 or feasible_end_date_index == -1:
		import pdb; pdb.set_trace()
		print("Start or end date exceeding range")
		return False
	SP500_values = asset_data["SP500"]["price_his"][feasible_start_date_index: feasible_end_date_index + 1]
	dates = asset_data["SP500"]["dates"][feasible_start_date_index: feasible_end_date_index + 1]
	portfolio_values = [0] * len(dates)
	cur_returns = [0] * (len(dates) - 1)
	shares = {} # {asset_name: num_shares}
	cur_value = {} # daily value of the portfolio {asset_name: dollar_value}
	for i in range(len(dates)):
		date = dates[i]
		for ticker in user_input["weight"].keys():
			if ticker in ticker_id_mapping:
				asset_name = ticker_id_mapping[ticker]
			else:
				asset_name = ticker
			if asset_name not in cur_value:
				cur_value[asset_name] = INITIAL_PORFOLIO_VALUE * user_input["weight"][ticker]
			if date in asset_data[asset_name]["dates"]:
				date_index = asset_data[asset_name]["dates"].index(date)
				if asset_name not in shares:
					shares[asset_name] = user_input["weight"][ticker] * INITIAL_PORFOLIO_VALUE \
								/asset_data[asset_name]["price_his"][date_index]
				cur_value[asset_name] = shares[asset_name] * \
									asset_data[asset_name]["price_his"][date_index]
		new_port_value = 0
		for asset_name in cur_value.keys():
			new_port_value += cur_value[asset_name]
		portfolio_values[i] = new_port_value
		if i > 0:
			cur_returns[i - 1] = portfolio_values[i] / portfolio_values[i - 1] - 1
	stats = {}
	stats["total_return"] = portfolio_values[-1] / portfolio_values[0] - 1
	stats["mean_return"] = numpy.mean(cur_returns)
	stats["volitility"] = numpy.std(cur_returns) / (len(cur_returns) ** 0.5)
	stats["sharpe"] = stats["mean_return"] / stats["volitility"]
	if not os.path.exists("img"):
		os.mkdir("img")
	plot_and_save(dates, [SP500_values, portfolio_values], ["SP500_values", "portfolio_values"], "img/back_res.png")
	#return {"portfolio_values": portfolio_values, "SP500_values": SP500_values, "dates": dates, "stats": stats}
	return {"portfolio_values": portfolio_values, "SP500_values": SP500_values, "dates": dates, "stats": stats, \
				"objective": "b"}

def find_next_available_date_index(asset_data, target_date, asset_name, increment):
	'''
		Description: Find the first available date near the target_date according to increment
		Input:
			asset_data: same as above
			asset_name: the ticker of the asset, such as AAPL
			target_date: the date whose index is desired
			increment: either +1 for starting date or -1 for ending date
		Return:
			The index of the available date in the -asset_data[asset_name]["dates"]
			if not found, return -1
	'''
	limit, i = 32, 0
	while target_date not in asset_data[asset_name]["dates"]:
		if i >= limit: break
		i += 1
		target_date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d") + datetime.timedelta(days=increment)
		target_date = datetime.datetime.strftime(target_date_obj, "%Y-%m-%d")
	return asset_data[asset_name]["dates"].index(target_date) if i < limit else -1


def port_domi_procedure(asset_data, user_input, id_ticker_mapping, ticker_id_mapping, factor_data):
	original_user_input = copy.deepcopy(user_input)
	if user_input["start_date"] < "2004-01-31": user_input["start_date"] = "2004-01-31"
	if user_input["end_date"] > "2018-10-31": user_input["end_date"] = "2018-10-31"
	user_port_res_whole = back_testing_procedure(asset_data, user_input, id_ticker_mapping, ticker_id_mapping)
	feasible_start_date_index = find_next_available_date_index(asset_data, user_input["start_date"], "SP500", +1)
	feasible_end_date_index = find_next_available_date_index(asset_data, user_input["end_date"], "SP500", -1)
	dates = asset_data["SP500"]["dates"][feasible_start_date_index: feasible_end_date_index + 1]
	dates = asset_data["SP500"]["dates"][feasible_start_date_index - LOOK_BACK_L: feasible_start_date_index] + dates
	portfolio_values = [INITIAL_PORFOLIO_VALUE]
	cur_portfolio = {}
	cur_returns = []
	start_debug = False
	for i in range(LOOK_BACK_L, len(dates), 1):
		date = dates[i]
		user_input["start_date"] = dates[i - LOOK_BACK_L]  # Look back 4 years each time
		user_input["end_date"] = date
		user_port_res = back_testing_procedure(asset_data, user_input, id_ticker_mapping, ticker_id_mapping)
		factor_matrix = prepare_factor_matrix(factor_data, i - LOOK_BACK_L, i, dates)
		assets_included, asset_return_matrix = prepare_asset_return_matrix(asset_data, \
												user_input["start_date"], user_input["end_date"], dates)
		expected_returns, covariance_matrix = factor_model.generate_factor(factor_matrix, asset_return_matrix)
		weight = MVO.get_weight_from_MVO(expected_returns, covariance_matrix, \
											user_port_res["stats"]["mean_return"] * AMPLIFY_FACTOR)
		new_port_value = 0
		for asset_name in cur_portfolio.keys():
			if date in asset_data[asset_name]["dates"]:
				new_port_value += asset_data[asset_name]["price_his"][asset_data[asset_name]["dates"].index(date)] \
								* cur_shares[asset_name]
			else:
				new_port_value += portfolio_values[-1] * cur_portfolio[asset_name]
		if new_port_value != 0:
			portfolio_values.append(new_port_value)
		cur_portfolio = {} # {asset_name: weight(decimal)}
		for ticker in user_input["weight"]:
			asset_name = ticker_id_mapping[ticker]
			cur_portfolio[asset_name] = user_input["weight"][ticker] * ORIGINAL_CONSTANT
		for j2 in range(len(weight)):
			if assets_included[j2] in cur_portfolio:
				cur_portfolio[assets_included[j2]] += weight[j2] * (1 - ORIGINAL_CONSTANT)
			else:
				cur_portfolio[assets_included[j2]] = weight[j2] * (1 - ORIGINAL_CONSTANT)
		cur_shares = {} # {asset_name: #shares}
		for asset_name in cur_portfolio.keys():
			if date in asset_data[asset_name]["dates"]:
					cur_shares[asset_name] = portfolio_values[-1] * cur_portfolio[asset_name] / \
								asset_data[asset_name]["price_his"][asset_data[asset_name]["dates"].index(date)]
		if len(portfolio_values) > 1:
			cur_returns.append(portfolio_values[-1] / portfolio_values[-2] - 1)
	stats = {}
	stats["total_return"] = portfolio_values[-1] / portfolio_values[0] - 1
	stats["mean_return"] = numpy.mean(cur_returns)
	stats["volitility"] = numpy.std(cur_returns) / (len(cur_returns) ** 0.5)
	stats["sharpe"] = stats["mean_return"] / stats["volitility"]
	if not os.path.exists("img"):
		os.mkdir("img")
	plot_and_save(user_port_res_whole["dates"], [user_port_res_whole["portfolio_values"], portfolio_values]\
					, ["user's portfolio", "improved portfolio"], "img/domi_res.png")
	return {	"original_value": {"portfolio_values": user_port_res_whole["portfolio_values"], \
									"stats": user_port_res_whole["stats"]}, \
				"dominant": {"portfolio_values": portfolio_values, "stats": stats}, \
				#"dates": user_port_res_whole["dates"]}
                "dates": user_port_res_whole["dates"], "objective": "d"}


def prepare_factor_matrix(factor_data, start_date_i, end_date_i, dates):
	factor_matrix = []
	for i in range(start_date_i + 1, end_date_i + 1):
		factor_matrix.append(factor_data[dates[i][:7].replace("-", "")])
	return factor_matrix


def prepare_asset_return_matrix(asset_data, start_date, end_date, dates):
	assets_included = [] # [asset_name] that are included in the matrix, only when both start and end date are 
						# available, the asset will be included
	asset_return_matrix = []
	for asset_name in asset_data.keys():
		if start_date in asset_data[asset_name]["dates"] and end_date in asset_data[asset_name]["dates"]:
			asset_return_matrix.append(asset_data[asset_name]["ret_his"]\
									[asset_data[asset_name]["dates"].index(start_date) + 1: \
									 asset_data[asset_name]["dates"].index(end_date) + 1])
			assets_included.append(asset_name)
	return assets_included, matrix_helper.transpose(asset_return_matrix)


def port_cont_procedure(asset_data, user_input, id_ticker_mapping, ticker_id_mapping, factor_data):
	'''
		Start and end date in user_input is for user to select what range of data to look at
		If the user doesn't specify these two dates, default date will be used
		The end date for look back is "2018-09-30" for factor data availability
	'''
	if "investment_length" not in user_input or user_input["investment_length"] > MAX_LOOK_BACK_L:
		user_input["investment_length"] = LOOK_BACK_L
	if "target_return" not in user_input: user_input["target_return"] = 0.1
	user_input["end_date"] = "2018-09-30"
	feasible_end_date_index = find_next_available_date_index(asset_data, user_input["end_date"], "SP500", -1)
	dates = asset_data["SP500"]["dates"]\
			[feasible_end_date_index - user_input["investment_length"]: feasible_end_date_index + 1]
	factor_matrix = prepare_factor_matrix(factor_data, 0, len(dates) - 1, dates)
	assets_included, asset_return_matrix = prepare_asset_return_matrix(asset_data, \
												dates[0], dates[-1], dates)
	expected_returns, covariance_matrix = factor_model.generate_factor(factor_matrix, asset_return_matrix)
	mvo_weight = MVO.get_weight_from_MVO(expected_returns, covariance_matrix, \
											user_input["target_return"])
	mvo_port = {"weight": {}, "start_date": dates[0], "end_date": "2018-10-31"}
	for i in range(len(assets_included)):
		if assets_included[i] in id_ticker_mapping:
			mvo_port["weight"][id_ticker_mapping[assets_included[i]]] = mvo_weight[i]
		else:
			mvo_port["weight"][assets_included[i]] = mvo_weight[i]
	mvo_port_back_test_res = back_testing_procedure(asset_data, mvo_port, \
														id_ticker_mapping, ticker_id_mapping)
	cur_price = []
	for i in range(len(assets_included)):
		try:
			cur_price.append(asset_data[assets_included[i]]["price_his"]\
								[asset_data[assets_included[i]]["dates"].index(dates[0])])
		except:
			import pdb; pdb.set_trace()
	cvar_weight = cvar.get_optimal_weight_by_CVaR(expected_returns, covariance_matrix, cur_price, \
									10, int(user_input["investment_length"]), \
									int(user_input["investment_length"] / 4) )
	cvar_port = {"weight": {}, "start_date": dates[0], "end_date": "2018-10-31"}
	for i in range(len(assets_included)):
		if assets_included[i] in id_ticker_mapping:
			cvar_port["weight"][id_ticker_mapping[assets_included[i]]] = cvar_weight[i]
		else:
			cvar_port["weight"][assets_included[i]] = cvar_weight[i]
	cvar_port_back_test_res = back_testing_procedure(asset_data, cvar_port, \
														id_ticker_mapping, ticker_id_mapping)
	# import pdb; pdb.set_trace()
	if not os.path.exists("img"):
		os.mkdir("img")
	plot_and_save(dates + ["2018-10-31"], [cvar_port_back_test_res["portfolio_values"], \
											mvo_port_back_test_res["portfolio_values"]], \
						["CVaR", "MVO"], "img/port_c_res.png")
	if cvar_port_back_test_res["stats"]["sharpe"] > mvo_port_back_test_res["stats"]["sharpe"]:
		#return {"port": cvar_port, "back_test": cvar_port_back_test_res, "taken": "CVaR"}
		return {"port": cvar_port, "back_test": cvar_port_back_test_res, "taken": "CVaR", "objective": "c"}
	else:
		#return {"port": mvo_port, "back_test": mvo_port_back_test_res, "taken": "MVO"}
		return {"port": mvo_port, "back_test": mvo_port_back_test_res, "taken": "MVO", "objective": "c"}


def plot_and_save(dates, arr_of_data, legends, filename):
	for data in arr_of_data:
		if len(data) != len(dates):
			import pdb; pdb.set_trace()
			print("THe length of data must be in the same length as date")
			return
	x_ticks = [dates[0]]
	incre = int(len(dates) / NUM_DATES_SHOWN)
	for i in range(NUM_DATES_SHOWN - 1):
		x_ticks += [""] * (incre - 1) + [dates[(i + 1) * incre]]
	x_ticks += [""] * (len(dates) - len(x_ticks) - 1) + [dates[-1]]
	x = range(len(dates))

	fig = plt.figure()
	for i in range(len(arr_of_data)):
		plt.plot(x, arr_of_data[i], label = legends[i])
	plt.xticks(x, x_ticks, rotation='vertical')
	plt.legend(loc='upper left')
	fig.savefig(filename, dpi=fig.dpi)


if __name__ == '__main__':
	main()
	# plot_and_save([1,2,3,4,5,6,7,8,9,10,11,12,13], [[1,2,3,4,5,6,7,8,9,10,11,12,13], [1,2,3,4,5,6,7,8,9,10,11,12,13]], "")