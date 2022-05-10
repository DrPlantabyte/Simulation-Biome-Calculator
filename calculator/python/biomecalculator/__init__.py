"""
Dr. Plantabyte's biome calculator for Earth and simulated exoplanets.

This module provides several function for estimating the Dr. Plantabyte biome 
code for a given Earthly or exoplanet environment. If you have Cython 
installed, it will use Cython-optimized calculations to improve performance.

For more information on Dr. Plantabyte's biome codes, see the
biomecalculator.biomes module and the biomecalculator.biomes.Biome enum.

Example usage:
```
# Predict biomes at locations on Earth
import numpy, biomecalculator
from biomecalculator.biomes import Biome
Macapa_Brazil={'mean_solar_flux_Wpm2': 798, 'pressure_kPa': 101.3, 
  'altitude_m': 20, 'mean_temp_C': 28.2, 'temp_var_C': 3.2, 
  'annual_precip_mm': 2200}
print(biomecalculator.classify_biome(**Macapa_Brazil))
>>> Biome.JUNGLE
Fairbanks_Alaska={'mean_solar_flux_Wpm2': 356, 'pressure_kPa': 99.8, 
  'altitude_m': 136, 'mean_temp_C': -2.0, 'temp_var_C': 21.7,
  'annual_precip_mm': 296}
print(biomecalculator.classify_biome(**Fairbanks_Alaska))
>>> Biome.TUNDRA
# Predict biome at a location on Mars
Mars={'planet_mass_kg': 6.417e23, 'planet_mean_radius_km': 3.390e3, 
  'toa_solar_flux_Wpm2': 590, 'axis_tilt_deg': 25, 
  'mean_surface_pressure_kPa': 0.6}
Isidis_Mars={'altitude_m': -3500, 'mean_temp_C': -71.9, 'temp_var_C': 30, 
  'annual_precip_mm': 0.0, 'latitude': 12.9, 'longitude': 87.0}
print(biomecalculator.classify_biome_on_planet(**Mars, **Isidis_Mars, 
  exoplanet=True, tidal_lock=False))
>>> Biome.MOONSCAPE
# Predict biomes for a fantasy map
lats = numpy.linspace(-90,90,180)
lons = numpy.linspace(-180,180,360)
lat_map = numpy.outer(lats, numpy.ones_like(lons))
lon_map = numpy.outer(numpy.ones_like(lats), lons)
solar_flux_map = 800*numpy.cos(lat_map*3.14/180)
altitude_map = 1000*(numpy.random.default_rng().random(lat_map.shape)-0.5)
temperature_map = 40*numpy.cos(lat_map*3.14/180)-10
temp_variation_map = numpy.abs(20 * numpy.sin(lat_map*3.14/180))
rainfall_map = 1000*(numpy.random.default_rng().random(lat_map.shape))
biome_map = biomecalculator.classify_planet_biomes(9.81, 101.3, 
  solar_flux_map, altitude_map, temperature_map, temp_variation_map, 
  rainfall_map, exoplanet=False)
print(biome_map)
>>> [[ 7  8 21 ... 16 21  7]
>>>  [ 8 16  8 ...  8 21  8]
>>>  [21  8  8 ...  7  7 16]
>>>  ...
>>>  [ 8 21 21 ... 16  7  7]
>>>  [ 8 21  8 ...  8 16  7]
>>>  [ 7 16 16 ... 16 21 21]]
```

"""
import sys, numpy
from .biomes import Biome

from .impls import classifier_python
def classify_biome(
	mean_solar_flux_Wpm2,
	pressure_kPa,
	altitude_m,
	mean_temp_C,
	temp_var_C,
	annual_precip_mm
) -> Biome:
	"""
This function estimates the biome code for a given set of climate parameters

Parameters:
    mean_solar_flux_Wpm2 (float) - annual mean solar flux, in watts per square meter
    pressure_kPa (float) - atmospheric pressure at the surface (use sea-level pressure for underwater classification),
                           in kPa
    altitude_m (float) - altitude above (or below, if negative) sea-level, in meters
    mean_temp_C (float) - annual mean temperature, in degrees C
    temp_var_C (float) - the +/- range of the temperature throughout the year (1.5 standard deviations), in degrees C
    annual_precip_mm (float) - the annual mean precipitation, in mm rainfall (10 mm snowfall = 1 mm rainfall)

Returns:
    (Biome) returns the DrPlantabyte Biome enum for the predicted biome
    """
	return Biome(classifier_python.classify_biome(
		mean_solar_flux_Wpm2,
		pressure_kPa,
		altitude_m,
		mean_temp_C,
		temp_var_C,
		annual_precip_mm
	))

def classify_biome_on_planet(
	planet_mass_kg: float,
	planet_mean_radius_km: float,
	toa_solar_flux_Wpm2: float,
	axis_tilt_deg: float,
	tidal_lock: bool,
	mean_surface_pressure_kPa: float,
	altitude_m: float,
	mean_temp_C: float,
	temp_var_C: float,
	annual_precip_mm: float,
	latitude: float,
	longitude: float,
	exoplanet: bool,
) -> Biome:
	"""
This function estimates the biome code for a given set of planetary and climate parameters, with input parameters that
are more convenient for exoplanet simulations

Parameters:
    planet_mass_kg (float) - mass of the planet, in kg
    planet_mean_radius_km (float) - radius of the planet, in km
    toa_solar_flux_Wpm2 (float) - top-of-atmosphere solar flux from the planet's star, in watts per square meter
    axis_tilt_deg (float) - tilt of the planetary rotation axis, in degrees (ignored for tidally locked planets)
    tidal_lock (bool) - true for a tidally-locked plant (same side always faces the host star), false for a planet with
                        a day-night cycle (even if one day is significantly different from Earth)
    mean_surface_pressure_kPa (float) - atmospheric pressure at sea-level, in kPa
    altitude_m (float) - altitude above (or below, if negative) sea-level, in meters
    mean_temp_C (float) - annual mean temperature, in degrees C
    temp_var_C (float) - the +/- range of the temperature throughout the year (1.5 standard deviations), in degrees C
    annual_precip_mm (float) - the annual mean precipitation, in mm rainfall (10 mm snowfall = 1 mm rainfall)
    latitude (float) - the latitude coordinate of the location for biome estimation, in degrees north (negative for
                       south)
    longitude (float) - the longitude coordinate of the location for biome estimation, in degrees east (negative for
                        west)
    exoplanet (bool) - set to true to include more exotic biomes not found on Earth, set to false to only use Earthly
                       biomes

Returns:
    (Biome) returns the DrPlantabyte Biome code for the predicted biome, or 0 if no biome prediction could be made
    """
	return Biome(classifier_python.classify_biome_on_planet(
		planet_mass_kg,
		planet_mean_radius_km,
		toa_solar_flux_Wpm2,
		axis_tilt_deg,
		tidal_lock,
		mean_surface_pressure_kPa,
		altitude_m,
		mean_temp_C,
		temp_var_C,
		annual_precip_mm,
		latitude,
		longitude,
		exoplanet
	))

def classify_biome_on_planet_surface(
    gravity_m_per_s2: float,
    mean_surface_pressure_kPa: float,
    mean_solar_flux_Wpm2: float,
    altitude_m: float,
    mean_temp_C: float,
    temp_var_C: float,
    annual_precip_mm: float,
    exoplanet: bool
) -> Biome:
	"""
This function estimates the biome code for a given set of climate parameters, with the option to include extreme
exoplanet biomes that do not exist on Earth

Parameters:
    gravity_m_per_s2 (float) - gravity at the surface of the planet, in meters per second per second
    mean_surface_pressure_kPa (float) - atmospheric pressure at sea-level, in kPa
    mean_solar_flux_Wpm2 (float) - annual mean solar flux, in watts per square meter
    altitude_m (float) - altitude above (or below, if negative) sea-level, in meters
    mean_temp_C (float) - annual mean temperature, in degrees C
    temp_var_C (float) - the +/- range of the temperature throughout the year (1.5 standard deviations), in degrees C
    annual_precip_mm (float) - the annual mean precipitation, in mm rainfall (10 mm snowfall = 1 mm rainfall)
    exoplanet (bool) - set to true to include more exotic biomes not found on Earth, set to false to only use Earthly
                       biomes

Returns:
    (Biome) returns the DrPlantabyte Biome code for the predicted biome, or 0 if no biome prediction could be made
    """
	return Biome(classifier_python.classify_biome_on_planet_surface(
		gravity_m_per_s2,
		mean_surface_pressure_kPa,
		mean_solar_flux_Wpm2,
		altitude_m,
		mean_temp_C,
		temp_var_C,
		annual_precip_mm,
		exoplanet
	))

def classify_planet_biomes(
	gravity_m_per_s2: float,
	mean_surface_pressure_kPa: float,
	mean_solar_flux_Wpm2: numpy.ndarray,
	altitude_m: numpy.ndarray,
	mean_temp_C: numpy.ndarray,
	temp_var_C: numpy.ndarray,
	annual_precip_mm: numpy.ndarray,
	exoplanet: bool
) -> numpy.ndarray:
	"""
This function estimates the biome codes for an array of planet and climate parameters, with the option to include
extreme exoplanet biomes that do not exist on Earth

Parameters:
    gravity_m_per_s2 (float) - gravity at the surface of the planet, in meters per second per second
    mean_surface_pressure_kPa (float) - atmospheric pressure at sea-level, in kPa
    mean_solar_flux_Wpm2 (numpy.ndarray) - annual mean solar flux, in watts per square meter
    altitude_m (numpy.ndarray) - altitude above (or below, if negative) sea-level, in meters
    mean_temp_C (numpy.ndarray) - annual mean temperature, in degrees C
    temp_var_C (numpy.ndarray) - the +/- range of the temperature throughout the year (1.5 standard deviations), in
                                 degrees C
    annual_precip_mm (numpy.ndarray) - the annual mean precipitation, in mm rainfall (10 mm snowfall = 1 mm rainfall)
    exoplanet (bool) - set to true to include more exotic biomes not found on Earth, set to false to only use Earthly
                       biomes

Returns:
    (numpy.ndarray with dtype=uint8) returns the DrPlantabyte Biome codes for the predicted biomes
    """
	return classifier_python.classify_planet_biomes(
		gravity_m_per_s2,
		mean_surface_pressure_kPa,
		mean_solar_flux_Wpm2,
		altitude_m,
		mean_temp_C,
		temp_var_C,
		annual_precip_mm,
		exoplanet
	)

try:
	import pyximport
	pyximport.install()
	from .impls import classifier_cython
	## replace pure-python fuctions with Cython versions
	def _classify_biome(
			mean_solar_flux_Wpm2,
			pressure_kPa,
			altitude_m,
			mean_temp_C,
			temp_var_C,
			annual_precip_mm
	) -> Biome:
		return Biome(classifier_cython.classify_biome(
			mean_solar_flux_Wpm2,
			pressure_kPa,
			altitude_m,
			mean_temp_C,
			temp_var_C,
			annual_precip_mm
		))

	classify_biome = _classify_biome

	def _classify_biome_on_planet(
		planet_mass_kg: float,
		planet_mean_radius_km: float,
		toa_solar_flux_Wpm2: float,
		axis_tilt_deg: float,
		tidal_lock: bool,
		mean_surface_pressure_kPa: float,
		altitude_m: float,
		mean_temp_C: float,
		temp_var_C: float,
		annual_precip_mm: float,
		latitude: float,
		longitude: float,
		exoplanet: bool,
	) -> Biome:
		return Biome(classifier_cython.classify_biome_on_planet(
			planet_mass_kg,
			planet_mean_radius_km,
			toa_solar_flux_Wpm2,
			axis_tilt_deg,
			tidal_lock,
			mean_surface_pressure_kPa,
			altitude_m,
			mean_temp_C,
			temp_var_C,
			annual_precip_mm,
			latitude,
			longitude,
			exoplanet
		))

	classify_biome_on_planet = _classify_biome_on_planet

	def _classify_biome_on_planet_surface(
			gravity_m_per_s2: float,
			mean_surface_pressure_kPa: float,
			mean_solar_flux_Wpm2: float,
			altitude_m: float,
			mean_temp_C: float,
			temp_var_C: float,
			annual_precip_mm: float,
			exoplanet: bool
	) -> Biome:
		return Biome(classifier_cython.classify_biome_on_planet_surface(
			gravity_m_per_s2,
			mean_surface_pressure_kPa,
			mean_solar_flux_Wpm2,
			altitude_m,
			mean_temp_C,
			temp_var_C,
			annual_precip_mm,
			exoplanet
		))

	classify_biome_on_planet_surface = _classify_biome_on_planet_surface

	def _classify_planet_biomes(
		gravity_m_per_s2: float,
		mean_surface_pressure_kPa: float,
		mean_solar_flux_Wpm2: numpy.ndarray,
		altitude_m: numpy.ndarray,
		mean_temp_C: numpy.ndarray,
		temp_var_C: numpy.ndarray,
		annual_precip_mm: numpy.ndarray,
		exoplanet: bool
	) -> numpy.ndarray:
		assert tuple(mean_solar_flux_Wpm2.shape) == tuple(altitude_m.shape)
		assert tuple(mean_temp_C.shape) == tuple(altitude_m.shape)
		assert tuple(temp_var_C.shape) == tuple(altitude_m.shape)
		assert tuple(annual_precip_mm.shape) == tuple(altitude_m.shape)
		_mean_solar_flux_Wpm2 = mean_solar_flux_Wpm2.astype(numpy.float32).reshape((-1,))
		_altitude_m = altitude_m.astype(numpy.float32).reshape((-1,))
		_mean_temp_C = mean_temp_C.astype(numpy.float32).reshape((-1,))
		_temp_var_C = temp_var_C.astype(numpy.float32).reshape((-1,))
		_annual_precip_mm = annual_precip_mm.astype(numpy.float32).reshape((-1,))
		biomes = classifier_python.classify_planet_biomes(
			gravity_m_per_s2,
			mean_surface_pressure_kPa,
			_mean_solar_flux_Wpm2,
			_altitude_m,
			_mean_temp_C,
			_temp_var_C,
			_annual_precip_mm,
			exoplanet
		)
		return biomes.reshape(mean_temp_C.shape)

	classify_planet_biomes = _classify_planet_biomes
	print('INFO: using Cython bindings for improved performance', file=sys.stderr)
	#
except Exception as ex:
	print(ex, file=sys.stderr)
	print('WARNING: Failed to import Cython optimized bindings, using pure Python implementation instead. Performance may by suffer.', file=sys.stderr)
