import os
import shutil

head = "D:/Colton_Data/Mexican_Basins_Project/"

for root, dirs, files in os.walk('RH24D'):
	for file in files:
		if 'sub' in file:
			tr = root.replace('\\','/')
			oldp = head + tr + "/"+file
			newp = head + "el_salado/" + file
			shutil.move(oldp,newp)
