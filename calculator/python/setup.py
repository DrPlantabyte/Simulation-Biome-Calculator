#!/usr/bin/env python

from setuptools import setup
from Cython.Build import cythonize

setup(name='Biome_Calculator',
	version='1.0.0',
	description="Dr. Planbtabyte's biome calculator",
	author='Christopher C. Hall',
	author_email='explosivegnome@yahoo.com',
	url='https://github.com/DrPlantabyte/Simulation-Biome-Calculator',
	packages=['biomecalculator', 'biomecalculator.impls'],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: LGPL License"
	],
	python_requires='>=3.8',
	install_requires=["cython", "numpy"],
	ext_modules = cythonize("biomecalculator/impls/classifier_cython.pyx", compiler_directives={'language_level' : "3"})
)
