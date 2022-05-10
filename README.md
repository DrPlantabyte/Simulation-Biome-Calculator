# Dr. Plantabyte's Biomes for Earth and Simulated Exoplanets
Dr. Plantabyte's biomes calculator for use in simulations (or games), including derivation and validation of biomes from scientific data sources and calculator implementations in multiple programming languages.

# Biomes
TODO: write this section

# The Biome Calculator
TODO: write this section

# Derivation and Validation of Dr. Plantabyte's Biomes
TODO: write this section

# Implementations
Here we provide several implementations of the Dr. Plantabyte Biome calculations in several programming languages for your convenience.

## Python
The biomecalculator Python module is an implementation of Dr. Plantabyte's Biomes and Biome Calculator that is good for use in quick scripts, with geospatial science tools such as GDAL, and for machine learning applications.

### Installing the biomecalculator module
`biomecalculator` has not been added to [pypi.org](https://pypi.org/) (yet), so for now you have to install from source

#### Install from source with pip
Download the source distribution file `Biome_Calculator-x.y.z.tar.gz` (where x.y.z is the version number) and then install it with `pip`. For example:

```bash
pip3 install --user Biome_Calculator-1.0.0.tar.gz
```

### Using the biomecalculator module
If use Dr. Plantabyte's biomes in your Python code, import the `Biome` enum from the `biomecalculator` module, like this:

```python
from biomecalculator.biomes import Biome
print(Biome.GRASSLAND, Biome.GRASSLAND.value)
# prints Biome.GRASSLAND 5
```

To use the `biomecalculator` module to classify or predict biomes based on environmental data, use the `classify_*` functions in the `biomecalculator` module. For example:

```
import numpy, biomecalculator
from biomecalculator.biomes import Biome
# Predict biomes at a location on Earth
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

### Building from Source

```bash
# clone the repository
git clone https://github.com/DrPlantabyte/Simulation-Biome-Calculator.git
cd Simulation-Biome-Calculator/calculator/python/
# install build dependencies
pip3 install --user numpy cython setuptools wheel
# build source distribution package
python3 setup.py sdist
# build binary distribution package as a Python wheel
python3 setup.py bdist_wheel
```

## Java
Coming soon...

## Rust
Coming soon...

## C++
Coming eventually...

# Licensing Information
This project and all libraries contained within are provided here under the [GNU Lesser Public License (LGPL) v2.1](https://opensource.org/licenses/LGPL-2.1). In summary, this means that you may:

* Use these libraries as-is (unmodified) in your software project (even if your project is not open source), so long as you give credit to Dr. Christopher C. Hall (aka Dr. Plantabyte) and provide a link to this GitHub page
* Modify these libraries, so long as you provide a link to this GitHub page and distribute a copy of your modified version with each program you create with them
* Make money from using these licenses, so long as you give credit to Dr. Christopher C. Hall (aka Dr. Plantabyte) and provide a link to this GitHub page that is visible to your customers

And you must not:
* Claim to be the original author of these libraries
* Distribute these libraries, or any derivates thereof, without giving credit to Dr. Christopher C. Hall (aka Dr. Plantabyte) and providing a link to this GitHub page
* Hide the fact that you are using these libraries (or any derivates thereof) from your users or customers

