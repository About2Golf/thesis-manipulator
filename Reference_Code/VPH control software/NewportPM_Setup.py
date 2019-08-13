# -*- coding: utf-8 -*-
"""
Created on Fri Aug 22 14:50:02 2014

@author: Yuzo Ishikawa
"""

from distutils.core import setup, Extension

module1 = Extension('Newpma',
                    sources=['Newpma.cpp'],                    
                    include_dirs = ['C:\Users\fuv\Desktop\KPF VPH Tests'],                  
                    libraries = ['usbdll'],
                    library_dirs = ['C:\Users\fuv\Desktop\KPF VPH Tests'])

setup (name = 'Newpma',
       version = '2.0',
       description ='Newport Power Meter Model 1936-C',
       ext_modules = [module1])
