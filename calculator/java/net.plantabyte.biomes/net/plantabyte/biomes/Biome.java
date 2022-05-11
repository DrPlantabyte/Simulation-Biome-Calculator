package net.plantabyte.biomes;

public enum Biome {
	UNKNOWN(0, "unknown", "unknown"),
	// terrestrial biomes
	WETLAND(1, "swamp", "wetland"),
	JUNGLE(2, "jungle", "tropical rainforest"),
	SEASONAL_FOREST(3, "deciduous forest", "temperate forest"),
	NEEDLELEAF_FOREST(4, "evergreen forest", "needleleaf forest"),
	GRASSLAND(5, "grassland", "grassland"),
	DESERT_SHRUBLAND(6, "desert", "xeric shrubland"),
	TUNDRA(7, "tundra", "tundra"),
	// aquatic biomes
	FRESHWATER(17, "freshwater", "freshwater"),
	SEA_FOREST(18, "seaweed forest", "marine forest"),
	TROPICAL_REEF(19, "coral reef", "tropical reef"),
	ROCKY_SHALLOWS(20, "rocky shallows", "rocky shallows"),
	DEEP_OCEAN(16, "ocean", "deep ocean"),
	SHALLOW_OCEAN(21, "shallow ocean", "shallow ocean"),
	BARREN(8, "barren", "barren"),
	SAND_SEA(9, "sand dunes", "eolian sand"),
	ICE_SHEET(22, "ice sheet", "ice sheet"),
	BOILING_SEA(23, "boiling sea", "hydrothermal sea"),
	MOONSCAPE(64, "moonscape", "regolith"),
	MAGMA_SEA(65, "magma sea", "lava sea"),
	CRYOGEN_SEA(66, "cryogen sea", "cryogen sea"),
	GAS_GIANT(67, "gas giant", "gas giant"),
	STAR(68, "star", "star"),
	NEUTRON_STAR(69, "neutron star", "neutron star"),
	EVENT_HORIZON(70, "black hole", "event horizon"),
	FARMLAND(32, "farmland", "farmland"),
	URBAN(33, "urban", "urban"),
	RUINS(34, "ruins", "ruins"),
	BIOLUMINESCENT(112, "permanent night", "bioluminescent flora"),
	DEAD(113, "dead land", "dead land"),
	MAGIC_GARDEN(114, "magic garden", "magic garden"),
	ELEMENTAL_CHAOS(115, "elemental chaos", "elemental chaos"),
	OOZE(116, "ooze", "giant slime");
	//
	public final byte code;
	public final String commonName;
	public final String technicalName;
	
	Biome(int biomeCode, String commonName, String technicalName){
		this.code = (byte)biomeCode;
		this.commonName = commonName;
		this.technicalName = technicalName;
	}
	
	public byte getCode(){
		return code;
	}
	
	public static Biome fromCode(byte biomeCode){
		return _fromCode(biomeCode);
	}
	public static Biome fromCode(int biomeCode){
		return _fromCode(biomeCode);
	}
	private static Biome _fromCode(int biomeCode){
		return switch(biomeCode) {
			case 0 -> UNKNOWN;
			case 1 -> WETLAND;
			case 2 -> JUNGLE;
			case 3 -> SEASONAL_FOREST;
			case 4 -> NEEDLELEAF_FOREST;
			case 5 -> GRASSLAND;
			case 6 -> DESERT_SHRUBLAND;
			case 7 -> TUNDRA;
			case 8 -> BARREN;
			case 9 -> SAND_SEA;
			case 17 -> FRESHWATER;
			case 18 -> SEA_FOREST;
			case 19 -> TROPICAL_REEF;
			case 20 -> ROCKY_SHALLOWS;
			case 16 -> DEEP_OCEAN;
			case 21 -> SHALLOW_OCEAN;
			case 22 -> ICE_SHEET;
			case 23 -> BOILING_SEA;
			case 32 -> FARMLAND;
			case 33 -> URBAN;
			case 34 -> RUINS;
			case 64 -> MOONSCAPE;
			case 65 -> MAGMA_SEA;
			case 66 -> CRYOGEN_SEA;
			case 67 -> GAS_GIANT;
			case 68 -> STAR;
			case 69 -> NEUTRON_STAR;
			case 70 -> EVENT_HORIZON;
			case 112 -> BIOLUMINESCENT;
			case 113 -> DEAD;
			case 114 -> MAGIC_GARDEN;
			case 115 -> ELEMENTAL_CHAOS;
			case 116 -> OOZE;
			default -> UNKNOWN;
		};
	}
}