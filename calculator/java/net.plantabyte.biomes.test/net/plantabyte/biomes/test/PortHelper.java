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
use std::fmt::{Display, Result, Formatter};

#[allow(non_camel_case_types)]
#[derive(Copy, Clone, Eq, PartialEq, Ord, PartialOrd, Hash, Debug)]
#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
""");
		sb.append("pub enum Biome {\n");
		for(var b : Biome.values()){
			String docStr = b.getTechnicalName();
			if(!b.getCommonName().equals(b.getTechnicalName())) docStr += ", aka "+b.getCommonName();
			sb.append(commentPrefix(docStr, "\t/// ")).append("\n");
			sb.append("\t").append(b.name()).append(",\n");
		}
		sb.append("}\n");

		sb.append("impl Biome {\n");
		String arrayType = String.format("[Self; %d]", Biome.values().length);
		sb.append("\tconst _VALUES: ").append(arrayType).append(" = [");
		for(var b : Biome.values()){ sb.append("Self::").append(b.name()).append(", ");}
		sb.append("];\n");sb.append("""
	pub fn values() -> &'static TTT{
		return &(Self::_VALUES);
	}
""".replace("TTT",arrayType));
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
			String docStr = "const data for enum Biome::"+b.name();
			sb.append(commentPrefix(docStr, "\t/// ")).append("\n");
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
_DOCSTR_
	fn from(bcode: TTT) -> Biome {
		if bcode > 0 && bcode < 256 {
			Biome::from(bcode as u8)
		} else {
			Biome::UNKNOWN
		}
	}
}
""".replace("TTT", T)
						.replace("_DOCSTR_", commentPrefix("Converts from Plantabyte biome code (as "+T+") to the corresponding Biome enum","\t/// "));
				if(sign.equals("u")){
					fn_txt = fn_txt.replace("bcode > 0 && ", "");
				}
				sb.append(fn_txt);
			}
		}

		sb.append("""
impl From<&Biome> for u8 {
	/// Converts from Plantabyte biome byte code to the corresponding Biome enum
	fn from(b: &Biome) -> u8 {
		b.bcode()
	}
}
impl From<Biome> for u8 {
	/// Converts from Biome enum to the corresponding Plantabyte biome byte code
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
	
	private static String commentPrefix(String text, String prefix){
		return prefix+text.stripTrailing()
				.replace("\r\n", "\n")
				.replace("\r", "")
				.replace("\n", "\n"+prefix);
	}
}
