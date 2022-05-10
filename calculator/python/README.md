# Dr. Plantabyte's biome calculator for Earth and simulated exoplanets.

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

