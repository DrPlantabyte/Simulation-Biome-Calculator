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
	todo!()
}

#[test]
fn classify_biomes_with_earth_ref() {
	todo!()
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

