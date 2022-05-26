use std::str::Split;
use biomecalculator::*;

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
#[test]
fn classify_biomes_with_earth_ref() {
	use std::io;
	use std::io::prelude::*;
	use std::fs::File;
	use flate2::read::GzDecoder;
	use std::collections::HashMap;
	let filepath = "../java/net.plantabyte.biomes.test/resources/Earth_ref_table.csv.gz";
	let f = File::open(filepath).unwrap();
	let mut gz = GzDecoder::new(f);
	let mut csv = String::new();
	gz.read_to_string(&mut csv).unwrap();
	//csv.truncate(500);
	//println!("\n\n\n{}\n\n\n", csv);
	/*
tope 4 rows of CSV are:
,gravity_m_per_s2,mean_surface_pressure_kPa,toa_solar_flux_Wpm2,mean_solar_flux_Wpm2,altitude_m,mean_temp_C,temp_var_C,annual_precip_mm,exoplanet,biome
149920,9.81,101.3,1373,245.55655,-541.4,-0.761,1.6997077,251.82013,True,16
149921,9.81,101.3,1373,245.55655,-512.4,-0.10599999,0.11879394,101.111755,True,16
149922,9.81,101.3,1373,245.55655,-494.4,-0.849,0.71959674,75.29513,True,22

	 */
	let mut header = true;
	let mut index_gravity_m_per_s2: isize = -1;
	let mut index_mean_surface_pressure_kPa: isize = -1;
	let mut index_toa_solar_flux_Wpm2: isize = -1;
	let mut index_mean_solar_flux_Wpm2: isize = -1;
	let mut index_altitude_m: isize = -1;
	let mut index_mean_temp_C: isize = -1;
	let mut index_annual_precip_mm: isize = -1;
	let mut index_exoplanet: isize = -1;
	let mut index_biome: isize = -1;
	for row in csv.split("\n"){
		let cells = row.split(",");
		if header {
			index_gravity_m_per_s2 = index_in_split()
			todo!();
		} else {
			todo!();
		}
	}
	todo!()
}

fn index_in_split(target: &str, split: Split<&str>) -> Option<usize>{
	for i in 0..split.count(){
		if split[i] == target{
			return Some(i);
		}
	}
	return None;
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

