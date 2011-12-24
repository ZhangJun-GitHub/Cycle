#!/usr/bin/env python
#====================================================
#        Cycle - calendar for women
#        Distributed under GNU Public License
# Original author: Oleg S. Gints
# Maintainer: Matt Molyneaux (moggers87+git@moggers87.co.uk)
# Home page: http://moggers.co.uk/cgit/cycle.git/about
#===================================================    
import os, locale
from main import MyApp

locale.setlocale(locale.LC_ALL, "")
dir_path = os.getcwd()
app = MyApp(0)
app.MainLoop()

