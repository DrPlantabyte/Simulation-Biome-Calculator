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
 	/// Array of Biome enum variants
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
impl From<u8> for Biome {
	/// Converts from Plantabyte biome code (as u8) to the corresponding Biome enum
	/// # Parameters
	/// * **bcode: u8** - Plantabyte biome code
	/// # Returns
	/// Returns the corresponding Biome enum
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
			8 => Biome::Barren,
			9 => Biome::SandSea,
			16 => Biome::DeepOcean,
			17 => Biome::Freshwater,
			18 => Biome::SeaForest,
			19 => Biome::TropicalReef,
			20 => Biome::RockyShallows,
			21 => Biome::ShallowOcean,
			22 => Biome::IceSheet,
			23 => Biome::BoilingSea,
			32 => Biome::Farmland,
			33 => Biome::Urban,
			34 => Biome::Ruins,
			35 => Biome::PollutedWasteland,
			36 => Biome::PollutedWastewater,
			64 => Biome::Moonscape,
			65 => Biome::MagmaSea,
			66 => Biome::CryogenSea,
			67 => Biome::GasGiant,
			68 => Biome::Star,
			69 => Biome::NeutronStar,
			70 => Biome::EventHorizon,
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

pub mod classifier {
	use std::cmp::Ordering;
	use std::hash::{Hash, Hasher};
	use crate::Biome;
	use ordered_float::OrderedFloat;

	#[allow(non_snake_case)]
	#[derive(Copy, Clone, Debug)]
	#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
	pub struct Planet {
		pub mass_kg: f64,
		pub mean_radius_km: f64,
		pub toa_solar_flux_Wpm2: f64,
		pub axis_tilt_deg: f64,
		pub tidal_lock: bool,
		pub mean_surface_pressure_kPa: f64,
		pub exoplanet: bool
	}
	impl Planet {
		pub const EARTH: Planet = Planet{mass_kg: 5.972e24, mean_radius_km: 6.371e3,
			toa_solar_flux_Wpm2:
		1373., axis_tilt_deg: 23., mean_surface_pressure_kPa: 101.3, tidal_lock: false,
			exoplanet: false};

		fn to_f64_array(&self) -> [f64; 7]{
			return [self.mass_kg, self.mean_radius_km, self.toa_solar_flux_Wpm2,
				self.mean_surface_pressure_kPa, self.axis_tilt_deg,
				self.tidal_lock as i64 as f64, self.exoplanet as i64 as f64];
		}
	}
	impl Hash for Planet {
		// Note: not a particularly effective hash, but good enough to be usable
		fn hash<H: Hasher>(&self, state: &mut H) {
			let vals = self.to_f64_array();
			for v in vals {
				let hasher = OrderedFloat(v);
				hasher.hash(state);
			}
		}
	}
	impl PartialEq for Planet {
		fn eq(&self, other: &Self) -> bool {
			return self.tidal_lock == other.tidal_lock
				&& self.exoplanet == other.exoplanet
				&& sorta_equal(self.mass_kg, other.mass_kg)
				&& sorta_equal(self.mean_radius_km, other.mean_radius_km)
				&& sorta_equal(self.toa_solar_flux_Wpm2, other.toa_solar_flux_Wpm2)
				&& sorta_equal(self.axis_tilt_deg, other.axis_tilt_deg)
				&& sorta_equal(self.mean_surface_pressure_kPa, other.mean_surface_pressure_kPa)
		}
	}

	impl Eq for Planet {} // marker trait
	impl PartialOrd for Planet{
		fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
			return Some(self.cmp(other));
		}
	}
	impl Ord for Planet{
		fn cmp(&self, other: &Self) -> Ordering {
			let self_ords = self.to_f64_array();
			let other_ords = other.to_f64_array();
			for i in 0..7 {
				let s = OrderedFloat(self_ords[i]);
				let o = OrderedFloat(other_ords[i]);
				let cmp = s.cmp(&o);
				if cmp != Ordering::Equal{
					return cmp;
				}
			}
			return Ordering::Equal;
		}
	}

	fn sorta_equal(a: f64, b: f64) -> bool{
		if a.is_finite() && b.is_finite(){
			return !(a < b || a > b); // weird, but handles +/- 0
		} else if a.is_nan() && b.is_nan() {
			return true; // not equal, but functionally equivalent
		} else if a.is_infinite() && b.is_infinite() {
			return true; // not equal, but functionally equivalent
		} else {
			// definitely not equal
			return false;
		}
	}


	const REF_CLASSES: [Biome; 9] = [Biome::Wetland, Biome::Jungle, Biome::SeasonalForest,
		Biome::NeedleleafForest, Biome::Grassland, Biome::DesertShrubland, Biome::Tundra,
		Biome::Barren, Biome::SandSea];
	const REF_POINTS: [[[f32; 4]; 5]; 9] = [ // size = [9][5][4]
//// wetlands
		[[0.97589505f32, 0.6692817f32, 0.09676683f32, 0.42183435f32],
			[0.2872733f32, 0.5562218f32, 0.21704593f32, 0.3098737f32],
			[0.95833284f32, 0.6877248f32, 0.12377492f32, 0.2995282f32],
			[0.6171483f32, 0.47020113f32, 0.4836682f32, 0.22195342f32],
			[0.81850535f32, 0.60123855f32, 0.25867933f32, 0.31303504f32]],
//// jungle
		[[0.7665621f32, 0.5300055f32, 0.2408872f32, 0.3123359f32],
			[0.99121696f32, 0.6713649f32, 0.07588506f32, 0.40304184f32],
			[0.98553646f32, 0.67212886f32, 0.08356771f32, 0.3337861f32],
			[0.9209426f32, 0.59560406f32, 0.15855226f32, 0.3750781f32],
			[0.99228674f32, 0.67052644f32, 0.07420062f32, 0.49766815f32]],
//// seasonalf32orest
		[[0.82307386f32, 0.54830164f32, 0.28397045f32, 0.32422626f32],
			[0.95406234f32, 0.68983954f32, 0.16054682f32, 0.29840717f32],
			[0.5337313f32, 0.44197488f32, 0.4220576f32, 0.24119267f32],
			[0.70596063f32, 0.5029748f32, 0.37620285f32, 0.26919958f32],
			[0.65009725f32, 0.41467762f32, 0.53735024f32, 0.24624129f32]],
//// needleleaff32orest
		[[0.8442506f32, 0.513412f32, 0.23853904f32, 0.31593102f32],
			[0.4755671f32, 0.42182055f32, 0.32860836f32, 0.25947723f32],
			[0.69879943f32, 0.5263777f32, 0.3583926f32, 0.24800086f32],
			[0.6385724f32, 0.44265494f32, 0.30205786f32, 0.41645652f32],
			[0.59855306f32, 0.41948298f32, 0.4608879f32, 0.21030518f32]],
//// grassland
		[[0.9590115f32, 0.69129807f32, 0.14321554f32, 0.33431706f32],
			[0.64463437f32, 0.51307285f32, 0.6764352f32, 0.17131203f32],
			[0.75970644f32, 0.53838587f32, 0.34264302f32, 0.25237092f32],
			[0.9574419f32, 0.76865923f32, 0.21147878f32, 0.2162868f32],
			[0.7787093f32, 0.64991206f32, 0.49281284f32, 0.1717132f32]],
//// desert
		[[0.8768907f32, 0.68539584f32, 0.30395174f32, 0.18175352f32],
			[0.85951805f32, 0.75583154f32, 0.43008733f32, 0.13515931f32],
			[0.9133944f32, 0.80276865f32, 0.33543584f32, 0.15386288f32],
			[0.95464563f32, 0.8058968f32, 0.2042541f32, 0.1794926f32],
			[0.7509371f32, 0.62957406f32, 0.44375542f32, 0.1542665f32]],
//// tundra
		[[0.4441414f32, 0.30920148f32, 0.4959661f32, 0.24957538f32],
			[0.4513571f32, 0.23461857f32, 0.732274f32, 0.2127717f32],
			[0.6739347f32, 0.34742635f32, 0.41046205f32, 0.26215446f32],
			[0.577827f32, 0.32734275f32, 0.62989986f32, 0.22067626f32],
			[0.37011942f32, 0.15006503f32, 0.65958476f32, 0.18708763f32]],
//// barren
		[[0.29481938f32, 0.09472984f32, 0.59135556f32, 0.06860657f32],
			[0.86539465f32, 0.7506361f32, 0.37203112f32, 0.11493613f32],
			[0.664666f32, 0.6056427f32, 0.46542227f32, 0.14238815f32],
			[0.6938545f32, 0.43799615f32, 0.30913985f32, 0.2867542f32],
			[0.8466273f32, 0.53237015f32, 0.44636855f32, 0.16200702f32]],
//// sandsea
		[[0.82119286f32, 0.48783484f32, 0.44511366f32, 0.10902377f32],
			[0.9354581f32, 0.8444746f32, 0.28542006f32, 0.076657f32],
			[0.75143087f32, 0.70467633f32, 0.602095f32, 0.09906711f32],
			[0.8729486f32, 0.81519806f32, 0.4026484f32, 0.0783796f32],
			[0.24349129f32, 0.7866096f32, 0.45044297f32, 0.11177942f32]]
	];

	#[allow(non_snake_case)]
	pub fn classify_biome(
		mean_solar_flux_Wpm2: f64,
		pressure_kPa: f64,
		altitude_m: f64,
		mean_temp_C: f64,
		temp_var_C: f64,
		annual_precip_mm: f64
	) -> Biome {
		let mut biome_code: Biome = Biome::Unknown;
		//// constants and variables
		let min_rain_limit_mm = 110.;
		let max_rain_limit_mm = 6000.; // too much rain and we'll call it a wetland instead of a jungle
		let photic_zone_min_solar_flux_Wpm2 = 35.;
		let wave_disruption_depth_m = -6.; // corals, seagrasses, kelps, etc cannot grow above this depth
		let epsilon_water = 0.013333;  // Absorption per meter (150m == 1% transmission (0.01 = 10^(-epsilon*150))
		let benthic_solar_flux = mean_solar_flux_Wpm2 * f64::powf(10.,epsilon_water * altitude_m); // <- note: altitude is negative here
		let boiling_point_C = boiling_point(pressure_kPa);
		//// terrestrial biomes
		if altitude_m > 0. {
			if annual_precip_mm > max_rain_limit_mm {
				biome_code = Biome::Wetland;
			} else {
				////// rescale to normalize so that distance calcs aren't biased
				let mut closest_dist = 1e35;
				let norm_sol_flux = rescale(mean_solar_flux_Wpm2, 0.0, 800.);
				let norm_mtemp = rescale(mean_temp_C, -20., 50.);
				let norm_vtemp = rescale(temp_var_C, 0., 35.);
				let norm_precip = rescale(f64::sqrt(annual_precip_mm), 0.0, 75.);
				for bclass in 0..9 as usize{
					for refpt in 0..5 as usize{
						let d = dist4fd(REF_POINTS[bclass][refpt][0], REF_POINTS[bclass][refpt][1],
										   REF_POINTS[bclass][refpt][2], REF_POINTS[bclass][refpt][3],
										   norm_sol_flux, norm_mtemp, norm_vtemp, norm_precip
						);
						if d < closest_dist {
							closest_dist = d;
							biome_code = REF_CLASSES[bclass];
						}
					}
				}
			}
			if biome_code == Biome::Jungle && temp_var_C > 6.0 {
				// too much variation for jungle, actually grassland
				biome_code = Biome::Grassland;
			}
		} else {
			//// marine biomes
			if benthic_solar_flux >= photic_zone_min_solar_flux_Wpm2 {
				// sea floor in photic zone
				if mean_temp_C > 5. && mean_temp_C < 20. && altitude_m < wave_disruption_depth_m {
					biome_code = Biome::SeaForest;
				} else if mean_temp_C >= 20. && mean_temp_C < 30. && altitude_m < wave_disruption_depth_m {
					biome_code = Biome::TropicalReef;
				} else {
					biome_code = Biome::RockyShallows;
				}
			} else if altitude_m > -200. {
				biome_code = Biome::ShallowOcean;
			} else {
				biome_code = Biome::DeepOcean;
			}
		}
		//// extreme biomes
		if altitude_m > 0. {
			if annual_precip_mm < min_rain_limit_mm {
				if mean_temp_C > 15. {
					biome_code = Biome::SandSea;
				} else if mean_temp_C <= 15. {
					biome_code = Biome::Barren;
				}
			}
			if mean_temp_C >= boiling_point_C {
				biome_code = Biome::Moonscape;
			}
		} else {
			if mean_temp_C >= boiling_point_C {
				biome_code = Biome::BoilingSea;
			}
		}
		if (mean_temp_C < boiling_point_C) && (mean_temp_C + temp_var_C) < 0. {
			biome_code = Biome::IceSheet;
		}
		//// Done!
		return biome_code;
	}


	#[allow(non_snake_case)]
	pub fn classify_biome_on_planet_surface(
		planet: &Planet,
		mean_solar_flux_Wpm2: f64,
		altitude_m: f64,
		mean_temp_C: f64,
		temp_var_C: f64,
		annual_precip_mm: f64) -> Biome
	{
		// let mean_surface_pressure_kPa = planet.mean_surface_pressure_kPa;
		// let toa_solar_flux_Wpm2 = planet.toa_solar_flux_Wpm2;
		// let axis_tilt_deg = planet.axis_tilt_deg;
		// let tidal_lock = planet.tidal_lock;
		let mean_surface_pressure_kPa = planet.mean_surface_pressure_kPa;
		let exoplanet = planet.exoplanet;
		let gravity_m_per_s2 = gravity(planet.mass_kg, planet.mean_radius_km + (0.001*altitude_m));
		if f64::is_nan(gravity_m_per_s2 + mean_surface_pressure_kPa + mean_solar_flux_Wpm2 +
			altitude_m + mean_temp_C + temp_var_C + annual_precip_mm) {
			return Biome::Unknown;
		}
		let water_supercritical_pressure = 22000.; // kPa;
		let pyroxene_melting_point_C = 1000.;
		let quartz_boiling_boint_C = 2230.;
		////// cryogen params based on liquid nitrogen ( https://www.engineeringtoolbox.com/nitrogen-d_1421.html );
		//////// alternative cryogens: ammonia, methane; both would oxidize in presense of oxygen, so not as interesting;
		//////// (oxygen is a pretty common element);
		let cryo_crit_temp = -147.; // C;
		let cryo_crit_pressure = 3400.; // kPa;
		let cryo_triple_temp = -210.; // C;
		let goldilocks_min_atmosphere = 4.0; // kPa, water must be liquid up to 30 C for earth-like geography;
		let goldilocks_max_atmosphere = 3350.; // kPa, no super-critical gasses allowed for
		// earth-like geography;
		// cryo_triple_pressure = 12.5 // kPa;
		let vapor_pressure_kPa = 0.61094 * f64::exp((17.625 * (mean_temp_C + temp_var_C)) / ((mean_temp_C + temp_var_C) + 243.04)); // Magnus formula;
		let mut above_sealevel_m = altitude_m;
		if above_sealevel_m < 0. {
			above_sealevel_m = 0.;
		}
		let pressure_kPa = pressure_at_dry_altitude(planet, mean_temp_C, above_sealevel_m);
		let boiling_point_C = boiling_point(pressure_kPa);
		if exoplanet { // try to detect extreme conditions of a non-goldilocks-zone planet;
			if mean_temp_C > quartz_boiling_boint_C {
				//// at least as hot as a red dwarf XD;
				return Biome::Star;
			}
			if pressure_kPa > water_supercritical_pressure {
				////// defining a gas giant is a bit hand-wavey as of 2022;
				return Biome::GasGiant;
			}
			if mean_temp_C > pyroxene_melting_point_C {
				if altitude_m <= 0. {
					return Biome::MagmaSea;
				} else {
					return Biome::Moonscape;
				}
			}
			if pressure_kPa < vapor_pressure_kPa
				|| (mean_temp_C - temp_var_C) > boiling_point_C {
				////// not enough atmosphere to be anything other than a naked rock!;
				return Biome::Moonscape;
			}
			if (mean_temp_C > cryo_triple_temp) && (mean_temp_C < cryo_crit_temp)
				&& (pressure_kPa < cryo_crit_pressure)
				&& ( pressure_kPa > (1.6298e9*f64::exp(0.08898*mean_temp_C))) {
				//// liquid nitrogen planet! (like pluto);
				if altitude_m <= 0. {
					return Biome::CryogenSea;
				} else if annual_precip_mm > 0. {
					return Biome::IceSheet;
				} else {
					return Biome::Moonscape;
				}
			}
			if mean_surface_pressure_kPa < goldilocks_min_atmosphere
				|| mean_surface_pressure_kPa > goldilocks_max_atmosphere {
				return Biome::Moonscape;
			}
		}
		//// then check normal biomes;
		return classify_biome(
			mean_solar_flux_Wpm2,
			pressure_kPa,
			altitude_m,
			mean_temp_C,
			temp_var_C,
			annual_precip_mm
		);
	}

	#[allow(non_snake_case)]
	pub fn classify_biome_on_planet(
		planet: &Planet,
		altitude_m: f64,
		mean_temp_C: f64,
		temp_var_C: f64,
		annual_precip_mm: f64,
		latitude: f64,
		longitude: f64
	) -> Biome {
		let pi = std::f64::consts::PI;
		let two_over_pi = 0.5 * pi;
		let deg2Rad = pi / 180.;
		let radius_m = (planet.mean_radius_km * 1000.) + altitude_m;
		let mut above_sealevel_m = altitude_m;
		if above_sealevel_m < 0. {
			above_sealevel_m = 0.;
		}
		let pressure_kPa = pressure_at_dry_altitude(planet, mean_temp_C, above_sealevel_m);
		let epsilon_air = 3.46391e-5; // Absorption per kPa (1360 = 1371 * 10^(-eps * 101) );
		let max_flux = planet.toa_solar_flux_Wpm2 * f64::powf(10., -epsilon_air * pressure_kPa);
		let mut mean_solar_flux_Wpm2 = 0f64;
		let axis_tilt_deg = planet.axis_tilt_deg;
		if planet.tidal_lock {
			mean_solar_flux_Wpm2 =
				max_flux * two_over_pi * f64::cos(latitude) * clip(f64::cos(longitude), 0., 1.);
		} else {
			mean_solar_flux_Wpm2 = max_flux * two_over_pi * 0.5 * (
				clip(f64::cos(deg2Rad * (latitude - axis_tilt_deg)), 0., 1.) + clip(
					f64::cos(deg2Rad * (latitude + axis_tilt_deg)), 0., 1.));
		}
		//// if doing expoplanet calcualtion, first check astronomical biomes
		let min_neutron_star_density_Tpm3 = 1e14; // tons per cubic meter (aka g/cc)
		let max_neutron_star_density_Tpm3 = 2e16; // tons per cubic meter (aka g/cc)
		let planet_volume_m3 = 4.0/3.0*pi*radius_m*radius_m*radius_m;
		let planet_density_Tpm3 = planet.mass_kg / 1000. / planet_volume_m3;
		let red_dwarf_min_mass_kg = 1.2819e29;
		if planet.exoplanet { // try to detect extreme conditions of a non-goldilocks-zone planet
			if planet_density_Tpm3 > max_neutron_star_density_Tpm3 {
				////BLACK HOLE ! 
				return Biome::EventHorizon;
			}
			if planet_density_Tpm3 >= min_neutron_star_density_Tpm3 {
				////neutron star ! 
				return Biome::NeutronStar;}
			if planet.mass_kg >= red_dwarf_min_mass_kg {
				////big enough to spontaneously start thermonuclear fusion and become a star 
				return Biome::Star;
			}
		}
		return classify_biome_on_planet_surface(
			planet,
			mean_solar_flux_Wpm2,
			altitude_m,
			mean_temp_C,
			temp_var_C,
			annual_precip_mm
		);
	}

	fn rescale(x: f64, xmin: f64, xmax: f64) -> f64{
		return (x - xmin) / (xmax - xmin);
	}

	fn dist4fd(a1: f32, b1: f32, c1: f32, d1: f32, a2: f64, b2: f64, c2: f64, d2: f64) -> f64 {
		let da = a2 - a1 as f64;
		let db = b2 - b1 as f64;
		let dc = c2 - c1 as f64;
		let dd = d2 - d1 as f64;
		return f64::sqrt(da * da + db * db + dc * dc + dd * dd);
	}

	#[allow(non_snake_case)]
	fn boiling_point(pressure_kPa: f64) -> f64{
		let ln_mbar = f64::ln(pressure_kPa * 10.);
		let x = ln_mbar;
		let x2 = x * ln_mbar;
		let x3 = x2 * ln_mbar;
		let lp = 0.051769 * x3 + 0.65545 * x2 + 10.387 * x - 10.619;
		let hp = 0.47092 * x3 - 8.2481 * x2 + 75.520 * x - 183.98;
		if pressure_kPa< 101.3 {
			return lp;
		}else{
			return hp;
		}
	}

	#[allow(non_snake_case)]
	fn pressure_at_dry_altitude(planet: &Planet, altitude_m: f64, mean_temp_C: f64) -> f64 {
		let K = mean_temp_C + 273.15;
		let R = 8.314510;  // j/K/mole
		let air_molar_mass = 0.02897;  // kg/mol
		let gravity_m_per_s2 = gravity(planet.mass_kg, planet.mean_radius_km);
		let pressure_kPa = planet.mean_surface_pressure_kPa * f64::exp(-(air_molar_mass *
			gravity_m_per_s2 * altitude_m)/(R*K));
		return pressure_kPa;
	}

	#[allow(non_snake_case)]
	fn gravity(mass_kg: f64, distance_km: f64) -> f64 {
		let G = 6.6743015e-11; // N m2/kg2
		let distance_m = 1000. * distance_km;
		return G * (mass_kg) / (distance_m*distance_m);
	}

	fn clip(x: f64, xmin: f64, xmax: f64) -> f64 {
		if x < xmin { return xmin;}
		if x > xmax {return xmax;}
		return x;
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

