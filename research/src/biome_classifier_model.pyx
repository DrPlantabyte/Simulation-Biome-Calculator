import cython
from biome_enum import Biome

def classify_biome(
    float toa_solar_flux_Wpm2,
    float axis_tilt_deg,
    bint tidal_lock,
    float mean_surface_pressure_kPa,
    float altitude_m,
    float mean_temp_C,
    float temp_var_C,
    float annual_precip_mm
):
    return Biome.UNKOWN.value