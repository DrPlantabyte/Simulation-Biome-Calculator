# Dr. Plantabyte's Biome Calculator for Earth and Simulated Exoplanets
Dr. Plantabyte's biomes calculator for use in simulations (or games), including derivation and validation of biomes from scientific data sources and calculator implementations in multiple programming languages.

## biomecalculator::Biomes
Dr. Plantabyte's biomes include both Earthly biomes like tropical rainforests (jungle) and grasslands, as well as biomes that may exist on other planets, such as boiling seas. The point is to represent the major biomes Earth as well as what one might reasonably expect on habitable exoplanets. The Plantabyte biome set also includes astronimical "biomes", such as GAS_GIANT and NEUTRON_STAR, which may be returned when classifying extreme environments that could not possibly exist on a terrestrial planet.

### Plantabyte Biome Codes
Biome codes consist of 7 bits: 3 category upper bits and 4 biome code lower bits:
bits: 0yyyxxxx
yyy = biome category (0=terrestrial, 1=aquatic, 2=artificial, 4=astronomical, 7=fictional)
xxxx = biome code within category

| code |Name             |Description                                       |
|------|-----------------|--------------------------------------------------|
|    0 |UNKNOWN          |Unclassifiable biome                              |
|      | *Terrestrial Biomes* |                                             |
|    1 |WETLAND          |Permanent wetland                                 |
|    2 |JUNGLE           |Tropical rainforest                               |
|    3 |SEASONAL_FOREST  |Temperate deciduous forest                        |
|    4 |NEEDLELEAF_FOREST|Temperate evergreen forest                        |
|    5 |GRASSLAND        |Plains, prairies, and savannas                    |
|    6 |DESERT_SHRUBLAND |Dry shrublands and less extreme deserts           |
|    7 |TUNDRA           |Seasonal grasslands where it is too cold for trees|
|    8 |BARREN           |Exposed rocks with little to no macroscopic life  |
|    9 |SAND_SEA         |Sand dunes with little to no macroscopic life     |
|      | *Aquatic Biomes*|                                                  |
|   17 |FRESHWATER       |Lakes and rivers                                  |
|   18 |SEA_FOREST       |Seagrass meadows and seaweed forests              |
|   19 |TROPICAL_REEF    |Coral reefs                                       |
|   20 |ROCKY_SHALLOWS   |Low productivity shallow marine waters            |
|   16 |DEEP_OCEAN       |Ocean                                             |
|   21 |SHALLOW_OCEAN    |Shallow ocean regions where light reaches seabed  |
|   22 |ICE_SHEET        |Frozen ocean or land covered in permanent ice     |
|   23 |BOILING_SEA      |Water body so hot that it boils                   |
|      | *Artificial Biomes* |                                              |
|   32 |FARMLAND         |Cultivated land                                   |
|   33 |URBAN            |Cities, streets, and other artificial structures  |
|   34 |RUINS            |Abandoned urban areas being reclaimed by nature   |
|   35 |POLLUTED_WASTELAND|Land too polluted to support terrestrial life    |
|   36 |POLLUTED_WASTEWATER|Water too polluted to support aquatic life      |
|      | *Astronomical "Biomes"* |                                          |
|   64 |MOONSCAPE        |Lifeless dry dust and/or rock                     |
|   65 |MAGMA_SEA        |Ocean of molten rock                              |
|   66 |CRYOGEN_SEA      |Ocean of liquid cryogen (eg liquid nitrogen)      |
|   67 |GAS_GIANT        |"Surface" of planet with extreme thick atmosphere |
|   68 |STAR             |Surface of a star                                 |
|   69 |NEUTRON_STAR     |Surface of a neutron star                         |
|   70 |EVENT_HORIZON    |"Surface" of a black hole                         |
|      | *Fantasy Biomes*|                                                  |
|  112 |BIOLUMINESCENT   |Permanently dark biome with bioluminescent flora  |
|  113 |DEAD             |Dead (or undead) landscape                        |
|  114 |MAGIC_GARDEN     |Magical paradise                                  |
|  115 |ELEMENTAL_CHAOS  |Floating rocks, never-melt ice, dancing fire, etc.|
|  116 |OOZE             |Living landscape, such as an ocean-sized amoeba   |

## biomecalculator::classifier
The biome calculator is a classifier that predicts the Plantabyte biome for a given set of geophysical and climate parameters. Classification for Earth-like planets is based on a set of environmental parameters. For exoplanet simulations, additional planetary parameters are used.

#### Environmental parameters
* **Mean solar flux (watts per square meter)** - This is the integrated average light intensity (averaged across the whole year, day and night included), ranges from 200-800 on Earth
* **Pressure (kPa)** - Atmospheric pressure
* **Altitude (m)** - Altitude above/below sealevel
* **Annual mean temperature (C)** - Annual average temperature
* **Annual temperature variation (C)** - Range of temperature variation from the average, approximately 1.5 standard deviations of a year's worth of daily temperature data
* **Annual precipitation (in mm)** - Total total per year, with 10 mm snowfall counting as 1 mm precipitation

#### Planetary parameters
* **Planeteray mass (in kg)** - Total mass of the planet
* **Planet radius (in km)** - Average radius of the planet
* **Top-of-atmosphere solar flux (watts per square meter)** - This is the sunlight intensity before it hits the planet
* **Axis tilt (in degrees)** - How tilted the planet's rotational axis is (if not tidally locked)
* **Tidal lock (true/false)** - Tidally locked planets have no day-night cycle, so their calculations are a little different

## Example usage
TODO

## Validation of Dr. Plantabyte's Biomes
Dr. Plantabyte's biomes and classification system was validated against satellite data from NASA MODIS, GEBCO, and GPM IMERG data. Compared to the MODIS IGBP land cover biome classification data set, Dr. Plantabyte's biome classification algorithm is approximately 70% accurate. Unfortunately, there is no global accounting of marine biomes (yet), so it's impossible to verify the accuracy of Dr. Plantabyte's marine biome predictions, but several known coral reefs and kelp forest locations were used to confirm that they are successfully classified as such.

## Licensing Information
This project and all libraries contained within are provided here under the [GNU Lesser Public License (LGPL) v2.1](https://opensource.org/licenses/LGPL-2.1). In summary, this means that you may:

* Use these libraries as-is (unmodified) in your software project (even if your project is not open source), so long as you give credit to Dr. Christopher C. Hall (aka Dr. Plantabyte) and provide a link to this GitHub page
* Modify these libraries, so long as you provide a link to this GitHub page and distribute a copy of your modified version with each program you create with them
* Make money from using these licenses, so long as you give credit to Dr. Christopher C. Hall (aka Dr. Plantabyte) and provide a link to this GitHub page that is visible to your customers

And you must not:
* Claim to be the original author of these libraries
* Distribute these libraries, or any derivates thereof, without giving credit to Dr. Christopher C. Hall (aka Dr. Plantabyte) and providing a link to this GitHub page
* Hide the fact that you are using these libraries (or any derivates thereof) from your users or customers

