package net.plantabyte.biomes.test;

import net.plantabyte.biomes.Biome;

public class PortHelper {
	public static void main(String[] args){
		printRustEnum();
	}

	private static void printRustEnum() {
		System.out.println("//===== RUST =====");
		var sb = new StringBuilder();
		sb.append("""
use strum::IntoEnumIterator;
use strum_macros::EnumIter;
use std::fmt::{Display, Result, Formatter};

#[allow(non_camel_case_types)]
#[derive(Debug, EnumIter, Clone)]
""");
		sb.append("pub enum Biome {\n");
		for(var b : Biome.values()){
			sb.append("\t").append(b.name()).append(",\n");
		}
		sb.append("}\n");

		sb.append("""
struct BiomeEnumData {
	biome_code: u8,
	enum_name: &'static str,
	common_name: &'static str,
	technical_name: &'static str
}
""");
		sb.append("impl BiomeEnumData {\n");
		for(var b : Biome.values()){
			sb.append("\tconst ").append(b.name())
					.append(": Self = Self{biome_code: ").append(b.getBiomeCode())
					.append(", enum_name: &\"").append(b.name())
					.append("\", common_name: &\"").append(b.getCommonName())
					.append("\", technical_name: &\"").append(b.getTechnicalName())
					.append("\"};\n");
		}
		sb.append("}\n");

		sb.append("fn get_data(biome: &Biome) -> &'static BiomeEnumData {\n");
		sb.append("\tmatch *biome {\n");
		for(var b : Biome.values()){
			sb.append("\t\tBiome::").append(b.name()).append(" => &BiomeEnumData::").append(b.name()).append(",\n");
		}
		sb.append("\t}\n}\n");

		sb.append("impl Biome {\n");
		sb.append("""
	pub fn bcode(&self) -> u8 {
		get_data(self).biome_code
	}
""");
		sb.append("""
	pub fn label(&self) -> &'static str {
		get_data(self).enum_name
	}
""");
		sb.append("""
	pub fn common_name(&self) -> &'static str {
		get_data(self).common_name
	}
""");
		sb.append("""
	pub fn technical_name(&self) -> &'static str {
		get_data(self).technical_name
	}
""");

		sb.append("}\n");

		sb.append("impl From<u8> for Biome {\n\tfn from(bcode: u8) -> Biome {\n\t\tmatch bcode {\n");
		for(var b : Biome.values()){
			sb.append("\t\t\t").append(b.getBiomeCode()).append(" => Biome::").append(b.name()).append(",\n");
		}
		sb.append("\t\t\t_ => Biome::").append(Biome.UNKNOWN.name()).append(",\n");
		sb.append("\t\t}\n\t}\n}\n");

		for(var base : "16,32,64".split(",")){
			for(var sign : "u,i".split(",")) {
				var T = sign+base;
				var fn_txt = """
impl From<TTT> for Biome {
	fn from(bcode: TTT) -> Biome {
		if bcode > 0 && bcode < 256 {
			Biome::from(bcode as u8)
		} else {
			Biome::UNKNOWN
		}
	}
}
""".replace("TTT", T);
				if(sign.equals("u")){
					fn_txt = fn_txt.replace("bcode > 0 && ", "");
				}
				sb.append(fn_txt);
			}
		}

		sb.append("""
impl From<&Biome> for u8 {
	fn from(b: &Biome) -> u8 {
		b.bcode()
	}
}
impl From<Biome> for u8 {
	fn from(b: Biome) -> u8 {
		b.bcode()
	}
}
""");

		sb.append("""
impl Display for Biome {
	fn fmt(&self, f: &mut Formatter<'_>) -> Result {
		f.write_str(self.label().as_ref())
	}
}
""");

		System.out.println(sb.toString());
	}
}
