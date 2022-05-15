package net.plantabyte.biomes;

public class BiomeCalculator {
	//
	private final double planet_mass_kg;
	private final double planet_mean_radius_km;
	private final double toa_solar_flux_Wpm2;
	private final double axis_tilt_deg;
	private final boolean tidal_lock;
	private final double mean_surface_pressure_kPa;
	private final boolean exoplanet;
	
	public BiomeCalculator() {
		// Earth-like planet
		planet_mass_kg = 5.972e24;
		planet_mean_radius_km = 6.371e3;
		toa_solar_flux_Wpm2 = 1373;
		axis_tilt_deg = 23;
		mean_surface_pressure_kPa = 101.3;
		tidal_lock = false;
		exoplanet = false;
	}
	
	public BiomeCalculator(
			final double planet_mass_kg,
			final double planet_mean_radius_km,
			final double axis_tilt_deg,
			final boolean tidal_lock,
			final double toa_solar_flux_Wpm2,
			final double mean_surface_pressure_kPa,
			final boolean is_exoplanet
	){
		this.planet_mass_kg = planet_mass_kg;
		this.planet_mean_radius_km = planet_mean_radius_km;
		this.axis_tilt_deg = axis_tilt_deg;
		this.toa_solar_flux_Wpm2 = toa_solar_flux_Wpm2;
		this.mean_surface_pressure_kPa = mean_surface_pressure_kPa;
		this.exoplanet = is_exoplanet;
		this.tidal_lock = tidal_lock;
	}
	public BiomeCalculator withPlanetMass(double planet_mass_kg){
		return new BiomeCalculator(
				planet_mass_kg,
				this.planet_mean_radius_km,
				this.axis_tilt_deg,
				this.tidal_lock,
				this.toa_solar_flux_Wpm2,
				this.mean_surface_pressure_kPa,
				this.exoplanet
		);
	}
	public BiomeCalculator withPlanetRadius(double planet_mean_radius_km){
		return new BiomeCalculator(
				this.planet_mass_kg,
				planet_mean_radius_km,
				this.axis_tilt_deg,
				this.tidal_lock,
				this.toa_solar_flux_Wpm2,
				this.mean_surface_pressure_kPa,
				this.exoplanet
		);
	}
	public BiomeCalculator withAxisTilt(double axis_tilt_deg){
		return new BiomeCalculator(
				this.planet_mass_kg,
				this.planet_mean_radius_km,
				axis_tilt_deg,
				this.tidal_lock,
				this.toa_solar_flux_Wpm2,
				this.mean_surface_pressure_kPa,
				this.exoplanet
		);
	}
	public BiomeCalculator withTidalLock(boolean isTidallyLocked){
		return new BiomeCalculator(
				this.planet_mass_kg,
				this.planet_mean_radius_km,
				this.axis_tilt_deg,
				isTidallyLocked,
				this.toa_solar_flux_Wpm2,
				this.mean_surface_pressure_kPa,
				this.exoplanet
		);
	}
	public BiomeCalculator withTOASolarFlux(double toa_solar_flux_Wpm2){
		return new BiomeCalculator(
				this.planet_mass_kg,
				this.planet_mean_radius_km,
				this.axis_tilt_deg,
				this.tidal_lock,
				toa_solar_flux_Wpm2,
				this.mean_surface_pressure_kPa,
				this.exoplanet
		);
	}
	public BiomeCalculator withSurfacePressure(double mean_surface_pressure_kPa){
		return new BiomeCalculator(
				this.planet_mass_kg,
				this.planet_mean_radius_km,
				this.axis_tilt_deg,
				this.tidal_lock,
				this.toa_solar_flux_Wpm2,
				mean_surface_pressure_kPa,
				this.exoplanet
		);
	}
	public BiomeCalculator asExoplanet(boolean is_exoplanet){
		return new BiomeCalculator(
				this.planet_mass_kg,
				this.planet_mean_radius_km,
				this.axis_tilt_deg,
				this.tidal_lock,
				this.toa_solar_flux_Wpm2,
				this.mean_surface_pressure_kPa,
				is_exoplanet
		);
	}
	// classifiers
	
	private static final Biome[] ref_classes = {Biome.WETLAND, Biome.JUNGLE, Biome.SEASONAL_FOREST, Biome.NEEDLELEAF_FOREST, Biome.GRASSLAND, Biome.DESERT_SHRUBLAND, Biome.TUNDRA, Biome.BARREN, Biome.SAND_SEA};
	private static final float[][][] ref_points = { // size = [9][5][4]
//// wetlands
			{{0.97589505F, 0.6692817F, 0.09676683F, 0.42183435F},
					{0.2872733F, 0.5562218F, 0.21704593F, 0.3098737F},
					{0.95833284F, 0.6877248F, 0.12377492F, 0.2995282F},
					{0.6171483F, 0.47020113F, 0.4836682F, 0.22195342F},
					{0.81850535F, 0.60123855F, 0.25867933F, 0.31303504F}},
//// jungle
			{{0.7665621F, 0.5300055F, 0.2408872F, 0.3123359F},
					{0.99121696F, 0.6713649F, 0.07588506F, 0.40304184F},
					{0.98553646F, 0.67212886F, 0.08356771F, 0.3337861F},
					{0.9209426F, 0.59560406F, 0.15855226F, 0.3750781F},
					{0.99228674F, 0.67052644F, 0.07420062F, 0.49766815F}},
//// seasonalForest
			{{0.82307386F, 0.54830164F, 0.28397045F, 0.32422626F},
					{0.95406234F, 0.68983954F, 0.16054682F, 0.29840717F},
					{0.5337313F, 0.44197488F, 0.4220576F, 0.24119267F},
					{0.70596063F, 0.5029748F, 0.37620285F, 0.26919958F},
					{0.65009725F, 0.41467762F, 0.53735024F, 0.24624129F}},
//// needleleafForest
			{{0.8442506F, 0.513412F, 0.23853904F, 0.31593102F},
					{0.4755671F, 0.42182055F, 0.32860836F, 0.25947723F},
					{0.69879943F, 0.5263777F, 0.3583926F, 0.24800086F},
					{0.6385724F, 0.44265494F, 0.30205786F, 0.41645652F},
					{0.59855306F, 0.41948298F, 0.4608879F, 0.21030518F}},
//// grassland
			{{0.9590115F, 0.69129807F, 0.14321554F, 0.33431706F},
					{0.64463437F, 0.51307285F, 0.6764352F, 0.17131203F},
					{0.75970644F, 0.53838587F, 0.34264302F, 0.25237092F},
					{0.9574419F, 0.76865923F, 0.21147878F, 0.2162868F},
					{0.7787093F, 0.64991206F, 0.49281284F, 0.1717132F}},
//// desert
			{{0.8768907F, 0.68539584F, 0.30395174F, 0.18175352F},
					{0.85951805F, 0.75583154F, 0.43008733F, 0.13515931F},
					{0.9133944F, 0.80276865F, 0.33543584F, 0.15386288F},
					{0.95464563F, 0.8058968F, 0.2042541F, 0.1794926F},
					{0.7509371F, 0.62957406F, 0.44375542F, 0.1542665F}},
//// tundra
			{{0.4441414F, 0.30920148F, 0.4959661F, 0.24957538F},
					{0.4513571F, 0.23461857F, 0.732274F, 0.2127717F},
					{0.6739347F, 0.34742635F, 0.41046205F, 0.26215446F},
					{0.577827F, 0.32734275F, 0.62989986F, 0.22067626F},
					{0.37011942F, 0.15006503F, 0.65958476F, 0.18708763F}},
//// barren
			{{0.29481938F, 0.09472984F, 0.59135556F, 0.06860657F},
					{0.86539465F, 0.7506361F, 0.37203112F, 0.11493613F},
					{0.664666F, 0.6056427F, 0.46542227F, 0.14238815F},
					{0.6938545F, 0.43799615F, 0.30913985F, 0.2867542F},
					{0.8466273F, 0.53237015F, 0.44636855F, 0.16200702F}},
//// sandsea
			{{0.82119286F, 0.48783484F, 0.44511366F, 0.10902377F},
					{0.9354581F, 0.8444746F, 0.28542006F, 0.076657F},
					{0.75143087F, 0.70467633F, 0.602095F, 0.09906711F},
					{0.8729486F, 0.81519806F, 0.4026484F, 0.0783796F},
					{0.24349129F, 0.7866096F, 0.45044297F, 0.11177942F}}
	};
	
	public Biome classifyBiome(
			double mean_solar_flux_Wpm2,
			double pressure_kPa,
			double altitude_m,
			double mean_temp_C,
			double temp_var_C,
			double annual_precip_mm
	) {
		Biome biome_code = Biome.UNKNOWN;
		//// constants and variables
		double min_rain_limit_mm = 110;
		double max_rain_limit_mm = 6000; // too much rain and we'll call it a wetland instead of a jungle
		double photic_zone_min_solar_flux_Wpm2 = 35;
		double wave_disruption_depth_m = -6; // corals, seagrasses, kelps, etc cannot grow above this depth
		double epsilon_water = 0.013333;  // Absorption per meter (150m == 1% transmission (0.01 = 10^(-epsilon*150))
		double benthic_solar_flux = mean_solar_flux_Wpm2 * Math.pow(10,
				epsilon_water * altitude_m
		); // <- note: altitude is negative here
		double boiling_point_C = boiling_point(pressure_kPa);
		//// terrestrial biomes
		if(altitude_m > 0) {
			if(annual_precip_mm > max_rain_limit_mm) {
				biome_code = Biome.WETLAND;
			} else {
				////// rescale to normalize so that distance calcs aren't biased
				double closest_dist = 1e35;
				double norm_sol_flux = rescale(mean_solar_flux_Wpm2, 0.0, 800.);
				double norm_mtemp = rescale(mean_temp_C, -20., 50.);
				double norm_vtemp = rescale(temp_var_C, 0., 35.);
				double norm_precip = rescale(Math.sqrt(annual_precip_mm), 0.0, 75.);
				for(int bclass = 0; bclass < 9; ++bclass) {
					for(int refpt = 0; refpt < 5; ++refpt) {
						double d = dist4fd(ref_points[bclass][refpt][0], ref_points[bclass][refpt][1],
								ref_points[bclass][refpt][2], ref_points[bclass][refpt][3],
								norm_sol_flux, norm_mtemp, norm_vtemp, norm_precip
						);
						if(d < closest_dist) {
							closest_dist = d;
							biome_code = ref_classes[bclass];
						}
					}
				}
			}
			if(biome_code == Biome.JUNGLE && temp_var_C > 6.0) {
				// too much variation for jungle, actually grassland
				biome_code = Biome.GRASSLAND;
			}
		} else {
			//// marine biomes
			if(benthic_solar_flux >= photic_zone_min_solar_flux_Wpm2) {
				// sea floor in photic zone
				if(mean_temp_C > 5 && mean_temp_C < 20 && altitude_m < wave_disruption_depth_m) {
					biome_code = Biome.SEA_FOREST;
				} else if(mean_temp_C >= 20 && mean_temp_C < 30 && altitude_m < wave_disruption_depth_m) {
						biome_code = Biome.TROPICAL_REEF;
					} else {
						biome_code = Biome.ROCKY_SHALLOWS;
					}
			} else if(altitude_m > -200) {
				biome_code = Biome.SHALLOW_OCEAN;
			} else {
				biome_code = Biome.DEEP_OCEAN;
			}
		}
		//// extreme biomes
		if(altitude_m > 0) {
			if(annual_precip_mm < min_rain_limit_mm) {
				if(mean_temp_C > 15) {
					biome_code = Biome.SAND_SEA;
				} else if(mean_temp_C <= 15) {
					biome_code = Biome.BARREN;
				}
			}
			if(mean_temp_C >= boiling_point_C) {
				biome_code = Biome.MOONSCAPE;
			}
		} else {
			if(mean_temp_C >= boiling_point_C) {
				biome_code = Biome.BOILING_SEA;
			}
		}
		if((mean_temp_C < boiling_point_C) && (mean_temp_C + temp_var_C) < 0) {
			biome_code = Biome.ICE_SHEET;
		}
		//// Done!
		return biome_code;
	}
	
	public Biome classifyBiomeOnPlanet(
			double altitude_m,
			double mean_temp_C,
			double temp_var_C,
			double annual_precip_mm,
			double latitude,
			double longitude
			){
		// TODO
		return Biome.UNKNOWN;
	}
	
	private static double dist4fd(float a1, float b1, float c1, float d1, double a2, double b2, double c2, double d2){
		double da = a2-a1;
		double db = b2-b1;
		double dc = c2-c1;
		double dd = d2-d1;
		return Math.sqrt(da*da + db*db + dc*dc + dd*dd);
	}
	
	private static double rescale(double x, double xmin, double xmax) {
		return (x - xmin) / (xmax - xmin);
	}
	
	private static double boiling_point(double pressure_kPa) {
		double ln_mbar = Math.log(pressure_kPa * 10);
		double x = ln_mbar;
		double x2 = x * ln_mbar;
		double x3 = x2 * ln_mbar;
		double lp = 0.051769 * x3 + 0.65545 * x2 + 10.387 * x - 10.619;
		double hp = 0.47092 * x3 - 8.2481 * x2 + 75.520 * x - 183.98;
		if(pressure_kPa< 101.3){
			return lp;
		}else{
			return hp;
		}
	}
	
	public double pressureAtDryAltitude(double altitude_m, double mean_temp_C) {
		double K = mean_temp_C + 273.15;
		double R = 8.314510;  // j/K/mole
		double air_molar_mass = 0.02897;  // kg/mol
		double gravity_m_per_s2 = gravity(this.planet_mass_kg, this.planet_mean_radius_km);
		double pressure_kPa = mean_surface_pressure_kPa * Math.exp(-(air_molar_mass * gravity_m_per_s2 * altitude_m)/(R*K));
		return pressure_kPa;
	}
	
	static double gravity(final double mass_kg, final double distance_km) {
		final double G = 6.6743015e-11; // N m2/kg2
		double distance_m = 1000. * distance_km;
		return G * (mass_kg) / (distance_m*distance_m);
	}
	
	private static double clip(double x, double xmin, double xmax) {
		if(x < xmin) return xmin;
		if(x > xmax) return xmax;
		return x;
	}
}