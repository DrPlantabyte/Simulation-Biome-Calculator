"""
Dr. Plantabyte's biomes for Earth and simulated exoplanets.

These biomes are based on various sources from the fields of remote sensing, marine biology, and astrobiology research,
combined with machine learning and a few expert guestimates from plant biologist Dr. Christopher C. Hall. The result is
a realistic biome classification system that covers both Earthly biomes and plausible exoplanet environments. A few
abiotic "biomes" are included as well to facilitate use in simulations for graphic design, story-telling, and games.

"""

from enum import Enum, unique
import numpy, sys

@unique
class Biome(Enum):
	"""
The Biome enum represents Dr. Plantabyte's biomes for Earth and simulated exoplanets. The biomes include both Earthly
biomes like tropical rainforests (jungle) and grasslands, as well as biomes that may exist on other planets, such as
boiling seas.

Biomes are recorded as 7-bit codes consisting of 3 category bits and 4 biome code bits:
bits: 0yyyxxxx
yyy = biome category (0=terrestrial, 1=aquatic, 2=artificial, 4=astronomical, 7=fictional)
xxxx = biome code within category

The full list of biomes are as follows:
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

	"""
	UNKNOWN = 0x00
	# bits: 0yyyxxxx
	# yyy = biome category (0=terrestrial, 1=aquatic, 2=artificial, 4=astronomical, 7=fictional)
	# xxxx = biome code within category
	## TERRESTRIAL BIOMES
	WETLAND = 0x01
	JUNGLE = 0x02
	SEASONAL_FOREST = 0x03
	NEEDLELEAF_FOREST = 0x04
	GRASSLAND = 0x05
	DESERT_SHRUBLAND = 0x06
	TUNDRA = 0x07
	## AQUATIC BIOMES
	FRESHWATER = 0x11
	SEA_FOREST = 0x12
	TROPICAL_REEF = 0x13
	ROCKY_SHALLOWS = 0x14
	DEEP_OCEAN = 0x10
	SHALLOW_OCEAN = 0x15
	## EXTREME/MICROBIOTIC BIOMES (terrestrial and aquatic)
	BARREN = 0x08
	SAND_SEA = 0x09
	ICE_SHEET = 0x16
	BOILING_SEA = 0x17
	## ASTRONOMICAL BIOMES
	MOONSCAPE = 0x40
	MAGMA_SEA = 0x41
	CRYOGEN_SEA = 0x42
	GAS_GIANT = 0x43
	STAR = 0x44
	NEUTRON_STAR = 0x45
	EVENT_HORIZON = 0x46
	## ARTIFICIAL BIOMES
	FARMLAND = 0x20
	URBAN = 0x21
	## SCIFI/FANTASY BIOMES
	RUINS = 0x22
	BIOLUMINESCENT = 0x70
	DEAD = 0x71
	MAGIC_GARDEN = 0x72
	ELEMENTAL_CHAOS = 0x73
	OOZE = 0x74

	def __int__(self):
		return self.value


# see paged 7-14 of https://lpdaac.usgs.gov/documents/101/MCD12_User_Guide_V6.pdf
def Biome_from_IGBP_cover_type(cover_type: int) -> Biome:
	"""
	Converts an IGBP land cover type to the corresponding Plantabyte biome
	:param cover_type: IGBP land cover code
	:return: Returns the corresponding Biome
	"""
	if cover_type   == 1: return Biome.NEEDLELEAF_FOREST # Use FAO for tundra
	elif cover_type == 2: return Biome.JUNGLE
	elif cover_type == 3: return Biome.SEASONAL_FOREST
	elif cover_type == 4: return Biome.SEASONAL_FOREST
	elif cover_type == 5: return Biome.SEASONAL_FOREST
	elif cover_type == 6: return Biome.DESERT_SHRUBLAND
	elif cover_type == 7: return Biome.DESERT_SHRUBLAND
	elif cover_type == 8: return Biome.GRASSLAND # could be desert shrubland, but a lay person would probably call it grassland with trees
	elif cover_type == 9: return Biome.GRASSLAND
	elif cover_type == 10: return Biome.GRASSLAND
	elif cover_type == 11: return Biome.WETLAND
	elif cover_type == 12: return Biome.FARMLAND
	elif cover_type == 13: return Biome.URBAN
	elif cover_type == 14: return Biome.FARMLAND
	elif cover_type == 15: return Biome.ICE_SHEET
	elif cover_type == 16: return Biome.SAND_SEA # could be barren, but 90+% is sand sea
	elif cover_type == 17: return Biome.FRESHWATER # code 17 is usually ocean, but IGBP is meant for terrestrial analysis only, so if altitude is above sealevel, then it's freshwater
	else: return Biome.UNKNOWN
