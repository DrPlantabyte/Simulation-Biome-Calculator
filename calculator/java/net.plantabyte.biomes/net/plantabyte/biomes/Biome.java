package net.plantabyte.biomes;

/**
 <p><b><u>Dr. Plantabyte's biomes for Earth and simulated exoplanets.</u></b></p>
 <p>These biomes are based on various sources from the fields of remote sensing,
 marine biology, and astrobiology research, combined with machine learning and a
 few expert guestimates from plant biologist Dr. Christopher C. Hall. The result
 is  a realistic biome classification system that covers both Earthly biomes and
 plausible exoplanet environments. A few  abiotic "biomes" are included as well
 to facilitate use in simulations for graphic design, story-telling, and games.
 </p>
 <p>The Biome enum represents Dr. Plantabyte's biomes for Earth and simulated
 exoplanets. The biomes include both Earthly biomes like tropical rainforests
 (jungle) and grasslands, as well as biomes that may exist on other planets,
 such as boiling seas.</p>
 <p>To bridge the gap between lay-person and technical names for the biomes,
 each Plantabyte biome has a common name
 ({@link net.plantabyte.biomes.Biome#commonName}) and a technical name
 ({@link Biome#getTechnicalName()}). For example, the </p>
 <p>Biomes are encoded as 7-bit codes consisting of 3 category bits and 4 biome
 code bits:<br>
 bits: <code>0b0yyyxxxx</code><br>
 <code>yyy</code> = biome category (0=terrestrial, 1=aquatic, 2=artificial, 4=astronomical, 7=fictional)<br>
 <code>xxxx</code> = biome code within category</p>
 <p>The full list of biomes and corresponding biome number codes are as follows:<br>
 <table border="1">
 <tr><th> Code </th><th>Name             </th><th>Description                                       </th></tr>
 <tr><td>    0 </td><td>UNKNOWN          </td><td>Unclassifiable biome                              </td></tr>
 <tr><td colspan="3">  <i>Terrestrial Biomes</i>                                                    </td></tr>
 <tr><td>    1 </td><td>WETLAND          </td><td>Permanent wetland                                 </td></tr>
 <tr><td>    2 </td><td>JUNGLE           </td><td>Tropical rainforest                               </td></tr>
 <tr><td>    3 </td><td>SEASONAL_FOREST  </td><td>Temperate deciduous forest                        </td></tr>
 <tr><td>    4 </td><td>NEEDLELEAF_FOREST</td><td>Temperate evergreen forest                        </td></tr>
 <tr><td>    5 </td><td>GRASSLAND        </td><td>Plains, prairies, and savannas                    </td></tr>
 <tr><td>    6 </td><td>DESERT_SHRUBLAND </td><td>Dry shrublands and less extreme deserts           </td></tr>
 <tr><td>    7 </td><td>TUNDRA           </td><td>Seasonal grasslands where it is too cold for trees</td></tr>
 <tr><td>    8 </td><td>BARREN           </td><td>Exposed rocks with little to no macroscopic life  </td></tr>
 <tr><td>    9 </td><td>SAND_SEA         </td><td>Sand dunes with little to no macroscopic life     </td></tr>
 <tr><td colspan="3">  <i>Aquatic Biomes</i>                                                        </td></tr>
 <tr><td>   17 </td><td>FRESHWATER       </td><td>Lakes and rivers                                  </td></tr>
 <tr><td>   18 </td><td>SEA_FOREST       </td><td>Seagrass meadows and seaweed forests              </td></tr>
 <tr><td>   19 </td><td>TROPICAL_REEF    </td><td>Coral reefs                                       </td></tr>
 <tr><td>   20 </td><td>ROCKY_SHALLOWS   </td><td>Low productivity shallow marine waters            </td></tr>
 <tr><td>   16 </td><td>DEEP_OCEAN       </td><td>Ocean                                             </td></tr>
 <tr><td>   21 </td><td>SHALLOW_OCEAN    </td><td>Shallow ocean regions where light reaches seabed  </td></tr>
 <tr><td>   22 </td><td>ICE_SHEET        </td><td>Frozen ocean or land covered in permanent ice     </td></tr>
 <tr><td>   23 </td><td>BOILING_SEA      </td><td>Water body so hot that it boils                   </td></tr>
 <tr><td colspan="3">  <i>Artificial Biomes</i>                                                     </td></tr>
 <tr><td>   32 </td><td>FARMLAND         </td><td>Cultivated land                                   </td></tr>
 <tr><td>   33 </td><td>URBAN            </td><td>Cities, streets, and other artificial structures  </td></tr>
 <tr><td>   34 </td><td>RUINS            </td><td>Abandoned urban areas being reclaimed by nature   </td></tr>
 <tr><td colspan="3">  <i>Astronomical "Biomes"</i>                                                 </td></tr>
 <tr><td>   64 </td><td>MOONSCAPE        </td><td>Lifeless dry dust and/or rock                     </td></tr>
 <tr><td>   65 </td><td>MAGMA_SEA        </td><td>Ocean of molten rock                              </td></tr>
 <tr><td>   66 </td><td>CRYOGEN_SEA      </td><td>Ocean of liquid cryogen (eg liquid nitrogen)      </td></tr>
 <tr><td>   67 </td><td>GAS_GIANT        </td><td>"Surface" of planet with extreme thick atmosphere </td></tr>
 <tr><td>   68 </td><td>STAR             </td><td>Surface of a star                                 </td></tr>
 <tr><td>   69 </td><td>NEUTRON_STAR     </td><td>Surface of a neutron star                         </td></tr>
 <tr><td>   70 </td><td>EVENT_HORIZON    </td><td>"Surface" of a black hole                         </td></tr>
 <tr><td colspan="3">  <i>Fantasy Biomes</i>                                                        </td></tr>
 <tr><td>  112 </td><td>BIOLUMINESCENT   </td><td>Permanently dark biome with bioluminescent flora  </td></tr>
 <tr><td>  113 </td><td>DEAD             </td><td>Dead (or undead) landscape                        </td></tr>
 <tr><td>  114 </td><td>MAGIC_GARDEN     </td><td>Magical paradise                                  </td></tr>
 <tr><td>  115 </td><td>ELEMENTAL_CHAOS  </td><td>Floating rocks, never-melt ice, dancing fire, etc.</td></tr>
 <tr><td>  116 </td><td>OOZE             </td><td>Living landscape, such as an ocean-sized amoeba   </td><td>
 </table></p>
 */
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
	public final byte biomeCode;
	public final String commonName;
	public final String technicalName;
	
	Biome(int biomeCode, String commonName, String technicalName){
		this.biomeCode = (byte)biomeCode;
		this.commonName = commonName;
		this.technicalName = technicalName;
	}
	
	
	public static Biome[][][] convertByteArray(byte[][][] byteArray){
		var out = new Biome[byteArray.length][][];
		for(int i = 0; i < out.length; ++i){
			out[i] = convertByteArray(byteArray[i]);
		}
		return out;
	}
	public static Biome[][] convertByteArray(byte[][] byteArray){
		var out = new Biome[byteArray.length][];
		for(int i = 0; i < out.length; ++i){
			out[i] = convertByteArray(byteArray[i]);
		}
		return out;
	}
	public static Biome[] convertByteArray(byte[] byteArray){
		var out = new Biome[byteArray.length];
		for(int i = 0; i < out.length; ++i){
			out[i] = fromBiomeCode(byteArray[i]);
		}
		return out;
	}
	
	public static byte[][][] convertBiomeArray(Biome[][][] biomeArray){
		var out = new byte[biomeArray.length][][];
		for(int i = 0; i < out.length; ++i){
			out[i] = convertBiomeArray(biomeArray[i]);
		}
		return out;
	}
	public static byte[][] convertBiomeArray(Biome[][] biomeArray){
		var out = new byte[biomeArray.length][];
		for(int i = 0; i < out.length; ++i){
			out[i] = convertBiomeArray(biomeArray[i]);
		}
		return out;
	}
	public static byte[] convertBiomeArray(Biome[] biomeArray){
		var out = new byte[biomeArray.length];
		for(int i = 0; i < out.length; ++i){
			out[i] = toBiomeCode(biomeArray[i]);
		}
		return out;
	}
	
	public String getCommonName(){ return commonName; }
	public String getTechnicalName(){ return technicalName; }
	
	public static byte toBiomeCode(Biome b){ return b.biomeCode; }
	
	public byte getBiomeCode(){
		return biomeCode;
	}
	
	public static Biome fromBiomeCode(byte biomeCode){
		return _fromBiomeCode(biomeCode);
	}
	public static Biome fromBiomeCode(int biomeCode){
		return _fromBiomeCode(biomeCode);
	}
	private static Biome _fromBiomeCode(int biomeCode){
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