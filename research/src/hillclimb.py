import numpy

def minimize(
	f, p0, precision=1e-5, iteration_limit=100000
):
	"""
		Use hill-climbing to minimize a function, f, by adjusting the
		parameter values towards the local optimum

		Assumes ``Y = f(*params)``.

		Parameters
		----------
		f : callable
			The cost function, f(...). It must take the parameters to
			fit as arguments.
		p0 : array_like
			Initial guess for the parameters (length N)
		precision : float (optional, default = 0.00001)
			Keep tuning the parameters until the parameters are within this
			epsilon of the local optimum (eg precision=0.01 means stop when
			within 0.01 of local minimum)
		iteration_limit : int (optional, default = 100000)
			Give up after this many iterations

		Returns
		-------
		popt : array
			Optimal values for the parameters so that the result of
			``f(*popt)`` is minimized.
		num_iters :int
			Number of iterations used to reach the optimum parameter values
	"""
	p0 = numpy.asarray(p0, dtype=numpy.float64)
	num_params = len(p0)
	params = p0.copy()
	jump_size = numpy.zeros_like(p0) + 256*precision
	iterations = 0
	base_val = f(*params)
	while (iterations := iterations+1) < iteration_limit and numpy.max(jump_size) > precision:
		for i in range(0, num_params):
			left_jump = params.copy()
			left_jump[i] = left_jump[i] - jump_size[i]
			left_long_jump = params.copy()
			left_long_jump[i] = left_long_jump[i] - 2*jump_size[i]
			right_jump = params.copy()
			right_jump[i] = right_jump[i] + jump_size[i]
			right_long_jump = params.copy()
			right_long_jump[i] = right_long_jump[i] + 2*jump_size[i]
			p_array = numpy.asarray([params, left_jump, right_jump, left_long_jump, right_long_jump])
			val_array = numpy.asarray([
					base_val, f(*left_jump), f(*right_jump),
					f(*left_long_jump), f(*right_long_jump)
			])
			best_index = numpy.argmin(val_array)
			base_val = val_array[best_index]
			params = p_array[best_index]
			if best_index == 0:
				# existing param already best, shrink step size
				jump_size[i] = jump_size[i] * 0.25
			elif best_index > 2:
				# long jump gave best result, expand step size
				jump_size[i] = jump_size[i] * 4
	return params, iterations

def maximize(
	f, p0, precision=1e-5, iteration_limit=100000
):
	"""
		Use hill-climbing to maximize a function, f, by adjusting the
		parameter values towards the local optimum

		Assumes ``Y = f(*params)``.

		Parameters
		----------
		f : callable
			The value function, f(...). It must take the parameters to
			fit as arguments.
		p0 : array_like
			Initial guess for the parameters (length N)
		precision : float (optional, default = 0.00001)
			Keep tuning the parameters until the parameters are within this
			epsilon of the local optimum (eg precision=0.01 means stop when
			within 0.01 of local maximum)
		iteration_limit : int (optional, default = 100000)
			Give up after this many iterations

		Returns
		-------
		popt : array
			Optimal values for the parameters so that the result of
			``f(*popt)`` is maximized.
		num_iters :int
			Number of iterations used to reach the optimum parameter values
	"""
	def wrapper(*params):
		return -1*f(*params)
	return minimize(f=wrapper, p0=p0, precision=precision, iteration_limit=iteration_limit)

def curve_fit(
	f, xdata, ydata, p0, precision=1e-5, iteration_limit=100000
):
	"""
	Use hill-climbing least squares to fit a function, f, to data.

	Assumes ``ydata = f(xdata, *params)``.

	Parameters
	----------
	f : callable
		The model function, f(x, ...). It must take the independent
		variable as the first argument and the parameters to fit as
		separate remaining arguments.
	xdata : array_like or object
		The independent variable where the data is measured.
		Should usually be the same length as ydata
	ydata : array_like
		The dependent data,  should be the same length as xdata
		- nominally ``f(xdata, ...)``.
	p0 : array_like
		Initial guess for the parameters (length N)
	precision : float (optional, default = 0.00001)
		Keep tuning the parameters until the parameters are within this
		epsilon of the local optimum (eg precision=0.01 means stop when
		within 0.01 of local optimum)
	iteration_limit : int (optional, default = 100000)
		Give up after this many iterations

	Returns
	-------
	popt : array
		Optimal values for the parameters so that the sum of the squared
		residuals of ``f(xdata, *popt) - ydata`` is minimized.
	num_iters :int
		Number of iterations used to reach the optimum parameter values

	Examples
	--------
	>>> import matplotlib.pyplot as plt
	>>> import numpy as np
	>>> from hillclimb import curve_fit

	>>> def fitting_function(x, a, b, c, d):
	...     return np.polyval([a, b, c, d], x)

	Define the data to be fit with some noise:

	>>> actual_params = numpy.asarray([-0.05,0.2,1.5,-5.7])
	>>> xdata = numpy.linspace(-10,10,17)
	>>> ydata = fitting_function(xdata, *actual_params) + np.random.normal(size=xdata.size)
	>>> plt.plot(xdata, ydata, 'rx', label='data')

	Fit for the parameters a, b, c of the function `func`:

	>>> popt, iters = curve_fit(func, xdata, ydata, p0=np.zeros((4,)))
	>>> print('took %s iterations' % iters)
	took 67 iterations
	>>> popt
	array([-0.04941375, 0.2123116, 1.44516, -5.80574937])
	>>> plt.plot(xdata, func(xdata, *popt), 'b--',
	...          label='fit: a=%5.3f, b=%5.3f, c=%5.3f, d=%5.3f' % tuple(popt))
	>>> plt.xlabel('x')
	>>> plt.ylabel('y')
	>>> plt.legend()
	>>> plt.show()

	"""
	def rmse(*params):
		ypred = f(xdata, *params)
		return numpy.sqrt(numpy.nanmean(numpy.square(ypred-ydata)))
	return minimize(f=rmse, p0=p0, precision=precision, iteration_limit=iteration_limit)