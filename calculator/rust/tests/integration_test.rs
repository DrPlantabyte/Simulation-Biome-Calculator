
use std::io;
use std::io::prelude::*;
use std::fs::File;
use flate2::read::GzDecoder;
use std::collections::HashMap;
use std::str::{FromStr, Split};
use biomecalculator::*;
use biomecalculator::classifier::classify_biome;

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
	for row in rows {
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
			let exoplanet = bool::from_str(cells[index_exoplanet]).unwrap();
			let biome = Biome::from(u8::from_str(cells[index_biome]).unwrap());
			//
			let calculated_biome = classify_biome(mean_solar_flux_Wpm2, mean_surface_pressure_kPa, altitude_m, mean_temp_C, temp_var_C, annual_precip_mm);
			assert_eq!(biome, calculated_biome);
		}
	}
}

fn index_of(target: &str, array: &Vec<&str>) -> Option<usize>{
	return array.iter().position(|x| *x == target);
}

#[test]
fn classify_biomes_on_planet() {
	todo!()
}

#[test]
fn raster_conversion(){
	todo!()
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

