import cython
from libc.math cimport sin, cos, exp, log10, pow
from biome_enum import Biome

cpdef unsigned char classify_biome(
    float mean_solar_flux_Wpm2,
    float pressure_kPa,
    float altitude_m,
    float mean_temp_C,
    float temp_var_C,
    float annual_precip_mm
):
	## terrestrial biomes
	if altitude_m > 0:
		### rescale to normalize so that distance calcs aren't biased
		float norm_sol_flux = rescale(mean_solar_flux_Wpm2, 0.0, 1976.0277)
		float norm_mtemp = rescale(mean_temp_C, -24.903875, 54.133900)
		float norm_vtemp = rescale(temp_var_C, 0.12730642, 42.466022)
		float norm_precip = rescale(annual_precip_mm, 0.0, 58917.738)
	## marine biomes
	## extreme biomes
	## astronomical biomes
	## Done!
    return Biome.UNKOWN.value

cpdef unsigned char classify_biome_on_planet(
    float planet_mass_kg,
    float planet_mean_radius_km,
    float toa_solar_flux_Wpm2,
    float axis_tilt_deg,
    bint tidal_lock,
    float mean_surface_pressure_kPa,
    float altitude_m,
    float mean_temp_C,
    float temp_var_C,
    float annual_precip_mm,
    float latitude,
    float longitude
):
    cdef float pi = 3.14159265358979
    cdef float two_over_pi = 0.5 * pi
    cdef float deg2Rad = pi / 180
    #
    cdef float G = 6.67430e-11 # N m2 / kg2
    cdef radius_m = (planet_mean_radius_km * 1000) + altitude_m
    cdef float gravity_m_per_s2 = G * planet_mass_kg / (radius_m * radius_m)
    cdef above_sealevel_m = altitude_m
    if above_sealevel_m < 0:
        above_sealevel_m = 0
    cdef float K = mean_temp_C + 273.15
    cdef float R = 8.314510  # j/K/mole
    cdef float air_molar_mass = 0.02897  # kg/mol
    cdef float epsilon_air = 3.46391e-5 # Absorption per kPa (1360 = 1371 * 10^(-eps * 101) )
    cdef float pressure_kPa = mean_surface_pressure_kPa * exp(-(air_molar_mass * gravity_m_per_s2 * altitude_m)/(R*K))
    cdef max_flux = toa_solar_flux_Wpm2 * pow(10, -epsilon_air * pressure_kPa)
    cdef float mean_solar_flux_Wpm2 = 0
    if tidal_lock:
        mean_solar_flux_Wpm2 = max_flux * two_over_pi * cos(latitude) * clip(cos(longitude), 0, 1)
    else:
        mean_solar_flux_Wpm2 = max_flux * two_over_pi * 0.5 * (
                clip(cos(deg2Rad * (latitude - axis_tilt_deg)), 0, 1)
                + clip(cos(deg2Rad * (latitude + axis_tilt_deg)), 0, 1)
        )
    return classify_biome(
        mean_solar_flux_Wpm2,
        pressure_kPa,
        altitude_m,
        mean_temp_C,
        temp_var_C,
        annual_precip_mm
    )

cpdef float clip(float x, float xmin, float xmax):
    if x < xmin:
        return xmin
    if x > xmax:
        return xmax
    return x

cpdef float rescale(x, xmin, xmax):
	return (x - xmin) / (xmax - xmin)