# -*- coding: utf-8 -*-

#!/usr/bin/python  
#python version: 2.7.3  
#Filename: SetupTestOMP.py  
   
# Run as:    
#    python setup.py build_ext --inplace    
     
import sys    
sys.path.insert(0, "..")    
     
from distutils.core import setup    
from distutils.extension import Extension    
from Cython.Build import cythonize    
from Cython.Distutils import build_ext  
     
# ext_module = cythonize("TestOMP.pyx")    
ext_module = Extension(  
                        "deepnovo_cython_modules",  
            ["deepnovo_cython_modules.pyx"],  
            extra_compile_args=["/openmp"],  
            extra_link_args=["/openmp"],  
            )  
     
setup(  
    cmdclass = {'build_ext': build_ext},  
        ext_modules = [ext_module],   
)  