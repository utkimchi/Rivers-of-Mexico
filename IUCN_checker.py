import os
import pandas
import numpy as np
import csv

toppather = "/home/utkimchi/Documents/RoM/Data/final_data/"
iucnpath = "/home/utkimchi/Documents/RoM/Data/IUCN_Species_Mexico/simple_summary.csv"
toproot = "/home/utkimchi/Documents/RoM/Data/final_data/Lacatun_Occurences"

iucn_list = pandas.read_csv(iucnpath)
iucn_dic = {}
print_dic = {}

for row in iucn_list.itertuples():
	if row.scientificName not in iucn_dic:
		iucn_dic[row.scientificName] = row.redlistCategory

templist = []
csv_columns = ["Species", "Redlist_Category"]

for root, dirs, files in os.walk(toppather, topdown=False):
	if root != toproot:
		t_name = "IUCN_" + toproot.split('/')[-1] + ".csv"
		toproot = root
		print("Checking for IUCN Listed Species")

		for key, value in iucn_dic.items():
			if key in templist:
				print_dic[key] = value

		try:
			with open(t_name, 'w') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerow(csv_columns)
				for key, val in print_dic.items():
					writer.writerow([key,val])
		except IOError:
			print("I/O error")
		print_dic = {}
		templist = []

   	for name in files:
   		if name[-3:] == "txt":
   			fullpath = os.path.join(root,name)
   			print("File at : " + fullpath)
   			df = pandas.read_csv(fullpath, sep ='\t', low_memory = False, error_bad_lines=False)
   			for row in df.itertuples():
   				if row.species not in templist:
   					templist.append(row.species)