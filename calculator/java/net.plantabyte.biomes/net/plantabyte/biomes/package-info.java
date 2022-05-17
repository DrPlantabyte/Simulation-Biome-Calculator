/**
 <p>This package provides and enum and a class:
 {@link net.plantabyte.biomes.Biome} and
 {@link net.plantabyte.biomes.BiomeCalculator}.</p>
 <p>The enum {@link net.plantabyte.biomes.Biome} represents the Dr. Plantabyte
 biome system, which has about a dozen terrestrial biomes and eight aquatic
 biomes, plus several abiotic "biomes" representing extreme and inhospitable
 planetary environments.</p>
 <p>Class {@link net.plantabyte.biomes.BiomeCalculator} is a biome calculator
 that predicts the biome one should expect in a given environment. The
 prediction is made based ont he following parameters, which are relatively
 easy to simulate:
 <ul>
 <li>solar irradiance (aka solar flux)</li>
 <li>altitude</li>
 <li>average annual temperature</li>
 <li>range of annual temperature variation (~1.5 standard deviations)</li>
 <li>annual precipitation (10mm of snow == 1 mm precipitation)</li>
 </ul>
 </p>
 */
package net.plantabyte.biomes;