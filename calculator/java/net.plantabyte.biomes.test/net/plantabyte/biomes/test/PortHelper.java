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
use variant_count::VariantCount;

#[derive(Copy, Clone, Eq, PartialEq, Ord, PartialOrd, Hash, Debug)]
#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
#[derive(VariantCount)] // NOTE: exposes Biome::VARIANT_COUNT to public API
""");
		sb.append("pub enum Biome {\n");
		for(var b : Biome.values()){
			String docStr = b.getTechnicalName();
			if(!b.getCommonName().equals(b.getTechnicalName())) docStr += ", aka "+b.getCommonName();
			sb.append(commentPrefix(docStr, "\t/// ")).append("\n");
			sb.append("\t").append(toUpperCamelCase(b.name())).append(",\n");
		}
		sb.append("}\n");

		sb.append("impl Biome {\n");
		String arrayType = String.format("[Self; %d]", Biome.values().length);
		sb.append("""
	/// This array is used as a work-around for the Rust compiler not supporting 
	/// enum iterators. For every enum variant added to Biome, an entry must be 
	/// added to this array (and a const struct added to BiomeEnumData). Unit 
	/// tests are used to check that there isn't a mismatch between this array, 
	/// the Biome enum, the BiomeEnumData struct, and related functions
""");
		sb.append("\tconst _VALUES: ").append(arrayType).append(" = [");
		for(var b : Biome.values()){ sb.append("Self::").append(toUpperCamelCase(b.name())).append(", ");}
		sb.append("];\n");sb.append("""
 	/// Returns a reference to a static array of all enum variants (useful for 
 	/// iteration over Biome enum types)
 	/// # Returns
 	/// Array or Biome enum variants
	pub fn values() -> &'static TTT{
		return &(Self::_VALUES);
	}
""".replace("TTT",arrayType));
		sb.append("}\n");


		sb.append("""
/// This stuct is is a workaround for Rust not having Java-style const value 
/// enums. For each data-less type in enum Biome, there is a corresponding 
/// const BiomeEnumData struct instance holding it's assiciated data. Then 
/// there is a private get_data(Biome) function using a match statement to link 
/// the two.
struct BiomeEnumData {
	biome_code: u8,
	enum_name: &'static str,
	common_name: &'static str,
	technical_name: &'static str
}
""");
		sb.append("impl BiomeEnumData {\n");
		for(var b : Biome.values()){
			String docStr = "const data for enum Biome::"+toUpperCamelCase(b.name());
			sb.append(commentPrefix(docStr, "\t/// ")).append("\n");
			sb.append("\tconst ").append(b.name())
					.append(": Self = Self{biome_code: ").append(b.getBiomeCode())
					.append(", enum_name: &\"").append(toUpperCamelCase(b.name()))
					.append("\", common_name: &\"").append(b.getCommonName())
					.append("\", technical_name: &\"").append(b.getTechnicalName())
					.append("\"};\n");
		}
		sb.append("}\n");

		sb.append("""
/// This is a work-around for the Rust compiler not supporting Java-style enums
/// of data constants. For a given reference to a Biome enum variant, it 
/// returns the corresponding const BiomeEnumData struct instance holding the 
/// const data for that enum variant.
/// # Parameters
/// * **biome: &Biome** - A reference to a Biome enum variant
/// # Returns
/// A static reference to a BiomeEnumData struct constant
""");
		sb.append("fn get_data(biome: &Biome) -> &'static BiomeEnumData {\n");
		sb.append("\tmatch *biome {\n");
		for(var b : Biome.values()){
			sb.append("\t\tBiome::").append(toUpperCamelCase(b.name())).append(" => &BiomeEnumData::").append(b.name()).append(",\n");
		}
		sb.append("\t}\n}\n");

		sb.append("impl Biome {\n");
		sb.append("""
 	/// Returns the Plantabyte Biome code for this Biome
	pub fn bcode(&self) -> u8 {
		get_data(self).biome_code
	}
""");
		sb.append("""
 	/// Returns the Plantabyte Biome code name for this Biome (intended for 
 	/// debugging). For user-facing apps, either use this as the key for i18n 
 	/// localization or use `.common_name()` or `.technical_name()` instead.
	pub fn name(&self) -> &'static str {
		get_data(self).enum_name
	}
""");
		sb.append("""
 	/// Returns the US English name this Biome for a non-scientist audience
	pub fn common_name(&self) -> &'static str {
		get_data(self).common_name
	}
""");
		sb.append("""
 	/// Returns the US English name this Biome for a scientist audience
	pub fn technical_name(&self) -> &'static str {
		get_data(self).technical_name
	}
""");

		sb.append("}\n");

		sb.append("""
	/// Converts from Plantabyte biome code (as u8) to the corresponding Biome enum
	/// # Parameters
	/// * **bcode: u8** - Plantabyte biome code
	/// # Returns
	/// Returns the corresponding Biome enum
""");
		sb.append("impl From<u8> for Biome {\n\tfn from(bcode: u8) -> Biome {\n\t\tmatch bcode {\n");
		for(var b : Biome.values()){
			sb.append("\t\t\t").append(b.getBiomeCode()).append(" => Biome::").append(toUpperCamelCase(b.name())).append(",\n");
		}
		sb.append("\t\t\t_ => Biome::").append(toUpperCamelCase(Biome.UNKNOWN.name())).append(",\n");
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
			Biome::Unknown
		}
	}
}
""".replace("TTT", T)
						.replace("_DOCSTR_", commentPrefix("Converts from Plantabyte biome code (as "+T+") to the corresponding Biome enum\n" +
								"# Parameters\n* **bcode: "+T+"** - Plantabyte biome code\n" +
								"# Returns\nReturns the corresponding Biome enum","\t/// "));
				if(sign.equals("u")){
					fn_txt = fn_txt.replace("bcode > 0 && ", "");
				}
				sb.append(fn_txt);
			}
		}

		sb.append("""
impl From<&Biome> for u8 {
	/// Converts from Plantabyte biome byte code to the corresponding Biome enum
	/// # Parameters
	/// * **bcode: u8** - Plantabyte biome code
	/// # Returns
	/// Returns the corresponding Biome enum
	fn from(b: &Biome) -> u8 {
		b.bcode()
	}
}
impl From<Biome> for u8 {
	/// Converts from Biome enum to the corresponding Plantabyte biome byte code
	/// # Parameters
	/// * **b: u8** - The Biome to convert
	/// # Returns
	/// Returns the Plantabyte biome code corresponding to the given Biome enum
	fn from(b: Biome) -> u8 {
		b.bcode()
	}
}
""");

		sb.append("""
				impl Display for Biome {
					/// Text representation of this Biome enum variant, for internal use. User-facing 
					/// apps should instead either use this as the key for i18n localization or use 
					/// `.common_name()` or `.technical_name()`.
					fn fmt(&self, f: &mut Formatter<'_>) -> Result {
						f.write_str(self.name().as_ref())
					}
				}
				""");

		sb.append("""
/// Unit tests
#[cfg(test)]
mod unit_tests {
	use crate::Biome;
	/// This unit test should guarantee that the following bits are all synchronized 
	/// relative to each other:
	/// * Biome enum
	/// * Biome::_VALUES
	/// * BiomeEnumData struct
	/// * impl From<u8> for Biome
	/// * impl From<Biome> for u8
	/// Due to Rust's lack of support for Java-style enumerations of constant data, 
	/// all of the above must be correctly modified every time a new Biome is added 
	#[test]
	fn consistency_check(){
		assert_eq!(Biome::VARIANT_COUNT, Biome::_VALUES.len(), "Assertion failure: Biome::VARIANT_COUNT != Biome::_VALUES.len()");
		assert_eq!(Biome::VARIANT_COUNT, Biome::values().len(), "Assertion failure: Biome::VARIANT_COUNT != Biome::values().len()");
		use std::collections::HashMap;
		let mut instance_counter: HashMap<Biome, usize> = HashMap::new();
		for biome in Biome::values() {
			*instance_counter.entry(*biome).or_insert(0) += 1;
			assert_eq!(instance_counter[biome], 1, "Assertion failure: duplicate of {} found in Biome::values()", biome.name());
			let bcode = biome.bcode();
			let biome2 = Biome::from(bcode);
			let bcode2 = u8::from(biome2);
			assert_eq!(*biome, biome2, "Assertion failure: round-trip from {} to {} to {} did not produce consistent Biome",\s
					biome, bcode, biome2);
			assert_eq!(bcode, bcode2, "Assertion failure: round-trip from {} to {} to {} to {} did not produce consistent bcode",\s
					biome, bcode, biome2, bcode2);
		}
		for bcode1 in 0..255 {
			let biome1 = Biome::from(bcode1);
			let bcode2 = u8::from(biome1);
			let biome2 = Biome::from(bcode2);
			let bcode3 = u8::from(biome2);
			if biome1 != Biome::Unknown {
				assert_eq!(bcode1, bcode2, "Assertion failure: round-trip from {} to {} to {} did not produce consistent bcode for known source bcode",\s
					bcode1, biome1, bcode2);
			}
			assert_eq!(biome1, biome2, "Assertion failure: round-trip from {} to {} to {} to {} did not produce consistent Biome enum",\s
					bcode1, biome1, bcode2, biome2);
			assert_eq!(bcode2, bcode3, "Assertion failure: round-trip from {} to {} to {} to {} to {} did not produce consistent bcode",\s
					bcode1, biome1, bcode2, biome2, bcode3);
		}

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

	private static String toUpperCamelCase(String text){
		var sb = new StringBuilder();
		for(int i = 0; i < text.length(); ++i){
			if(i == 0 || !Character.isLetterOrDigit(text.charAt(i-1))){
				sb.append(Character.toUpperCase(text.charAt(i)));
			} else if(Character.isLetterOrDigit(text.charAt(i))){
				sb.append(Character.toLowerCase(text.charAt(i)));
			}
		}
		return sb.toString();
	}
}
