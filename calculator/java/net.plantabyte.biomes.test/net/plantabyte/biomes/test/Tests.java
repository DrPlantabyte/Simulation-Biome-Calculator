package net.plantabyte.biomes.test;


import net.plantabyte.biomes.Biome;
import net.plantabyte.biomes.BiomeCalculator;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Collectors;
import java.util.zip.GZIPInputStream;


public class Tests {
	public static void main(String[] args){
		final AtomicBoolean allGood = new AtomicBoolean(true);
		Arrays.stream(Tests.class.getMethods()).filter(Tests::isTestMethod).forEach((Method test)->{
			System.out.println(test.getName()+"...");
			try {
				test.invoke(null);
				System.out.println("\tSuccess!");
			} catch(Exception e) {
				System.out.println("\tFailure!");
				System.out.flush();
				if(e.getCause() != null) {
					e.getCause().printStackTrace(System.err);
				} else {
					e.printStackTrace(System.err);
				}
				allGood.set(false);
			}
			System.out.println();
			System.out.flush();
			System.err.flush();
		});
		System.exit(allGood.get() ? 0 : 1);
	}
	public static void testClassifyBiomeWithEarthRef() throws IOException {
		var table = unzipCSV("/resources/Earth_ref_table.csv.gz");
		var header = Arrays.asList(table[0]);
		int iGravity = header.indexOf("gravity_m_per_s2");
		int iMeanSurfPressure = header.indexOf("mean_surface_pressure_kPa");
		int iTOAFlux = header.indexOf("toa_solar_flux_Wpm2");
		int iMeanFlux = header.indexOf("mean_solar_flux_Wpm2");
		int iAlt = header.indexOf("altitude_m");
		int iTemp = header.indexOf("mean_temp_C");
		int iTempVar = header.indexOf("temp_var_C");
		int iPrecip = header.indexOf("annual_precip_mm");
		int iExo = header.indexOf("exoplanet");
		int iBiome = header.indexOf("biome");
		var bc = new BiomeCalculator();
		for(int row = 1; row < table.length; ++row){
			var trow = table[row];
			if(trow.length <= 1) continue; // blank row or comment
			bc = bc.asExoplanet(Boolean.parseBoolean(trow[iExo]));
			var b = bc.classifyBiome(
					Double.parseDouble(trow[iMeanFlux]),
					bc.pressureAtDryAltitude(Double.parseDouble(trow[iAlt]), Double.parseDouble(trow[iTemp])),
					Double.parseDouble(trow[iAlt]),
					Double.parseDouble(trow[iTemp]),
					Double.parseDouble(trow[iTempVar]),
					Double.parseDouble(trow[iPrecip])
			);
			var tbiome = Biome.fromBiomeCode(Byte.parseByte(trow[iBiome]));
			if(!b.equals(tbiome)){
				// mismatch
				throw new AssertionError(String.format("Error in row # %d: \n%s\n%s\n\t"
						+ "Should have returned biome %s but instead returned biome %s",
						row, Arrays.toString(table[0]), Arrays.toString(trow), tbiome.toString(), b.toString()));
			}
		}
	}
	
	private static boolean isTestMethod(Method m){
		return Modifier.isStatic(m.getModifiers())
				&& m.getName().startsWith("test");
	}

	private static String[][] unzipCSV(String resourcePath) throws IOException {
		var src = new BufferedReader(new InputStreamReader(
				new GZIPInputStream(Tests.class.getResourceAsStream(resourcePath)),
				StandardCharsets.UTF_8
		));
		return src.lines().map((String s) -> s.split(",")).collect(Collectors.toList()).toArray(new String[0][]);
	}
}