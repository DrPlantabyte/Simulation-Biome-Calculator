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
 <tr><th>Code</th><th>Biome</th><th>Technical Name</th><th>Common Name</th><th>Description</th></tr>
 <tr><td>   0</td><td>UNKNOWN           </td><td>Unknown               </td><td>Unknown          </td><td>Represents an absence of data                           </td></tr>
 <tr><td colspan="5">  <i>Terrestrial Biomes</i>                                                                                                                  </td></tr>
 <tr><td>   1</td><td>WETLAND           </td><td>Wetland               </td><td>Swamp            </td><td>Permanent wetland habitat                               </td></tr>
 <tr><td>   2</td><td>JUNGLE            </td><td>Tropical rainforest   </td><td>Jungle           </td><td>Tropical rainforest                                     </td></tr>
 <tr><td>   3</td><td>SEASONAL_FOREST   </td><td>Temperate forest      </td><td>Deciduous forest </td><td>Deciduous broadleaf forest                              </td></tr>
 <tr><td>   4</td><td>NEEDLELEAF_FOREST </td><td>Needleleaf forest     </td><td>Evergreen forest </td><td>Borial, alpine, and taiga evergreen forests             </td></tr>
 <tr><td>   5</td><td>GRASSLAND         </td><td>Grassland             </td><td>Grassland        </td><td>Grasslands, prairies, plains, and savannahs             </td></tr>
 <tr><td>   6</td><td>DESERT_SHRUBLAND  </td><td>Xeric shrubland       </td><td>Desert           </td><td>Deserts with sparse vegitation                          </td></tr>
 <tr><td>   7</td><td>TUNDRA            </td><td>Tundra                </td><td>Tundra           </td><td>Habitat that is too cold for forests to grow            </td></tr>
 <tr><td>   8</td><td>BARREN            </td><td>Barren                </td><td>Barren           </td><td>Desert with virtually no vegetation                     </td></tr>
 <tr><td>   9</td><td>SAND_SEA          </td><td>Eolian sand           </td><td>Sand dunes       </td><td>Sand dunes with virtually no vegetation                 </td></tr>
 <tr><td colspan="5">  <i>Aquatic Biomes</i>                                                                                                                      </td></tr>
 <tr><td>  16</td><td>DEEP_OCEAN        </td><td>Deep ocean            </td><td>Ocean            </td><td>Deep ocean                                              </td></tr>
 <tr><td>  17</td><td>FRESHWATER        </td><td>Freshwater            </td><td>Freshwater       </td><td>Lakes and rivers                                        </td></tr>
 <tr><td>  18</td><td>SEA_FOREST        </td><td>Marine forest         </td><td>Seaweed forest   </td><td>Kelp forests and seagrass meadows                       </td></tr>
 <tr><td>  19</td><td>TROPICAL_REEF     </td><td>Tropical reef         </td><td>Coral reef       </td><td>Coral reefs                                             </td></tr>
 <tr><td>  20</td><td>ROCKY_SHALLOWS    </td><td>Rocky shallows        </td><td>Rocky shallows   </td><td>Shallow marine habitat with sparse flora                </td></tr>
 <tr><td>  21</td><td>SHALLOW_OCEAN     </td><td>Shallow ocean         </td><td>Shallow ocean    </td><td>Shallow ocean, such as a coastal shelf                  </td></tr>
 <tr><td>  22</td><td>ICE_SHEET         </td><td>Ice sheet             </td><td>Ice sheet        </td><td>Permanent ice                                           </td></tr>
 <tr><td>  23</td><td>BOILING_SEA       </td><td>Hydrothermal sea      </td><td>Boiling sea      </td><td>Water body so hot that it boils                         </td></tr>
 <tr><td colspan="5">  <i>Artificial Biomes</i>                                                                                                                   </td></tr>
 <tr><td>  32</td><td>FARMLAND          </td><td>Farmland              </td><td>Farmland         </td><td>Agriculture land (eg crop fields and pastures)          </td></tr>
 <tr><td>  33</td><td>URBAN             </td><td>Urban                 </td><td>Urban            </td><td>Cities and other artificial landscapes                  </td></tr>
 <tr><td>  34</td><td>RUINS             </td><td>Ruins                 </td><td>Ruins            </td><td>Abandoned or destroyed urban areas                      </td></tr>
 <tr><td>  35</td><td>POLLUTED_WASTELAND</td><td>Toxic wasteland       </td><td>Industrial barrens</td><td>Land too polluted to support terrestrial life          </td></tr>
 <tr><td>  36</td><td>POLLUTED_WASTEWATER</td><td>Toxic water          </td><td>Hypoxic water    </td><td>Water too polluted to support aquatic life              </td></tr>
 <tr><td colspan="5">  <i>Atronomical "Biomes"</i>                                                                                                                </td></tr>
 <tr><td>  64</td><td>MOONSCAPE         </td><td>Regolith              </td><td>Moonscape        </td><td>Completely inhospitable rock and dust                   </td></tr>
 <tr><td>  65</td><td>MAGMA_SEA         </td><td>Lava sea              </td><td>Magma sea        </td><td>Permanently molten lava                                 </td></tr>
 <tr><td>  66</td><td>CRYOGEN_SEA       </td><td>Cryogen sea           </td><td>Cryogen sea      </td><td>Bodies of liquid nitrogen or methane                    </td></tr>
 <tr><td>  67</td><td>GAS_GIANT         </td><td>Gas giant             </td><td>Gas giant        </td><td>"Surface" of a gas giant                                </td></tr>
 <tr><td>  68</td><td>STAR              </td><td>Star                  </td><td>Star             </td><td>Surface of a star                                       </td></tr>
 <tr><td>  69</td><td>NEUTRON_STAR      </td><td>Neutron star          </td><td>Neutron star     </td><td>Surface of a nuetron star                               </td></tr>
 <tr><td>  70</td><td>EVENT_HORIZON     </td><td>Event horizon         </td><td>Black hole       </td><td>"Surface" of a black hole                               </td></tr>
 <tr><td colspan="5">  <i>Fantasy Biomes</i>                                                                                                                  </td></tr>
 <tr><td> 112</td><td>BIOLUMINESCENT    </td><td>Bioluminescent flora  </td><td>Permanent night  </td><td>Permanently dark habitat with glowing flora             </td></tr>
 <tr><td> 113</td><td>DEAD              </td><td>Dead land             </td><td>Dead land        </td><td>Dead (or undead) land                                   </td></tr>
 <tr><td> 114</td><td>MAGIC_GARDEN      </td><td>Magic garden          </td><td>Magic garden     </td><td>Magical paradise                                        </td></tr>
 <tr><td> 115</td><td>ELEMENTAL_CHAOS   </td><td>Elemental chaos       </td><td>Elemental chaos  </td><td>Elemental phenomana (floating rock, unmeltable ice, etc)</td></tr>
 <tr><td> 116</td><td>OOZE              </td><td>Giant slime           </td><td>Ooze             </td><td>Living landscape, such as an ocean-sized amoeba         </td></tr>
 </table>
 </p>
 <p><b>Warning:</b> Do not rely on the <code>ordinal()</code> value of this enum! Future versions of this library may
 re-order the enum if new biomes are added. Use the biome codes instead, converting to and from the enum using the
 <code>toBiomeCode(...)</code> and <code>fromBiomeCode(...)</code> functions.</p>
 */
public enum Biome {
	/** Represents an absence of data */
	UNKNOWN(0, "unknown", "unknown"),
	// terrestrial biomes
	/** Permanent wetland habitat */
	WETLAND(1, "swamp", "wetland"),
	/** Tropical rainforest */
	JUNGLE(2, "jungle", "tropical rainforest"),
	/** Deciduous broadleaf forest  */
	SEASONAL_FOREST(3, "deciduous forest", "temperate forest"),
	/** Borial, alpine, and taiga evergreen forests */
	NEEDLELEAF_FOREST(4, "evergreen forest", "needleleaf forest"),
	/** Grasslands, prairies, plains, and savannahs */
	GRASSLAND(5, "grassland", "grassland"),
	/** Deserts with sparse vegitation  */
	DESERT_SHRUBLAND(6, "desert", "xeric shrubland"),
	/** Habitat that is too cold for forests to grow  */
	TUNDRA(7, "tundra", "tundra"),
	// aquatic biomes
	/** Lakes and rivers  */
	FRESHWATER(17, "freshwater", "freshwater"),
	/** Kelp forests and seagrass meadows */
	SEA_FOREST(18, "seaweed forest", "marine forest"),
	/** Coral reefs */
	TROPICAL_REEF(19, "coral reef", "tropical reef"),
	/** Shallow marine habitat with sparse flora */
	ROCKY_SHALLOWS(20, "rocky shallows", "rocky shallows"),
	/** Deep ocean */
	DEEP_OCEAN(16, "ocean", "deep ocean"),
	/** Shallow ocean, such as a coastal shelf */
	SHALLOW_OCEAN(21, "shallow ocean", "shallow ocean"),
	/** Desert with virtually no vegetation */
	BARREN(8, "barren", "barren"),
	/** Sand dunes with virtually no vegetation */
	SAND_SEA(9, "sand dunes", "eolian sand"),
	/** Permanent ice */
	ICE_SHEET(22, "ice sheet", "ice sheet"),
	/** Water body so hot that it boils */
	BOILING_SEA(23, "boiling sea", "hydrothermal sea"),
	/** Inhospitable rock and dust, completely devoid of life */
	MOONSCAPE(64, "moonscape", "regolith"),
	/** Permanently molten rock */
	MAGMA_SEA(65, "magma sea", "lava sea"),
	/** Bodies of liquid nitrogen or other cryogenic liquid */
	CRYOGEN_SEA(66, "cryogen sea", "cryogen sea"),
	/** "Surface" of a gas giant */
	GAS_GIANT(67, "gas giant", "gas giant"),
	/** Surface of a star */
	STAR(68, "star", "star"),
	/** Surface of a nuetron star */
	NEUTRON_STAR(69, "neutron star", "neutron star"),
	/** "Surface" of a black hole */
	EVENT_HORIZON(70, "black hole", "event horizon"),
	// Artificial biomes
	/** Agriculture land (eg crop fields and pastures)  */
	FARMLAND(32, "farmland", "farmland"),
	/** Cities and other artificial landscapes */
	URBAN(33, "urban", "urban"),
	/** Abandoned or destroyed urban areas  */
	RUINS(34, "ruins", "ruins"),
	/** Abandoned or destroyed urban areas  */
	POLLUTED_WASTELAND(35, "toxic wasteland", "industrial barrens"),
	/** Abandoned or destroyed urban areas  */
	POLLUTED_WASTEWATER(36, "toxic water", "hypoxic water"),
	// Fantasy biomes
	/** Permanently dark habitat with glowing flora  */
	BIOLUMINESCENT(112, "permanent night", "bioluminescent flora"),
	/** Dead (or undead) land  */
	DEAD(113, "dead land", "dead land"),
	/** Magical paradise */
	MAGIC_GARDEN(114, "magic garden", "magic garden"),
	/** Floating rocks, never-melt ice, dancing fire, etc. */
	ELEMENTAL_CHAOS(115, "elemental chaos", "elemental chaos"),
	/** Living landscape, such as an ocean-sized amoeba */
	OOZE(116, "ooze", "giant slime");
	//

	private final byte biomeCode;
	private final String commonName;
	private final String technicalName;

	/**
	 * Biome enum constructor
	 * @param biomeCode Biome code (must be unique)
	 * @param commonName Common name (in American English) for this biome, lowercase
	 * @param technicalName Technical name (in American English) for this biome, lowercase
	 */
	Biome(int biomeCode, String commonName, String technicalName){
		this.biomeCode = (byte)biomeCode;
		this.commonName = commonName;
		this.technicalName = technicalName;
	}

	/**
	 * Converts a multi-dimensional array of biome codes to a corresponding array of Biome enums
	 * @param byteArray an array of bytes
	 * @return an array of Biome enum instances
	 */
	public static Biome[][][] convertByteArray(byte[][][] byteArray){
		var out = new Biome[byteArray.length][][];
		for(int i = 0; i < out.length; ++i){
			out[i] = convertByteArray(byteArray[i]);
		}
		return out;
	}

	/**
	 * Converts a multi-dimensional array of biome codes to a corresponding array of Biome enums
	 * @param byteArray an array of bytes
	 * @return an array of Biome enum instances
	 */
	public static Biome[][] convertByteArray(byte[][] byteArray){
		var out = new Biome[byteArray.length][];
		for(int i = 0; i < out.length; ++i){
			out[i] = convertByteArray(byteArray[i]);
		}
		return out;
	}

	/**
	 * Converts an array of biome codes to a corresponding array of Biome enums
	 * @param byteArray an array of bytes
	 * @return an array of Biome enum instances
	 */
	public static Biome[] convertByteArray(byte[] byteArray){
		var out = new Biome[byteArray.length];
		for(int i = 0; i < out.length; ++i){
			out[i] = fromBiomeCode(byteArray[i]);
		}
		return out;
	}

	/**
	 * Converts a multi-dimensional array of Biome enums to their corresponding 7-bit biome codes (as a byte array)
	 * @param biomeArray an array of Biome enums
	 * @return an array of biome codes as bytes
	 */
	public static byte[][][] convertBiomeArray(Biome[][][] biomeArray){
		var out = new byte[biomeArray.length][][];
		for(int i = 0; i < out.length; ++i){
			out[i] = convertBiomeArray(biomeArray[i]);
		}
		return out;
	}

	/**
	 * Converts a multi-dimensional array of Biome enums to their corresponding 7-bit biome codes (as a byte array)
	 * @param biomeArray an array of Biome enums
	 * @return an array of biome codes as bytes
	 */
	public static byte[][] convertBiomeArray(Biome[][] biomeArray){
		var out = new byte[biomeArray.length][];
		for(int i = 0; i < out.length; ++i){
			out[i] = convertBiomeArray(biomeArray[i]);
		}
		return out;
	}

	/**
	 * Converts an array of Biome enums to their corresponding 7-bit biome codes (as a byte array)
	 * @param biomeArray an array of Biome enums
	 * @return an array of biome codes as bytes
	 */
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
		return fromBiomeCode((int)biomeCode);
	}

	public static Biome fromBiomeCode(int biomeCode){
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
			case 16 -> DEEP_OCEAN;
			case 17 -> FRESHWATER;
			case 18 -> SEA_FOREST;
			case 19 -> TROPICAL_REEF;
			case 20 -> ROCKY_SHALLOWS;
			case 21 -> SHALLOW_OCEAN;
			case 22 -> ICE_SHEET;
			case 23 -> BOILING_SEA;
			case 32 -> FARMLAND;
			case 33 -> URBAN;
			case 34 -> RUINS;
			case 35 -> POLLUTED_WASTELAND;
			case 36 -> POLLUTED_WASTEWATER;
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