#![allow(unused_imports)]
use std::io;
use std::io::prelude::*;
use std::fs::File;
use flate2::read::GzDecoder;
use std::collections::HashMap;
use std::str::{FromStr};
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
	println!();
	use biomecalculator::classifier::*;
	let ascii2data = |ascii: &[&str], m: f64, b: f64| {
		let mut rows: Vec<Vec<f64>> = Vec::with_capacity(ascii.len());
		for row_ascii in ascii{
			let mut row: Vec<f64> = Vec::with_capacity(row_ascii.len());
			for i in 0..row_ascii.len(){
				row.push(f64::from_str(&row_ascii[i..i+1]).unwrap_or(0f64) * m + b);
			}
			rows.push(row);
		}
		rows
	};
	let w = 36; let h = 18;
	let land_alt_map = ascii2data(
&["000000000000000000000000000000000000",
  "000000001200103400000000000110000000",
  "014775221010020000011111111543357331",
  "000009842123000000111112114879650000",
  "000000993220000000123031299999400000",
  "000000892200000001000289999993000000",
  "000000070000000003663262029991000000",
  "000000001000000003436630000010000000",
  "000000000112000000055900000000000000",
  "000000000061111000017900000000000000",
  "000000000009361000029400000000010000",
  "000000000009310000009000000000422000",
  "000000000005100000000000000000001000",
  "000000000001000000000000000000000000",
  "000000000000000000000000000000000000",
  "000000000000000000000000000000000000",
  "000000000001000000245643343400000110",
  "121111111111111111111533353211111111"], 100., 0.);
	let sea_depth_map = ascii2data(
&["999999999999999999999999999999999999",
  "999996010016000089981221110002640025",
  "000000000002909799900000000000000000",
  "999990000000999990000000000000003399",
  "999998000006999997000300000000089999",
  "999999000099999990299000000000099999",
  "999999909999999990000000600000999999",
  "999999990999999980000009939909999999",
  "999999999000699999900029999906999999",
  "999999999900000999900099999994958999",
  "999999999990000999900099999999207999",
  "999999999990009999960999999998000999",
  "999999999990099999999999999999990999",
  "999999999990999999999999999999999999",
  "999999999999999999999999999999999999",
  "999999999999999999999999999999999999",
  "888888888440699970000000000003115007",
  "000000000000000000000000000000000000"], -100., 0.);
	let temp_min_map = ascii2data(
&["000000000000000000000000000000000000",
  "440443222133100005504554443212343000",
  "432221111303413455543332211110000111",
  "554543332322455555554443322222124445",
  "555565444434556665555555544443334555",
  "666666655566666666666666654450566666",
  "777776777777777677777777076666777777",
  "777777777877777777788887777777777777",
  "777777777788877777777888777777777777",
  "777777777778887777777888777777777777",
  "777777777767777777777777777777777777",
  "777777766666667766666777777777677777",
  "666666666666666666666666666666666666",
  "555555555555555555555555555555555655",
  "555555555555550004444545545555555555",
  "000000444400000000000000000000000000",
  "000000000000000000000000000000000000",
  "000000000000000000000000000000000000"], 10., -50.);
	let temp_max_map = ascii2data(
&["444444444444444444444444444444444444",
  "554555555555544445545555565555555444",
  "667767766545555556667667777777776776",
  "666667887676666666677888888878776666",
  "666667998787766667888899999999876666",
  "777777998887777779988999988884777777",
  "777777888888777789999999498788888877",
  "777777788887777789999998888888887777",
  "788877777788877778888998888888888888",
  "688777777788888777788888888888888888",
  "677777777778898777789987777778898776",
  "677777777778877777789887777779999776",
  "677777777778777777778777777767778776",
  "666666666667666665566666666666666666",
  "455555555555554445555555555555555554",
  "444444555544444444444444444444444444",
  "444444444444444444444422442112222244",
  "444433222244444422222111111111224444"], 10., -50.);
	let precip_map = ascii2data(
&["111111111111111111111111111111111111",
  "111111111111111113311211121112222111",
  "220002000200000006004034455422223023",
  "346894223333466798643333333221232333",
  "667876224558999754453331121001346787",
  "656521127799863211133211130124799987",
  "333410146765421000000000136979965433",
  "443568997833222232211200369977999965",
  "999999999999879895777523799999789999",
  "994211000199953210277538999999699999",
  "997521000027742000024465686433455799",
  "779996421002986420001245432122111444",
  "666787765323799864214865433322222766",
  "665455555572578777656677766654444688",
  "666666666675444444444554554444566688",
  "188876761611111531111111111111111111",
  "111111111111111111111111111111111111",
  "000000000000000000000000000000000000"], 200., 0.);
	let tidally_locked_earth = Planet::EARTH.with_tidal_lock(true);
	let mut biome_map: Vec<Vec<Biome>> = vec![vec![Biome::Unknown; w]; h];
	for row in 0..h {
		let latitude = (h-row) as f64 * (180./h as f64) - 90.;
		for col in 0..w {
			let longitude = (col) as f64 * (360./w as f64) - 180.;
			let altitude = land_alt_map[row][col] + sea_depth_map[row][col];
			let mean_temperature = 0.5*(temp_max_map[row][col] + temp_min_map[row][col]);
			let temperature_range = temp_max_map[row][col] - temp_min_map[row][col];
			let precipitation = precip_map[row][col];
			biome_map[row][col] = classify_biome_on_planet(
				&tidally_locked_earth, altitude, mean_temperature,
				temperature_range, precipitation,
				latitude, longitude
			);
		}
	}
	for row in 0..h { for col in 0..w {
		print!("{}", biome_map[row][col].icon())
	} println!(); }
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


