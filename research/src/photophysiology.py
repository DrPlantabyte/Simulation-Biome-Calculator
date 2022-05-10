import numpy, pandas
from numpy import ndarray, nan, uint8, float32, logical_and, logical_or, clip, sin, cos, square, sqrt, power, log10
from pandas import DataFrame


def michalelis_menten(x: ndarray, Vmax, Km):
	return (Vmax * x) / (Km + x)

def haldane(x: ndarray, Vmax, Km, opt):
	return (Vmax * x) / (Km *square(( x /opt) - 1) + x)

def CTMI(x: ndarray, xmin, xopt, xmax):
	## WARNING: only works if xopt is closer to xmax than to xmin!
	mask = numpy.ones_like(x)
	mask[(x <= xmin) + (x >= xmax)] = 0
	return mask * (( x -xmax) * square( x -xmin)) / \
				((xopt - xmin) * ((xopt - xmin) * (x - xopt) - (xopt - xmax) * (xopt + xmin - 2 * x)))


def max_photochemistry(solar_flux_Wpm2: ndarray, pressure_kPa: ndarray):
	## based on Serôdio, J, & Lavaud, J. Photosynthesis research 108.1 (2011): 61-76
	## and Rzigui, T, et al. Plant science 205 (2013): 20-28.
	photochemistry_km_PAR = 90
	PAR2Wpm2 = 1360 / 2400
	CO2_Km_ppm = 200
	Vmax = michalelis_menten(pressure_kPa * 300 / 101, Km=CO2_Km_ppm, Vmax=1 / 0.6)
	return michalelis_menten(solar_flux_Wpm2, Km=photochemistry_km_PAR * PAR2Wpm2, Vmax=Vmax)


def water_limitation(precip_mm: ndarray):
	## from Schuur, E. Ecology 84.5 (2003): 1165-1170.
	rain_Km_mm = 500
	rain_opt_mm = 2400
	return haldane(precip_mm, Vmax=1, Km=rain_Km_mm, opt=rain_opt_mm)


def temperature_limitation(temp_C: ndarray):
	## from various sources
	Tmin = -5
	Tmax = 85
	Topt = 41
	return CTMI(temp_C, xmin=Tmin, xopt=Topt, xmax=Tmax)


def photosynthesis_score(
		mean_temp_C: ndarray, temp_variation_C: ndarray, precip_mm: ndarray,
		solar_flux_Wpm2: ndarray, pressure_kPa: ndarray
):
	return numpy.minimum(
		max_photochemistry(solar_flux_Wpm2=solar_flux_Wpm2, pressure_kPa=pressure_kPa),
		water_limitation(precip_mm=precip_mm)
	) * 0.25 * (2 * temperature_limitation(mean_temp_C) + temperature_limitation(
		mean_temp_C + temp_variation_C) + temperature_limitation(mean_temp_C - temp_variation_C))
