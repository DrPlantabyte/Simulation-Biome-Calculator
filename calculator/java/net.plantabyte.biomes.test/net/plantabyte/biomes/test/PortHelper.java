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
use std::string::String;

#[allow(non_camel_case_types)]
#[derive(Debug, EnumIter, Clone)]
""");
		sb.append("pub enum Biome {\n");
		for(var b : Biome.values()){
			sb.append("\t").append(b.name()).append(",\n");
		}
		sb.append("}\n");

		sb.append("impl Biome {\n");
		sb.append("\tfn bcode(&self) -> u8 {\n\t\tmatch *self {\n");
		for(var b : Biome.values()){
			sb.append("\t\t\tBiome::").append(b.name()).append(" => ").append(b.getBiomeCode()).append(",\n");
		}
		sb.append("\t\t}\n\t}\n");
		sb.append("\tfn label(&self) -> &str {\n\t\tmatch *self {\n");
		for(var b : Biome.values()){
			sb.append("\t\t\tBiome::").append(b.name()).append(" => \"").append(b.name()).append("\",\n");
		}
		sb.append("\t\t}\n\t}\n");
		sb.append("\tfn common_name(&self) -> &str {\n\t\tmatch *self {\n");
		for(var b : Biome.values()){
			sb.append("\t\t\tBiome::").append(b.name()).append(" => \"").append(b.getCommonName()).append("\",\n");
		}
		sb.append("\t\t}\n\t}\n");
		sb.append("\tfn technical_name(&self) -> &str {\n\t\tmatch *self {\n");
		for(var b : Biome.values()){
			sb.append("\t\t\tBiome::").append(b.name()).append(" => \"").append(b.getTechnicalName()).append("\",\n");
		}
		sb.append("\t\t}\n\t}\n");

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
