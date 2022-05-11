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
			final double mean_surface_pressure_kPa
	){
		this.planet_mass_kg = planet_mass_kg;
		this.planet_mean_radius_km = planet_mean_radius_km;
		this.axis_tilt_deg = axis_tilt_deg;
		this.toa_solar_flux_Wpm2 = toa_solar_flux_Wpm2;
		this.mean_surface_pressure_kPa = mean_surface_pressure_kPa;
		this.exoplanet = true;
		this.tidal_lock = tidal_lock;
	}
	// TODO: add with...(...) modifier functions
}