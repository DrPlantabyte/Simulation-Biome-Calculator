from enum import Enum, unique
import numpy, sys

@unique
class Biome(Enum):
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


# see paged 7-14 of https://lpdaac.usgs.gov/documents/101/MCD12_User_Guide_V6.pdf
def Biome_from_IGBP_cover_type(cover_type: int) -> Biome:
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
