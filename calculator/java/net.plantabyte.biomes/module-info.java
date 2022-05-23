/**
 <p>Dr. Plantabyte's biome calculator for Earth and simulated exoplanets.</p>
 <p>
 This module provides a single package, {@link net.plantabyte.biomes}, which
 contains an enum of Dr. Plantabyte biomes ({@link net.plantabyte.biomes.Biome})
 and a {@link net.plantabyte.biomes.BiomeCalculator} class for predicting the
 biome for a given Earthly or exoplanet environmental parameters.</p>
 <p></p>
 <p><b><u>Plantabyte Biomes</u></b></p>
 <p>Dr. Plantabyte's biomes are based on various sources from the fields of remote
 sensing, marine biology, and astrobiology research, combined with machine
 learning and a few expert guestimates from plant biologist
 Dr. Christopher C. Hall. The result is a realistic biome classification system
 that covers both Earthly biomes and plausible exoplanet environments. A few
 abiotic "biomes" are included as well to facilitate use in simulations for
 graphic design, story-telling, and games.</p>
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
 <tr><td>   35 </td><td>POLLUTED_WASTELAND</td><td>Land too polluted to support terrestrial life    </td></tr>
 <tr><td>   36 </td><td>POLLUTED_WASTEWATER</td><td>Water too polluted to support aquatic life      </td></tr>
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
 <p></p>
 
 <p><b><u>Example Usage</u></b></p>
 <p><pre>
 final var EarthBC = new BiomeCalculator();
 Consumer&lt;HashMap&lt;String,Double&gt;&gt; printBiome = (HashMap&lt;String,Double&gt; env)-&gt;System.out.println(
 &nbsp;&nbsp;EarthBC.classifyBiome(
 &nbsp;&nbsp;&nbsp;&nbsp;env.get("mean_solar_flux_Wpm2"),
 &nbsp;&nbsp;&nbsp;&nbsp;env.get("pressure_kPa"),
 &nbsp;&nbsp;&nbsp;&nbsp;env.get("altitude_m"),
 &nbsp;&nbsp;&nbsp;&nbsp;env.get("mean_temp_C"),
 &nbsp;&nbsp;&nbsp;&nbsp;env.get("temp_var_C"),
 &nbsp;&nbsp;&nbsp;&nbsp;env.get("annual_precip_mm")
 &nbsp;&nbsp;)
 );
 
 var Macapa_Brazil = new HashMap&lt;String,Double&gt;();
 Macapa_Brazil.put("mean_solar_flux_Wpm2", 798.);
 Macapa_Brazil.put("pressure_kPa", 101.3);
 Macapa_Brazil.put("altitude_m", 20.);
 Macapa_Brazil.put("mean_temp_C", 28.2);
 Macapa_Brazil.put("temp_var_C", 3.2);
 Macapa_Brazil.put("annual_precip_mm", 2200.);
 printBiome.accept(Macapa_Brazil);
 
 var Fairbanks_Alaska = new HashMap&lt;String,Double&gt;();
 Fairbanks_Alaska.put("mean_solar_flux_Wpm2", 356.);
 Fairbanks_Alaska.put("pressure_kPa", 99.8);
 Fairbanks_Alaska.put("altitude_m", 136.);
 Fairbanks_Alaska.put("mean_temp_C", -2.0);
 Fairbanks_Alaska.put("temp_var_C", 21.7);
 Fairbanks_Alaska.put("annual_precip_mm", 296.);
 printBiome.accept(Fairbanks_Alaska);
 </pre></p>
 
 */
module net.plantabyte.biomes{
	exports net.plantabyte.biomes;
}