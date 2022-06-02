
use std::io;
use std::io::prelude::*;
use std::fs::File;
use flate2::read::GzDecoder;
use std::collections::HashMap;
use std::str::{FromStr, Split};
use biomecalculator::*;
use biomecalculator::classifier::{classify_biome, Planet, classify_biome_on_planet, classify_biome_on_planet_surface};

#[test]
fn api_test1() {
	println!("Enum\tbcode\tCommon name\tTechnical name");
	for biome in Biome::values() {
		println!("{}\t{}\t{}\t{}", biome, biome.bcode(), biome.common_name(), biome.technical_name());
	}
}

#[test]
fn api_test2() {
	use biomecalculator::classifier::*;

	todo!()
}

#[allow(non_snake_case)]
#[allow(unused_variables)]
#[test]
fn classify_biomes_with_earth_ref() {
	let filepath = "../java/net.plantabyte.biomes.test/resources/Earth_ref_table.csv.gz";

	/*
tope 4 rows of CSV are:
,gravity_m_per_s2,mean_surface_pressure_kPa,toa_solar_flux_Wpm2,mean_solar_flux_Wpm2,altitude_m,mean_temp_C,temp_var_C,annual_precip_mm,exoplanet,biome
149920,9.81,101.3,1373,245.55655,-541.4,-0.761,1.6997077,251.82013,True,16
149921,9.81,101.3,1373,245.55655,-512.4,-0.10599999,0.11879394,101.111755,True,16
149922,9.81,101.3,1373,245.55655,-494.4,-0.849,0.71959674,75.29513,True,22

	 */
	let mut header = true;
	let mut index_gravity_m_per_s2: usize = 0;
	let mut index_mean_surface_pressure_kPa: usize = 0;
	let mut index_toa_solar_flux_Wpm2: usize = 0;
	let mut index_mean_solar_flux_Wpm2: usize = 0;
	let mut index_altitude_m: usize = 0;
	let mut index_mean_temp_C: usize = 0;
	let mut index_temp_var_C: usize = 0;
	let mut index_annual_precip_mm: usize = 0;
	let mut index_exoplanet: usize = 0;
	let mut index_biome: usize = 0;
	let f = File::open(filepath).unwrap();
	let mut gz = GzDecoder::new(f);
	let mut csv = String::new();
	gz.read_to_string(&mut csv).unwrap();
	let rows = csv.split("\n").collect::<Vec<&str>>(); // .split method returns an iterator, not an array!
	let mut row_number = 0;
	for row in rows {
		if row.trim().len() == 0{
			continue;
		}
		row_number += 1;
		if row_number < 10 {
			println!("#{}\t{}", row_number, row);
		}
		let cells = row.split(",").collect::<Vec<&str>>();
		if header {
			index_gravity_m_per_s2 = index_of("gravity_m_per_s2", &cells).unwrap();
			index_mean_surface_pressure_kPa = index_of("mean_surface_pressure_kPa", &cells).unwrap();
			index_toa_solar_flux_Wpm2 = index_of("toa_solar_flux_Wpm2", &cells).unwrap();
			index_mean_solar_flux_Wpm2 = index_of("mean_solar_flux_Wpm2", &cells).unwrap();
			index_altitude_m = index_of("altitude_m", &cells).unwrap();
			index_mean_temp_C = index_of("mean_temp_C", &cells).unwrap();
			index_temp_var_C = index_of("temp_var_C", &cells).unwrap();
			index_annual_precip_mm = index_of("annual_precip_mm", &cells).unwrap();
			index_exoplanet = index_of("exoplanet", &cells).unwrap();
			index_biome = index_of("biome", &cells).unwrap();
			header = false;
		} else {
			let gravity_m_per_s2 = f64::from_str(cells[index_gravity_m_per_s2]).unwrap();
			let mean_surface_pressure_kPa = f64::from_str(cells[index_mean_surface_pressure_kPa]).unwrap();
			let toa_solar_flux_Wpm2 = f64::from_str(cells[index_toa_solar_flux_Wpm2]).unwrap();
			let mean_solar_flux_Wpm2 = f64::from_str(cells[index_mean_solar_flux_Wpm2]).unwrap();
			let altitude_m = f64::from_str(cells[index_altitude_m]).unwrap();
			let mean_temp_C = f64::from_str(cells[index_mean_temp_C]).unwrap();
			let temp_var_C = f64::from_str(cells[index_temp_var_C]).unwrap();
			let annual_precip_mm = f64::from_str(cells[index_annual_precip_mm]).unwrap();
			let exoplanet = bool::from_str(cells[index_exoplanet].trim().to_lowercase().as_str())
				.unwrap();
			let biome = Biome::from(u8::from_str(cells[index_biome].trim()).unwrap());
			//
			let calculated_biome = classify_biome(mean_solar_flux_Wpm2, mean_surface_pressure_kPa, altitude_m, mean_temp_C, temp_var_C, annual_precip_mm);
			assert_eq!(biome, calculated_biome, "Failed to correctly predict biome {}, got {} \
			instead. Parameters: gravity_m_per_s2 = {}; mean_surface_pressure_kPa = {}; \
			toa_solar_flux_Wpm2 = {}; mean_solar_flux_Wpm2 = {}; altitude_m = {}; \
			 mean_temp_C = {}; temp_var_C = {}; annual_precip_mm = {}; exoplanet = {}; biome = {}",
			biome, calculated_biome, gravity_m_per_s2, mean_surface_pressure_kPa,
					   toa_solar_flux_Wpm2, mean_solar_flux_Wpm2, altitude_m, mean_temp_C,
					   temp_var_C, annual_precip_mm, exoplanet, biome);
		}
	}
}

fn index_of(target: &str, array: &Vec<&str>) -> Option<usize>{
	return array.iter().position(|x| x.trim() == target.trim());
}

#[allow(non_snake_case)]
#[allow(unused_variables)]
#[test]
fn classify_biomes_on_planet() {
	let filepath = "../java/net.plantabyte.biomes.test/resources/planet_refs.csv.gz";
	let mut header = true;
	let mut index_planet_mass_kg: usize = 0;
	let mut index_planet_mean_radius_km: usize = 0;
	let mut index_axis_tilt_deg: usize = 0;
	let mut index_tidal_lock: usize = 0;
	let mut index_mean_surface_pressure_kPa: usize = 0;
	let mut index_toa_solar_flux_Wpm2: usize = 0;
	let mut index_longitude: usize = 0;
	let mut index_latitude: usize = 0;
	let mut index_altitude_m: usize = 0;
	let mut index_mean_temp_C: usize = 0;
	let mut index_temp_var_C: usize = 0;
	let mut index_annual_precip_mm: usize = 0;
	let mut index_exoplanet: usize = 0;
	let mut index_biome: usize = 0;
	let f = File::open(filepath).unwrap();
	let mut gz = GzDecoder::new(f);
	let mut csv = String::new();
	gz.read_to_string(&mut csv).unwrap();
	let rows = csv.split("\n").collect::<Vec<&str>>(); // .split method returns an iterator, not an array!
	let mut row_number = 0;
	for _row in rows {
		let row = _row.trim(); // trim off trailing \n or something
		if row.trim().len() == 0{
			continue;
		}
		row_number += 1;
		if row_number < 10 {
			println!("#{}\t{}", row_number, row);
		}
		let cells = row.split(",").collect::<Vec<&str>>();
		if header {
			index_mean_surface_pressure_kPa = index_of("mean_surface_pressure_kPa", &cells).unwrap();
			index_toa_solar_flux_Wpm2 = index_of("toa_solar_flux_Wpm2", &cells).unwrap();
			index_altitude_m = index_of("altitude_m", &cells).unwrap();
			index_mean_temp_C = index_of("mean_temp_C", &cells).unwrap();
			index_temp_var_C = index_of("temp_var_C", &cells).unwrap();
			index_annual_precip_mm = index_of("annual_precip_mm", &cells).unwrap();
			index_exoplanet = index_of("exoplanet", &cells).unwrap();
			index_biome = index_of("biome", &cells).unwrap();
			index_latitude = index_of("latitude", &cells).unwrap();
			index_longitude = index_of("longitude", &cells).unwrap();
			index_planet_mass_kg = index_of("planet_mass_kg", &cells).unwrap();
			index_planet_mean_radius_km = index_of("planet_mean_radius_km", &cells).unwrap();
			index_axis_tilt_deg = index_of("axis_tilt_deg", &cells).unwrap();
			index_tidal_lock = index_of("tidal_lock", &cells).unwrap();
			header = false;
		} else {
			let planet_mass_kg = f64::from_str(cells[index_planet_mass_kg]).unwrap();
			let planet_mean_radius_km = f64::from_str(cells[index_planet_mean_radius_km]).unwrap();
			let axis_tilt_deg = f64::from_str(cells[index_axis_tilt_deg]).unwrap();
			let latitude = f64::from_str(cells[index_latitude]).unwrap();
			let longitude = f64::from_str(cells[index_longitude]).unwrap();
			let mean_surface_pressure_kPa = f64::from_str(cells[index_mean_surface_pressure_kPa]).unwrap();
			let toa_solar_flux_Wpm2 = f64::from_str(cells[index_toa_solar_flux_Wpm2]).unwrap();
			let altitude_m = f64::from_str(cells[index_altitude_m]).unwrap();
			let mean_temp_C = f64::from_str(cells[index_mean_temp_C]).unwrap();
			let temp_var_C = f64::from_str(cells[index_temp_var_C]).unwrap();
			let annual_precip_mm = f64::from_str(cells[index_annual_precip_mm]).unwrap();
			let exoplanet = bool::from_str(cells[index_exoplanet].trim().to_lowercase().as_str())
				.unwrap();
			let tidal_lock = bool::from_str(cells[index_tidal_lock].trim().to_lowercase()
				.as_str()).unwrap();
			let biome = Biome::from(u8::from_str(cells[index_biome].trim()).unwrap());
			//
			let planet = Planet{mass_kg: planet_mass_kg, mean_radius_km:
			planet_mean_radius_km, toa_solar_flux_Wpm2: toa_solar_flux_Wpm2, axis_tilt_deg:
			axis_tilt_deg, tidal_lock: tidal_lock, mean_surface_pressure_kPa:
			mean_surface_pressure_kPa, exoplanet: exoplanet};
			let calculated_biome = classify_biome_on_planet(
				&planet, altitude_m, mean_temp_C, temp_var_C, annual_precip_mm, latitude, longitude
			);
			assert_eq!(biome, calculated_biome, "Failed to correctly predict biome {} on planet \
			{:?}, got {} instead. \
			Parameters: planet_mass_kg = {}; planet_mean_radius_km={}; axis_tilt_deg = {}; mean_surface_pressure_kPa = {}; \
			toa_solar_flux_Wpm2 = {}; latitude = {}; longitude = {}; altitude_m = {}; \
			 mean_temp_C = {}; temp_var_C = {}; annual_precip_mm = {}; exoplanet = {}; biome = {}",
					   biome, planet, calculated_biome, planet_mass_kg, planet_mean_radius_km, axis_tilt_deg,
					   mean_surface_pressure_kPa, toa_solar_flux_Wpm2, latitude, longitude, altitude_m, mean_temp_C,
					   temp_var_C, annual_precip_mm, exoplanet, biome);
		}
	}
}

#[test]
fn raster_conversion(){
	const W: usize = 80;
	const H: usize = 60;
	let planet = Planet::EARTH;
	let mut altitude_map = vec![[0f64; W]; H]; // map[y][x]
	let mut rainfall_map = vec![[0f64; W]; H];
	let mut temperature_map = vec![[0f64; W]; H];
	let mut biome_map = vec![[Biome::Unknown; W]; H];
	let temperature_range = 3.;
	let mean_solar_flux = 500.;
	for row in 0..H{
		let y = (H as i32/2 - row as i32) as f64 * 10.;
		for col in 0..W {
			let x = (col as i32 - W as i32/2) as f64 * 10.;
			let r = f64::sqrt(x*x + y*y);
			altitude_map[row][col] = -0.015 * r.powi(2) + 1000.;
			rainfall_map[row][col] = (2000. - 20.*x).max(0.);
			temperature_map[row][col] = 30. - 0.05 * f64::max(0., altitude_map[row][col]);
		}
	}
	for row in 0..H{
		for col in 0..W {
			biome_map[row][col] = classify_biome_on_planet_surface(
				&planet, mean_solar_flux, altitude_map[row][col],
				temperature_map[row][col], temperature_range, rainfall_map[row][col]);
			println!("mean_solar_flux={}, altitude_map[row][col]={},
				temperature_map[row][col]={}, temperature_range={}, rainfall_map[row][col]={}", mean_solar_flux, altitude_map[row][col],
					 temperature_map[row][col], temperature_range, rainfall_map[row][col]);
		}
	}
	let mut ascii_art: HashMap<&Biome, &str> = HashMap::new();
	ascii_art.insert(&Biome::ShallowOcean, "~");
	ascii_art.insert(&Biome::DeepOcean, "≈");
	ascii_art.insert(&Biome::SeaForest, "≉");
	ascii_art.insert(&Biome::TropicalReef, "≃");
	ascii_art.insert(&Biome::RockyShallows, "~");
	ascii_art.insert(&Biome::IceSheet, "*");
	ascii_art.insert(&Biome::Wetland, "-");
	ascii_art.insert(&Biome::Grassland, "\"");
	ascii_art.insert(&Biome::SeasonalForest, "T");
	ascii_art.insert(&Biome::NeedleleafForest, "^");
	ascii_art.insert(&Biome::Jungle, "%");
	ascii_art.insert(&Biome::Tundra, "*");
	ascii_art.insert(&Biome::DesertShrubland, ".");
	ascii_art.insert(&Biome::Barren, "_");
	ascii_art.insert(&Biome::SandSea, "S");
	let test:Biome = Biome::Barren;
	println!("{}",ascii_art.get(&test).unwrap());

	for row in 0..H {
		for col in 0..W {
			print!("{}", ascii_art.get(&biome_map[row][col]).unwrap_or(&"?"));
		}
		println!();
	}
}

#[test]
fn conversion_coverage(){
	use std::vec::Vec;
	let mut biomes: Vec<Biome> = Vec::new();
	let mut bcodes: Vec<u8> = Vec::new();
	for biome in Biome::values() {
		biomes.push(*biome);
		bcodes.push(biome.bcode());
	}
	for i in 0..biomes.len(){
		assert_eq!(biomes[i], Biome::from(bcodes[i]));
	}
}

