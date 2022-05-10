from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("biome_classifier_model.pyx")
)

# execute command $ venv/bin/python3 setup.py build_ext --inplace