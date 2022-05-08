import numpy
from numpy import ndarray
from ..biomes import Biome


ref_classes = [1, 2, 3, 4, 5, 6, 7, 8, 9]
## order of features: ['solar_flux', 'temperature_mean', 'temperature_range', 'sqrt_precipitation']
ref_points = numpy.asarray([
## wetlands
       [[0.97589505, 0.6692817 , 0.09676683, 0.42183435],
        [0.2872733 , 0.5562218 , 0.21704593, 0.3098737 ],
        [0.95833284, 0.6877248 , 0.12377492, 0.2995282 ],
        [0.6171483 , 0.47020113, 0.4836682 , 0.22195342],
        [0.81850535, 0.60123855, 0.25867933, 0.31303504]],
## jungle
       [[0.7665621 , 0.5300055 , 0.2408872 , 0.3123359 ],
        [0.99121696, 0.6713649 , 0.07588506, 0.40304184],
        [0.98553646, 0.67212886, 0.08356771, 0.3337861 ],
        [0.9209426 , 0.59560406, 0.15855226, 0.3750781 ],
        [0.99228674, 0.67052644, 0.07420062, 0.49766815]],
## seasonal forest
       [[0.82307386, 0.54830164, 0.28397045, 0.32422626],
        [0.95406234, 0.68983954, 0.16054682, 0.29840717],
        [0.5337313 , 0.44197488, 0.4220576 , 0.24119267],
        [0.70596063, 0.5029748 , 0.37620285, 0.26919958],
        [0.65009725, 0.41467762, 0.53735024, 0.24624129]],
## needleleaf forest
       [[0.8442506 , 0.513412  , 0.23853904, 0.31593102],
        [0.4755671 , 0.42182055, 0.32860836, 0.25947723],
        [0.69879943, 0.5263777 , 0.3583926 , 0.24800086],
        [0.6385724 , 0.44265494, 0.30205786, 0.41645652],
        [0.59855306, 0.41948298, 0.4608879 , 0.21030518]],
## grassland
       [[0.9590115 , 0.69129807, 0.14321554, 0.33431706],
        [0.64463437, 0.51307285, 0.6764352 , 0.17131203],
        [0.75970644, 0.53838587, 0.34264302, 0.25237092],
        [0.9574419 , 0.76865923, 0.21147878, 0.2162868 ],
        [0.7787093 , 0.64991206, 0.49281284, 0.1717132 ]],
## desert
       [[0.8768907 , 0.68539584, 0.30395174, 0.18175352],
        [0.85951805, 0.75583154, 0.43008733, 0.13515931],
        [0.9133944 , 0.80276865, 0.33543584, 0.15386288],
        [0.95464563, 0.8058968 , 0.2042541 , 0.1794926 ],
        [0.7509371 , 0.62957406, 0.44375542, 0.1542665 ]],
## tundra
       [[0.4441414 , 0.30920148, 0.4959661 , 0.24957538],
        [0.4513571 , 0.23461857, 0.732274  , 0.2127717 ],
        [0.6739347 , 0.34742635, 0.41046205, 0.26215446],
        [0.577827  , 0.32734275, 0.62989986, 0.22067626],
        [0.37011942, 0.15006503, 0.65958476, 0.18708763]],
## barren
       [[0.29481938, 0.09472984, 0.59135556, 0.06860657],
        [0.86539465, 0.7506361 , 0.37203112, 0.11493613],
        [0.664666  , 0.6056427 , 0.46542227, 0.14238815],
        [0.6938545 , 0.43799615, 0.30913985, 0.2867542 ],
        [0.8466273 , 0.53237015, 0.44636855, 0.16200702]],
## sandsea
       [[0.82119286, 0.48783484, 0.44511366, 0.10902377],
        [0.9354581 , 0.8444746 , 0.28542006, 0.076657  ],
        [0.75143087, 0.70467633, 0.602095  , 0.09906711],
        [0.8729486 , 0.81519806, 0.4026484 , 0.0783796 ],
        [0.24349129, 0.7866096 , 0.45044297, 0.11177942]]
])

def classify_biome(
    mean_solar_flux_Wpm2: float,
    pressure_kPa: float,
    altitude_m: float,
    mean_temp_C: float,
    temp_var_C: float,
    annual_precip_mm: float
) -> int:
    """
This function estimates the biome code for a given set of climate parameters

Parameters:
    mean_solar_flux_Wpm2 (float) - annual mean solar flux, in watts per square meter
    pressure_kPa (float) - atmospheric pressure at the surface (use sea-level pressure for underwater classification),
                           in kPa
    altitude_m (float) - altitude above (or below, if negative) sea-level, in meters
    mean_temp_C (float) - annual mean temperature, in degrees C
    temp_var_C (float) - the +/- range of the temperature throughout the year (1.5 standard deviations), in degrees C
    annual_precip_mm (float) - the annual mean precipitation, in mm rainfall (10 mm snowfall = 1 mm rainfall)

Returns:
    (int) returns the DrPlantabyte Biome enum value for the predicted biome
    """
    ## constants and variables
    min_rain_limit_mm = 110
    max_rain_limit_mm = 6000 # too much rain and we'll call it a wetland instead of a jungle
    photic_zone_min_solar_flux_Wpm2 = 35
    wave_disruption_depth_m = -6 # corals, seagrasses, kelps, etc cannot grow above this depth
    epsilon_water = 0.013333  # Absorption per meter (150m == 1% transmission (0.01 = 10^(-epsilon*150))
    benthic_solar_flux = mean_solar_flux_Wpm2 * pow(10, epsilon_water*altitude_m) # <- note: altitude is negative here
    boiling_point_C = boiling_point(pressure_kPa)
    ## terrestrial biomes
    closest_dist = 1e35 #
    d = 0
    biome_code = Biome.UNKNOWN
    if altitude_m > 0:
        if annual_precip_mm > max_rain_limit_mm:
            biome_code = Biome.WETLAND
        else:
            ### rescale to normalize so that distance calcs aren't biased
            norm_sol_flux = rescale(mean_solar_flux_Wpm2, 0.0, 800.)
            norm_mtemp = rescale(mean_temp_C, -20., 50.)
            norm_vtemp = rescale(temp_var_C, 0., 35.)
            norm_precip = rescale(numpy.sqrt(annual_precip_mm), 0.0, 75.)
            for bclass in range(9):
                for refpt in range(5):
                    d = dist4f(
                        ref_points[bclass][refpt][0], ref_points[bclass][refpt][1], ref_points[bclass][refpt][2], ref_points[bclass][refpt][3],
                        norm_sol_flux, norm_mtemp, norm_vtemp, norm_precip
                    )
                    if d < closest_dist:
                        closest_dist = d
                        biome_code = ref_classes[bclass]
        if biome_code == Biome.JUNGLE and temp_var_C > 6.0:
            # too much variation for jungle, actually grassland
            biome_code = Biome.GRASSLAND
    ## marine biomes
    else:
        if benthic_solar_flux >= photic_zone_min_solar_flux_Wpm2:
            # sea floor in photic zone
            if mean_temp_C > 5 and mean_temp_C < 20 and altitude_m < wave_disruption_depth_m:
                biome_code = Biome.SEA_FOREST
            elif mean_temp_C >= 20 and mean_temp_C < 30 and altitude_m < wave_disruption_depth_m:
                biome_code = Biome.TROPICAL_REEF
            else:
                biome_code = Biome.ROCKY_SHALLOWS
        elif altitude_m > -200:
            biome_code = Biome.SHALLOW_OCEAN
        else:
            biome_code = Biome.DEEP_OCEAN
    ## extreme biomes
    if altitude_m > 0:
        if annual_precip_mm < min_rain_limit_mm:
            if mean_temp_C > 15:
                biome_code = Biome.SAND_SEA
            elif mean_temp_C <= 15:
                biome_code = Biome.BARREN
        if mean_temp_C >= boiling_point_C:
            biome_code = Biome.MOONSCAPE
    else:
        if mean_temp_C > boiling_point_C:
            biome_code = Biome.BOILING_SEA
    if (mean_temp_C < boiling_point_C) and (mean_temp_C + temp_var_C) < 0:
        biome_code = Biome.ICE_SHEET
    ## Done!
    return biome_code

def classify_biome_on_planet(
    planet_mass_kg: float,
    planet_mean_radius_km: float,
    toa_solar_flux_Wpm2: float,
    axis_tilt_deg: float,
    tidal_lock: bool,
    mean_surface_pressure_kPa: float,
    altitude_m: float,
    mean_temp_C: float,
    temp_var_C: float,
    annual_precip_mm: float,
    latitude: float,
    longitude: float,
    exoplanet: bool,
) -> int:
    """
This function estimates the biome code for a given set of planetary and climate parameters, with input parameters that
are more convenient for exoplanet simulations

Parameters:
    planet_mass_kg (float) - mass of the planet, in kg
    planet_mean_radius_km (float) - radius of the planet, in km
    toa_solar_flux_Wpm2 (float) - top-of-atmosphere solar flux from the planet's star, in watts per square meter
    axis_tilt_deg (float) - tilt of the planetary rotation axis, in degrees (ignored for tidally locked planets)
    tidal_lock (bool) - true for a tidally-locked plant (same side always faces the host star), false for a planet with
                        a day-night cycle (even if one day is significantly different from Earth)
    mean_surface_pressure_kPa (float) - atmospheric pressure at sea-level, in kPa
    altitude_m (float) - altitude above (or below, if negative) sea-level, in meters
    mean_temp_C (float) - annual mean temperature, in degrees C
    temp_var_C (float) - the +/- range of the temperature throughout the year (1.5 standard deviations), in degrees C
    annual_precip_mm (float) - the annual mean precipitation, in mm rainfall (10 mm snowfall = 1 mm rainfall)
    latitude (float) - the latitude coordinate of the location for biome estimation, in degrees north (negative for
                       south)
    longitude (float) - the longitude coordinate of the location for biome estimation, in degrees east (negative for
                        west)
    exoplanet (bool) - set to true to include more exotic biomes not found on Earth, set to false to only use Earthly
                       biomes

Returns:
    (int) returns the DrPlantabyte Biome code for the predicted biome, or 0 if no biome prediction could be made
    """
    pi = 3.14159265358979
    two_over_pi = 0.5 * pi
    deg2Rad = pi / 180
    #
    G = 6.67430e-11 # N m2 / kg2
    radius_m = (planet_mean_radius_km * 1000) + altitude_m
    gravity_m_per_s2 = G * planet_mass_kg / (radius_m * radius_m)
    above_sealevel_m = altitude_m
    if above_sealevel_m < 0:
        above_sealevel_m = 0
    pressure_kPa = pressure_at_altitude(gravity_m_per_s2, mean_surface_pressure_kPa, mean_temp_C, above_sealevel_m)
    epsilon_air = 3.46391e-5 # Absorption per kPa (1360 = 1371 * 10^(-eps * 101) )
    max_flux = toa_solar_flux_Wpm2 * pow(10, -epsilon_air * pressure_kPa)
    mean_solar_flux_Wpm2 = 0
    if tidal_lock:
        mean_solar_flux_Wpm2 = max_flux * two_over_pi * numpy.cos(latitude) * clip(numpy.cos(longitude), 0, 1)
    else:
        mean_solar_flux_Wpm2 = max_flux * two_over_pi * 0.5 * (
                clip(numpy.cos(deg2Rad * (latitude - axis_tilt_deg)), 0, 1)
                + clip(numpy.cos(deg2Rad * (latitude + axis_tilt_deg)), 0, 1)
        )
    ## if doing expoplanet calcualtion, first check astronomical biomes
    min_neutron_star_density_Tpm3 = 1e14# tons per cubic meter (aka g/cc)
    max_neutron_star_density_Tpm3 = 2e16 # tons per cubic meter (aka g/cc)
    planet_volume_m3 = 4.0/3.0*pi*radius_m*radius_m*radius_m
    planet_density_Tpm3 = planet_mass_kg / 1000. / planet_volume_m3
    red_dwarf_min_mass_kg = 1.2819e29
    if exoplanet: ## try to detect extreme conditions of a non-goldilocks-zone planet
        if planet_density_Tpm3 > max_neutron_star_density_Tpm3:
            ## BLACK HOLE!
            return Biome.EVENT_HORIZON
        if planet_density_Tpm3 >= min_neutron_star_density_Tpm3:
            ## neutron star!
            return Biome.NEUTRON_STAR
        if planet_mass_kg >= red_dwarf_min_mass_kg:
            ## big enough to spontaneously start thermonuclear fusion and become a star
            return Biome.STAR
    return classify_biome_on_planet_surface(
        gravity_m_per_s2,
        mean_surface_pressure_kPa,
        mean_solar_flux_Wpm2,
        altitude_m,
        mean_temp_C,
        temp_var_C,
        annual_precip_mm,
        exoplanet
    )


def classify_biome_on_planet_surface(
    gravity_m_per_s2: float,
    mean_surface_pressure_kPa: float,
    mean_solar_flux_Wpm2: float,
    altitude_m: float,
    mean_temp_C: float,
    temp_var_C: float,
    annual_precip_mm: float,
    exoplanet: bool
) -> int:
    """
This function estimates the biome code for a given set of climate parameters, with the option to include extreme
exoplanet biomes that do not exist on Earth

Parameters:
    gravity_m_per_s2 (float) - gravity at the surface of the planet, in meters per second per second
    mean_surface_pressure_kPa (float) - atmospheric pressure at sea-level, in kPa
    mean_solar_flux_Wpm2 (float) - annual mean solar flux, in watts per square meter
    altitude_m (float) - altitude above reference altitude (eg sea-level), in meters
    mean_temp_C (float) - annual mean temperature, in degrees C
    temp_var_C (float) - the +/- range of the temperature throughout the year (1.5 standard deviations), in degrees C
    annual_precip_mm (float) - the annual mean precipitation, in mm rainfall (10 mm snowfall = 1 mm rainfall)
    exoplanet (bool) - set to true to include more exotic biomes not found on Earth, set to false to only use Earthly
                       biomes

Returns:
    (int) returns the DrPlantabyte Biome code for the predicted biome, or 0 if no biome prediction could be made
    """
    if numpy.isnan(gravity_m_per_s2 + mean_surface_pressure_kPa + mean_solar_flux_Wpm2 + altitude_m + mean_temp_C + temp_var_C + annual_precip_mm):
        return Biome.UNKNOWN
    water_supercritical_pressure = 22000 # kPa
    pyroxene_melting_point_C = 1000
    quartz_boiling_boint_C = 2230
    ### cryogen params based on liquid nitrogen ( https://www.engineeringtoolbox.com/nitrogen-d_1421.html )
    #### alternative cryogens: ammonia, methane; both would oxidize in presense of oxygen, so not as interesting
    #### (oxygen is a pretty common element)
    cryo_crit_temp = -147 # C
    cryo_crit_pressure = 3400 # kPa
    cryo_triple_temp = -210 # C
    goldilocks_min_atmosphere = 4.0 # kPa, water must be liquid up to 30 C for earth-like geography
    goldilocks_max_atmosphere = 3350 # kPa, no super-critical gasses allowed for earth-like geography
    # cryo_triple_pressure = 12.5 # kPa
    vapor_pressure_kPa = 0.61094 * numpy.exp((17.625 * (mean_temp_C + temp_var_C)) / ((mean_temp_C + temp_var_C) + 243.04)) # Magnus formula
    above_sealevel_m = altitude_m
    if above_sealevel_m < 0:
        above_sealevel_m = 0
    pressure_kPa = pressure_at_altitude(gravity_m_per_s2, mean_surface_pressure_kPa, mean_temp_C, above_sealevel_m)
    boiling_point_C = boiling_point(pressure_kPa)
    if exoplanet: ## try to detect extreme conditions of a non-goldilocks-zone planet
        if mean_temp_C > quartz_boiling_boint_C:
            ## at least as hot as a red dwarf XD
            return Biome.STAR
        if pressure_kPa > water_supercritical_pressure:
            ### defining a gas giant is a bit hand-wavey as of 2022
            return Biome.GAS_GIANT
        if mean_temp_C > pyroxene_melting_point_C:
            if altitude_m <= 0:
                return Biome.MAGMA_SEA
            else:
                return Biome.MOONSCAPE
        if pressure_kPa < vapor_pressure_kPa or (mean_temp_C - temp_var_C) > boiling_point_C:
            ### not enough atmosphere to be anything other than a naked rock!
            return Biome.MOONSCAPE
        if (mean_temp_C > cryo_triple_temp) and (mean_temp_C < cryo_crit_temp) and \
                (pressure_kPa < cryo_crit_pressure) and ( pressure_kPa > (1.6298e9*numpy.exp(0.08898*mean_temp_C))):
            ## liquid nitrogen planet! (like pluto)
            if altitude_m <= 0:
                return Biome.CRYOGEN_SEA
            elif annual_precip_mm > 0:
                return Biome.ICE_SHEET
            else:
                return Biome.MOONSCAPE
        if mean_surface_pressure_kPa < goldilocks_min_atmosphere or mean_surface_pressure_kPa > goldilocks_max_atmosphere:
            return Biome.MOONSCAPE
    ## then check normal biomes
    return classify_biome(
        mean_solar_flux_Wpm2,
        pressure_kPa,
        altitude_m,
        mean_temp_C,
        temp_var_C,
        annual_precip_mm
    )


def boiling_point(pressure_kPa: float) -> float:
    ln_mbar = numpy.log(pressure_kPa*10)
    x = ln_mbar
    x2 = x*ln_mbar
    x3 = x2*ln_mbar
    lp = 0.051769*x3 + 0.65545*x2 + 10.387*x - 10.619
    hp = 0.47092*x3 - 8.2481*x2 + 75.520*x - 183.98
    if pressure_kPa < 101.3:
        return lp
    else:
        return hp

def pressure_at_altitude(gravity_m_per_s2: float, mean_surface_pressure_kPa: float, mean_temp_C: float, above_sealevel_m: float) -> float:
    K = mean_temp_C + 273.15
    R = 8.314510  # j/K/mole
    air_molar_mass = 0.02897  # kg/mol
    pressure_kPa = mean_surface_pressure_kPa * numpy.exp(-(air_molar_mass * gravity_m_per_s2 * above_sealevel_m)/(R*K))
    return pressure_kPa

def clip(x: float, xmin: float, xmax: float) -> float:
    if x < xmin:
        return xmin
    if x > xmax:
        return xmax
    return x

def rescale(x: float, xmin: float, xmax: float) -> float:
    return (x - xmin) / (xmax - xmin)

def dist4f(a1: float, b1: float, c1: float, d1: float, a2: float, b2: float, c2: float, d2: float) -> float:
    da = a2-a1
    db = b2-b1
    dc = c2-c1
    dd = d2-d1
    return numpy.sqrt(da*da + db*db + dc*dc + dd*dd)

def classify_planet_biomes(
    gravity_m_per_s2: float,
    mean_surface_pressure_kPa: float,
    mean_solar_flux_Wpm2: ndarray,
    altitude_m: ndarray,
    mean_temp_C: ndarray,
    temp_var_C: ndarray,
    annual_precip_mm: ndarray,
    exoplanet: bool
) -> ndarray:
    """
This function estimates the biome codes for an array of planet and climate parameters, with the option to include
extreme exoplanet biomes that do not exist on Earth

Note that all ndarray parameters must have identical shapes

Parameters:
    gravity_m_per_s2 (float) - gravity at the surface of the planet, in meters per second per second
    mean_surface_pressure_kPa (float) - atmospheric pressure at sea-level, in kPa
    mean_solar_flux_Wpm2 (numpy.ndarray) - annual mean solar flux, in watts per square meter
    altitude_m (numpy.ndarray) - altitude above (or below, if negative) sea-level, in meters
    mean_temp_C (numpy.ndarray) - annual mean temperature, in degrees C
    temp_var_C (numpy.ndarray) - the +/- range of the temperature throughout the year (1.5 standard deviations), in
                                 degrees C
    annual_precip_mm (numpy.ndarray) - the annual mean precipitation, in mm rainfall (10 mm snowfall = 1 mm rainfall)
    exoplanet (bool) - set to true to include more exotic biomes not found on Earth, set to false to only use Earthly
                       biomes

Returns:
    (numpy.ndarray with dtype=uint8) returns the DrPlantabyte Biome codes for the predicted biomes

Biome Code Reference:
    Code   Biome
       0   UNKNOWN
       1   WETLAND
       2   JUNGLE
       3   SEASONAL_FOREST
       4   NEEDLELEAF_FOREST
       5   GRASSLAND
       6   DESERT_SHRUBLAND
       7   TUNDRA
       8   BARREN
       9   SAND_SEA
   10-15   -- (reserved for future use)
      16   DEEP_OCEAN
      17   FRESHWATER
      18   SEA_FOREST
      19   TROPICAL_REEF
      20   ROCKY_SHALLOWS
      21   SHALLOW_OCEAN
      22   ICE_SHEET
      23   BOILING_SEA
   24-31   -- (reserved for future use)
      32   FARMLAND
      33   URBAN
      34   RUINS
   35-63   -- (reserved for future use)
      64   MOONSCAPE
      65   MAGMA_SEA
      66   CRYOGEN_SEA
      67   GAS_GIANT
      68   STAR
      69   NEUTRON_STAR
      70   EVENT_HORIZON
  71-111   -- (not used)
     112   BIOLUMINESCENT
     113   DEAD
     114   MAGIC_GARDEN
     115   ELEMENTAL_CHAOS
     116   OOZE
    """
    # for use with Numpy arrays
    assert tuple(mean_solar_flux_Wpm2.shape) == tuple(altitude_m.shape)
    assert tuple(mean_temp_C.shape) == tuple(altitude_m.shape)
    assert tuple(temp_var_C.shape) == tuple(altitude_m.shape)
    assert tuple(annual_precip_mm.shape) == tuple(altitude_m.shape)
    #
    result_view = numpy.zeros_like(mean_temp_C, dtype=numpy.uint8).reshape((-1,))
    #
    for i in range(result_view.shape[0]):
        result_view[i] = classify_biome_on_planet_surface(
            gravity_m_per_s2,
            mean_surface_pressure_kPa,
            mean_solar_flux_Wpm2[i],
            altitude_m[i],
            mean_temp_C[i],
            temp_var_C[i],
            annual_precip_mm[i],
            exoplanet
        )
    result = result_view.reshape(mean_temp_C.shape)
    return result

