# Biomes revisited:

Inputs to the calculation:
* Body type (rocky planet, gas giant, star, etc)
* Body mass
* Surface barometric pressure
* Altitude
* Annual mean solar flux
* Annual mean temperature
* Annual temperature variation from the mean (1.5x std dev)
* Annual rainfall total
* Annual rainfall variation from the mean (1.5x std dev)

## Terrestrial biomes:
* Swamp/Wetlands (includes estuaries, mangroves, and swamps)
* Jungle/Rainforest/Evergreen Broadleaf Forest
* Temperate Forest/Seasonal Broadleaf Forest
* Borial Forest/Evergreen Needleleaf Forest
* Grassland/Savannah
* Desert/Shrubland (normal deserts)
* Tundra/Alpine Tundra

## Aquatic biomes:
* Tropical Reef/Warm Euphotic Marine
* Sea Forest (seagrass and kelp)/Temprate to Cold Euphotic Marine
* Rocky Shallows/Seasonal Ice/Sponge Garden
* Deep Ocean
* Shallow Ocean (sea floor still in photic zone, but too deep for reefs and seaweeds)
* Surface Water/Rivers and Lakes

## Abiotic & microbiotic biomes:
* Barren (extreme dry and cold, rocky desert)
* Sand Sea (extreme dry and hot, sandy desert)
* Ice Sheet (wet and extreme cold)
* Boiling Sea/Thermal Springs (wet and extreme hot)

## Artificial biomes:
* Farmland
* Urban

## Celestial biomes:
* Moonscape
* Magma Sea
* Cryogen Sea (liquid methane, nitrogen, etc)
* Gas Giant
* Stellar Surface (normal star)
* Stellar Surface (neutron star)
* Event Horizon

## Fantasy/Sci-fi biomes:
* Ruins
* Underdark/bioluminescent/mushroom
* Evil/infected/undead wasteland
* Elemental chaos/wild magic
* Utopia/heaven/magic garden
* Consuming goo/giant blob/living ocean

# Enum Values:

### Binary format: 0b0yyyxxxx
* yyy = biome category (0=terrestrial, 1=aquatic, 2=artificial, 4=astronomical, 7=fictional)
* xxxx = biome code within category

## Codes
UNKNOWN = 0x00

### TERRESTRIAL BIOMES
WETLAND = 0x01
JUNGLE = 0x02
SEASONAL_FOREST = 0x03
NEEDLELEAF_FOREST = 0x04
GRASSLAND = 0x05
DESERT_SHRUBLAND = 0x06
TUNDRA = 0x07

### AQUATIC BIOMES
FRESHWATER = 0x11
SEA_FOREST = 0x12
TROPICAL_REEF = 0x13
ROCKY_SHALLOWS = 0x14
DEEP_OCEAN = 0x10
SHALLOW_OCEAN = 0x15

### EXTREME/MICROBIOTIC BIOMES (terrestrial and aquatic)
BARREN = 0x08
SAND_SEA = 0x09
ICE_SHEET = 0x16
BOILING_SEA = 0x17

### ASTRONOMICAL BIOMES
MOONSCAPE = 0x40
MAGMA_SEA = 0x41
CRYOGEN_SEA = 0x42
GAS_GIANT = 0x43
STAR = 0x44
NEUTRON_STAR = 0x45
EVENT_HORIZON = 0x46

### ARTIFICIAL BIOMES
FARMLAND = 0x20
URBAN = 0x21

### SCIFI/FANTASY BIOMES
RUINS = 0x22
BIOLUMINESCENT = 0x70
DEAD = 0x71
MAGIC_GARDEN = 0x72
ELEMENTAL_CHAOS = 0x73
OOZE = 0x74

