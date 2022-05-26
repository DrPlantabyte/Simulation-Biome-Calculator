use std::fmt::{Display, Result, Formatter};
use variant_count::VariantCount;

#[derive(Copy, Clone, Eq, PartialEq, Ord, PartialOrd, Hash, Debug)]
#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
#[derive(VariantCount)] // NOTE: exposes Biome::VARIANT_COUNT to public API
pub enum Biome {
	/// Represents an absence of data or unsupported biome code
	Unknown,
	/// (Terrestrial Biome) Permanent wetland habitat
	Wetland,
	/// (Terrestrial Biome) Tropical rainforest
	Jungle,
	/// (Terrestrial Biome) Deciduous broadleaf forest
	SeasonalForest,
	/// (Terrestrial Biome) Borial, alpine, and taiga evergreen forests
	NeedleleafForest,
	/// (Terrestrial Biome) Grasslands, prairies, plains, and savannahs
	Grassland,
	/// (Terrestrial Biome) Deserts with sparse vegitation
	DesertShrubland,
	/// (Terrestrial Biome) Habitat that is too cold for forests to grow
	Tundra,
	/// (Aquatic Biome)  Lakes and rivers
	Freshwater,
	/// (Aquatic Biome) Kelp forests and seagrass meadows
	SeaForest,
	/// (Aquatic Biome) Coral reefs
	TropicalReef,
	/// (Aquatic Biome) Shallow marine habitat with sparse flora
	RockyShallows,
	/// (Aquatic Biome) Deep ocean (no light reaches the seafloor)
	DeepOcean,
	/// (Aquatic Biome) Shallow ocean (sunlight may reach the seafloor)
	ShallowOcean,
	/// (Extremophile Biome) Desert with virtually no vegetation
	Barren,
	/// (Extremophile Biome) Sand dunes with virtually no vegetation
	SandSea,
	/// (Extremophile Biome) Permanent ice
	IceSheet,
	/// (Extremophile Biome) Water body so hot that it boils
	BoilingSea,
	/// (Astronomical Biome) Completely inhospitable rock and dust (eg lunar regolith)
	Moonscape,
	/// (Astronomical Biome) Permanently molten lava
	MagmaSea,
	/// (Astronomical Biome) Bodies of liquid nitrogen or methane (or other cryogenic liquid)
	CryogenSea,
	/// (Astronomical Biome) "Surface" of a gas giant
	GasGiant,
	/// (Astronomical Biome) Surface of a star
	Star,
	/// (Astronomical Biome) Surface of a nuetron star
	NeutronStar,
	/// (Astronomical Biome) "Surface" of a black hole
	EventHorizon,
	/// (Artificial Biome) Agriculture land (eg crop fields and pastures)
	Farmland,
	/// (Artificial Biome) Cities and other artificial landscapes
	Urban,
	/// (Artificial Biome) Abandoned or destroyed urban areas
	Ruins,
	/// (Artificial Biome) Land too polluted to support terrestrial life
	PollutedWasteland,
	/// (Artificial Biome) Water too polluted to support aquatic life
	PollutedWastewater,
	/// (Fantasy Biome) Permanently dark habitat with glowing flora
	Bioluminescent,
	/// (Fantasy Biome) Dead (or undead) land
	Dead,
	/// (Fantasy Biome) Magical paradise
	MagicGarden,
	/// (Fantasy Biome) Elemental phenomana (floating rock, unmeltable ice, etc)
	ElementalChaos,
	/// (Fantasy Biome) Living landscape, such as an ocean-sized amoeba
	Ooze,
}
impl Biome {
	/// This array is used as a work-around for the Rust compiler not supporting
	/// enum iterators. For every enum variant added to Biome, an entry must be
	/// added to this array (and a const struct added to BiomeEnumData). Unit
	/// tests are used to check that there isn't a mismatch between this array,
	/// the Biome enum, the BiomeEnumData struct, and related functions
	const _VALUES: [Self; 35] = [Self::Unknown, Self::Wetland, Self::Jungle, Self::SeasonalForest, Self::NeedleleafForest, Self::Grassland, Self::DesertShrubland, Self::Tundra, Self::Freshwater, Self::SeaForest, Self::TropicalReef, Self::RockyShallows, Self::DeepOcean, Self::ShallowOcean, Self::Barren, Self::SandSea, Self::IceSheet, Self::BoilingSea, Self::Moonscape, Self::MagmaSea, Self::CryogenSea, Self::GasGiant, Self::Star, Self::NeutronStar, Self::EventHorizon, Self::Farmland, Self::Urban, Self::Ruins, Self::PollutedWasteland, Self::PollutedWastewater, Self::Bioluminescent, Self::Dead, Self::MagicGarden, Self::ElementalChaos, Self::Ooze, ];
 	/// Returns a reference to a static array of all enum variants (useful for
 	/// iteration over Biome enum types)
 	/// # Returns
 	/// Array or Biome enum variants
	pub fn values() -> &'static [Self; 35]{
		return &(Self::_VALUES);
	}
}
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
impl BiomeEnumData {
	/// const data for enum Biome::Unknown
	const UNKNOWN: Self = Self{biome_code: 0, enum_name: &"Unknown", common_name: &"unknown", technical_name: &"unknown"};
	/// const data for enum Biome::Wetland
	const WETLAND: Self = Self{biome_code: 1, enum_name: &"Wetland", common_name: &"swamp", technical_name: &"wetland"};
	/// const data for enum Biome::Jungle
	const JUNGLE: Self = Self{biome_code: 2, enum_name: &"Jungle", common_name: &"jungle", technical_name: &"tropical rainforest"};
	/// const data for enum Biome::SeasonalForest
	const SEASONAL_FOREST: Self = Self{biome_code: 3, enum_name: &"SeasonalForest", common_name: &"deciduous forest", technical_name: &"temperate forest"};
	/// const data for enum Biome::NeedleleafForest
	const NEEDLELEAF_FOREST: Self = Self{biome_code: 4, enum_name: &"NeedleleafForest", common_name: &"evergreen forest", technical_name: &"needleleaf forest"};
	/// const data for enum Biome::Grassland
	const GRASSLAND: Self = Self{biome_code: 5, enum_name: &"Grassland", common_name: &"grassland", technical_name: &"grassland"};
	/// const data for enum Biome::DesertShrubland
	const DESERT_SHRUBLAND: Self = Self{biome_code: 6, enum_name: &"DesertShrubland", common_name: &"desert", technical_name: &"xeric shrubland"};
	/// const data for enum Biome::Tundra
	const TUNDRA: Self = Self{biome_code: 7, enum_name: &"Tundra", common_name: &"tundra", technical_name: &"tundra"};
	/// const data for enum Biome::Freshwater
	const FRESHWATER: Self = Self{biome_code: 17, enum_name: &"Freshwater", common_name: &"freshwater", technical_name: &"freshwater"};
	/// const data for enum Biome::SeaForest
	const SEA_FOREST: Self = Self{biome_code: 18, enum_name: &"SeaForest", common_name: &"seaweed forest", technical_name: &"marine forest"};
	/// const data for enum Biome::TropicalReef
	const TROPICAL_REEF: Self = Self{biome_code: 19, enum_name: &"TropicalReef", common_name: &"coral reef", technical_name: &"tropical reef"};
	/// const data for enum Biome::RockyShallows
	const ROCKY_SHALLOWS: Self = Self{biome_code: 20, enum_name: &"RockyShallows", common_name: &"rocky shallows", technical_name: &"rocky shallows"};
	/// const data for enum Biome::DeepOcean
	const DEEP_OCEAN: Self = Self{biome_code: 16, enum_name: &"DeepOcean", common_name: &"ocean", technical_name: &"deep ocean"};
	/// const data for enum Biome::ShallowOcean
	const SHALLOW_OCEAN: Self = Self{biome_code: 21, enum_name: &"ShallowOcean", common_name: &"shallow ocean", technical_name: &"shallow ocean"};
	/// const data for enum Biome::Barren
	const BARREN: Self = Self{biome_code: 8, enum_name: &"Barren", common_name: &"barren", technical_name: &"barren"};
	/// const data for enum Biome::SandSea
	const SAND_SEA: Self = Self{biome_code: 9, enum_name: &"SandSea", common_name: &"sand dunes", technical_name: &"eolian sand"};
	/// const data for enum Biome::IceSheet
	const ICE_SHEET: Self = Self{biome_code: 22, enum_name: &"IceSheet", common_name: &"ice sheet", technical_name: &"ice sheet"};
	/// const data for enum Biome::BoilingSea
	const BOILING_SEA: Self = Self{biome_code: 23, enum_name: &"BoilingSea", common_name: &"boiling sea", technical_name: &"hydrothermal sea"};
	/// const data for enum Biome::Moonscape
	const MOONSCAPE: Self = Self{biome_code: 64, enum_name: &"Moonscape", common_name: &"moonscape", technical_name: &"regolith"};
	/// const data for enum Biome::MagmaSea
	const MAGMA_SEA: Self = Self{biome_code: 65, enum_name: &"MagmaSea", common_name: &"magma sea", technical_name: &"lava sea"};
	/// const data for enum Biome::CryogenSea
	const CRYOGEN_SEA: Self = Self{biome_code: 66, enum_name: &"CryogenSea", common_name: &"cryogen sea", technical_name: &"cryogen sea"};
	/// const data for enum Biome::GasGiant
	const GAS_GIANT: Self = Self{biome_code: 67, enum_name: &"GasGiant", common_name: &"gas giant", technical_name: &"gas giant"};
	/// const data for enum Biome::Star
	const STAR: Self = Self{biome_code: 68, enum_name: &"Star", common_name: &"star", technical_name: &"star"};
	/// const data for enum Biome::NeutronStar
	const NEUTRON_STAR: Self = Self{biome_code: 69, enum_name: &"NeutronStar", common_name: &"neutron star", technical_name: &"neutron star"};
	/// const data for enum Biome::EventHorizon
	const EVENT_HORIZON: Self = Self{biome_code: 70, enum_name: &"EventHorizon", common_name: &"black hole", technical_name: &"event horizon"};
	/// const data for enum Biome::Farmland
	const FARMLAND: Self = Self{biome_code: 32, enum_name: &"Farmland", common_name: &"farmland", technical_name: &"farmland"};
	/// const data for enum Biome::Urban
	const URBAN: Self = Self{biome_code: 33, enum_name: &"Urban", common_name: &"urban", technical_name: &"urban"};
	/// const data for enum Biome::Ruins
	const RUINS: Self = Self{biome_code: 34, enum_name: &"Ruins", common_name: &"ruins", technical_name: &"ruins"};
	/// const data for enum Biome::PollutedWasteland
	const POLLUTED_WASTELAND: Self = Self{biome_code: 35, enum_name: &"PollutedWasteland", common_name: &"toxic wasteland", technical_name: &"industrial barrens"};
	/// const data for enum Biome::PollutedWastewater
	const POLLUTED_WASTEWATER: Self = Self{biome_code: 36, enum_name: &"PollutedWastewater", common_name: &"toxic water", technical_name: &"hypoxic water"};
	/// const data for enum Biome::Bioluminescent
	const BIOLUMINESCENT: Self = Self{biome_code: 112, enum_name: &"Bioluminescent", common_name: &"permanent night", technical_name: &"bioluminescent flora"};
	/// const data for enum Biome::Dead
	const DEAD: Self = Self{biome_code: 113, enum_name: &"Dead", common_name: &"dead land", technical_name: &"dead land"};
	/// const data for enum Biome::MagicGarden
	const MAGIC_GARDEN: Self = Self{biome_code: 114, enum_name: &"MagicGarden", common_name: &"magic garden", technical_name: &"magic garden"};
	/// const data for enum Biome::ElementalChaos
	const ELEMENTAL_CHAOS: Self = Self{biome_code: 115, enum_name: &"ElementalChaos", common_name: &"elemental chaos", technical_name: &"elemental chaos"};
	/// const data for enum Biome::Ooze
	const OOZE: Self = Self{biome_code: 116, enum_name: &"Ooze", common_name: &"ooze", technical_name: &"giant slime"};
}
/// This is a work-around for the Rust compiler not supporting Java-style enums
/// of data constants. For a given reference to a Biome enum variant, it
/// returns the corresponding const BiomeEnumData struct instance holding the
/// const data for that enum variant.
/// # Parameters
/// * **biome: &Biome** - A reference to a Biome enum variant
/// # Returns
/// A static reference to a BiomeEnumData struct constant
fn get_data(biome: &Biome) -> &'static BiomeEnumData {
	match *biome {
		Biome::Unknown => &BiomeEnumData::UNKNOWN,
		Biome::Wetland => &BiomeEnumData::WETLAND,
		Biome::Jungle => &BiomeEnumData::JUNGLE,
		Biome::SeasonalForest => &BiomeEnumData::SEASONAL_FOREST,
		Biome::NeedleleafForest => &BiomeEnumData::NEEDLELEAF_FOREST,
		Biome::Grassland => &BiomeEnumData::GRASSLAND,
		Biome::DesertShrubland => &BiomeEnumData::DESERT_SHRUBLAND,
		Biome::Tundra => &BiomeEnumData::TUNDRA,
		Biome::Freshwater => &BiomeEnumData::FRESHWATER,
		Biome::SeaForest => &BiomeEnumData::SEA_FOREST,
		Biome::TropicalReef => &BiomeEnumData::TROPICAL_REEF,
		Biome::RockyShallows => &BiomeEnumData::ROCKY_SHALLOWS,
		Biome::DeepOcean => &BiomeEnumData::DEEP_OCEAN,
		Biome::ShallowOcean => &BiomeEnumData::SHALLOW_OCEAN,
		Biome::Barren => &BiomeEnumData::BARREN,
		Biome::SandSea => &BiomeEnumData::SAND_SEA,
		Biome::IceSheet => &BiomeEnumData::ICE_SHEET,
		Biome::BoilingSea => &BiomeEnumData::BOILING_SEA,
		Biome::Moonscape => &BiomeEnumData::MOONSCAPE,
		Biome::MagmaSea => &BiomeEnumData::MAGMA_SEA,
		Biome::CryogenSea => &BiomeEnumData::CRYOGEN_SEA,
		Biome::GasGiant => &BiomeEnumData::GAS_GIANT,
		Biome::Star => &BiomeEnumData::STAR,
		Biome::NeutronStar => &BiomeEnumData::NEUTRON_STAR,
		Biome::EventHorizon => &BiomeEnumData::EVENT_HORIZON,
		Biome::Farmland => &BiomeEnumData::FARMLAND,
		Biome::Urban => &BiomeEnumData::URBAN,
		Biome::Ruins => &BiomeEnumData::RUINS,
		Biome::PollutedWasteland => &BiomeEnumData::POLLUTED_WASTELAND,
		Biome::PollutedWastewater => &BiomeEnumData::POLLUTED_WASTEWATER,
		Biome::Bioluminescent => &BiomeEnumData::BIOLUMINESCENT,
		Biome::Dead => &BiomeEnumData::DEAD,
		Biome::MagicGarden => &BiomeEnumData::MAGIC_GARDEN,
		Biome::ElementalChaos => &BiomeEnumData::ELEMENTAL_CHAOS,
		Biome::Ooze => &BiomeEnumData::OOZE,
	}
}
impl Biome {
 	/// Returns the Plantabyte Biome code for this Biome
	pub fn bcode(&self) -> u8 {
		get_data(self).biome_code
	}
 	/// Returns the Plantabyte Biome code name for this Biome (intended for
 	/// debugging). For user-facing apps, either use this as the key for i18n
 	/// localization or use `.common_name()` or `.technical_name()` instead.
	pub fn name(&self) -> &'static str {
		get_data(self).enum_name
	}
 	/// Returns the US English name of this Biome for a non-scientist audience
	pub fn common_name(&self) -> &'static str {
		get_data(self).common_name
	}
 	/// Returns the US English name of this Biome for a scientist audience
	pub fn technical_name(&self) -> &'static str {
		get_data(self).technical_name
	}
}
	/// Converts from Plantabyte biome code (as u8) to the corresponding Biome enum
	/// # Parameters
	/// * **bcode: u8** - Plantabyte biome code
	/// # Returns
	/// Returns the corresponding Biome enum
impl From<u8> for Biome {
	fn from(bcode: u8) -> Biome {
		match bcode {
			0 => Biome::Unknown,
			1 => Biome::Wetland,
			2 => Biome::Jungle,
			3 => Biome::SeasonalForest,
			4 => Biome::NeedleleafForest,
			5 => Biome::Grassland,
			6 => Biome::DesertShrubland,
			7 => Biome::Tundra,
			17 => Biome::Freshwater,
			18 => Biome::SeaForest,
			19 => Biome::TropicalReef,
			20 => Biome::RockyShallows,
			16 => Biome::DeepOcean,
			21 => Biome::ShallowOcean,
			8 => Biome::Barren,
			9 => Biome::SandSea,
			22 => Biome::IceSheet,
			23 => Biome::BoilingSea,
			64 => Biome::Moonscape,
			65 => Biome::MagmaSea,
			66 => Biome::CryogenSea,
			67 => Biome::GasGiant,
			68 => Biome::Star,
			69 => Biome::NeutronStar,
			70 => Biome::EventHorizon,
			32 => Biome::Farmland,
			33 => Biome::Urban,
			34 => Biome::Ruins,
			35 => Biome::PollutedWasteland,
			36 => Biome::PollutedWastewater,
			112 => Biome::Bioluminescent,
			113 => Biome::Dead,
			114 => Biome::MagicGarden,
			115 => Biome::ElementalChaos,
			116 => Biome::Ooze,
			_ => Biome::Unknown,
		}
	}
}
impl From<u16> for Biome {
	/// Converts from Plantabyte biome code (as u16) to the corresponding Biome enum
	/// # Parameters
	/// * **bcode: u16** - Plantabyte biome code
	/// # Returns
	/// Returns the corresponding Biome enum
	fn from(bcode: u16) -> Biome {
		if bcode < 256 {
			Biome::from(bcode as u8)
		} else {
			Biome::Unknown
		}
	}
}
impl From<i16> for Biome {
	/// Converts from Plantabyte biome code (as i16) to the corresponding Biome enum
	/// # Parameters
	/// * **bcode: i16** - Plantabyte biome code
	/// # Returns
	/// Returns the corresponding Biome enum
	fn from(bcode: i16) -> Biome {
		if bcode > 0 && bcode < 256 {
			Biome::from(bcode as u8)
		} else {
			Biome::Unknown
		}
	}
}
impl From<u32> for Biome {
	/// Converts from Plantabyte biome code (as u32) to the corresponding Biome enum
	/// # Parameters
	/// * **bcode: u32** - Plantabyte biome code
	/// # Returns
	/// Returns the corresponding Biome enum
	fn from(bcode: u32) -> Biome {
		if bcode < 256 {
			Biome::from(bcode as u8)
		} else {
			Biome::Unknown
		}
	}
}
impl From<i32> for Biome {
	/// Converts from Plantabyte biome code (as i32) to the corresponding Biome enum
	/// # Parameters
	/// * **bcode: i32** - Plantabyte biome code
	/// # Returns
	/// Returns the corresponding Biome enum
	fn from(bcode: i32) -> Biome {
		if bcode > 0 && bcode < 256 {
			Biome::from(bcode as u8)
		} else {
			Biome::Unknown
		}
	}
}
impl From<u64> for Biome {
	/// Converts from Plantabyte biome code (as u64) to the corresponding Biome enum
	/// # Parameters
	/// * **bcode: u64** - Plantabyte biome code
	/// # Returns
	/// Returns the corresponding Biome enum
	fn from(bcode: u64) -> Biome {
		if bcode < 256 {
			Biome::from(bcode as u8)
		} else {
			Biome::Unknown
		}
	}
}
impl From<i64> for Biome {
	/// Converts from Plantabyte biome code (as i64) to the corresponding Biome enum
	/// # Parameters
	/// * **bcode: i64** - Plantabyte biome code
	/// # Returns
	/// Returns the corresponding Biome enum
	fn from(bcode: i64) -> Biome {
		if bcode > 0 && bcode < 256 {
			Biome::from(bcode as u8)
		} else {
			Biome::Unknown
		}
	}
}
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
	/// * **b: u8** - The Biome to convert
	/// # Returns
	/// Returns the Plantabyte biome code corresponding to the given Biome enum
	fn from(b: Biome) -> u8 {
		b.bcode()
	}
}
impl Display for Biome {
	/// Text representation of this Biome enum variant, for internal use. User-facing
	/// apps should instead either use this as the key for i18n localization or use
	/// `.common_name()` or `.technical_name()`.
	fn fmt(&self, f: &mut Formatter<'_>) -> Result {
		f.write_str(self.name().as_ref())
	}
}
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
			assert_eq!(*biome, biome2, "Assertion failure: round-trip from {} to {} to {} did not produce consistent Biome", 
					biome, bcode, biome2);
			assert_eq!(bcode, bcode2, "Assertion failure: round-trip from {} to {} to {} to {} did not produce consistent bcode", 
					biome, bcode, biome2, bcode2);
		}
		for bcode1 in 0..255 {
			let biome1 = Biome::from(bcode1);
			let bcode2 = u8::from(biome1);
			let biome2 = Biome::from(bcode2);
			let bcode3 = u8::from(biome2);
			if biome1 != Biome::Unknown {
				assert_eq!(bcode1, bcode2, "Assertion failure: round-trip from {} to {} to {} did not produce consistent bcode for known source bcode", 
					bcode1, biome1, bcode2);
			}
			assert_eq!(biome1, biome2, "Assertion failure: round-trip from {} to {} to {} to {} did not produce consistent Biome enum", 
					bcode1, biome1, bcode2, biome2);
			assert_eq!(bcode2, bcode3, "Assertion failure: round-trip from {} to {} to {} to {} to {} did not produce consistent bcode", 
					bcode1, biome1, bcode2, biome2, bcode3);
		}

	}
}

