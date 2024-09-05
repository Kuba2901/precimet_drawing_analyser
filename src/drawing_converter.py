import os
import subprocess

class DrawingConverter:
	def __init__(self, oda_converter_path):
		self.oda_converter_path = oda_converter_path

	def convert_dwg_to_dxf(self, input_dwg) -> str:
		import subprocess
		# PARAMS:
		# Input folder
		# Output folder
		# Output version: ACAD9, ACAD10, ACAD12, ACAD14, ACAD2000, ACAD2004, ACAD2007, ACAD20010, ACAD2013, ACAD2018
		# Output file type: DWG, DXF, DXB
		# Recurse Input Folder: 0, 1
		# Audit each file: 0, 1
		# (Optional) Input files filter: *.DWG, *.DXF

		# /Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter "." "tmp" "ACAD2018" "DXF" "0" "1"

		ODA_PATH = self.oda_converter_path
		INPUT_FOLDER = r"."
		OUTPUT_FOLDER = r"tmp"
		OUTVER = "ACAD2018"
		OUTFORMAT = "DXF"
		RECURSIVE = "0"
		AUDIT = "1"
		# INPUTFILTER = "*.DWG"
		cmd = [ODA_PATH, INPUT_FOLDER, OUTPUT_FOLDER, OUTVER, OUTFORMAT, RECURSIVE, AUDIT]
		subprocess.run(cmd, shell=True)
		import shutil
		shutil.move(f"{OUTPUT_FOLDER}/{input_dwg.replace('.dwg', '.dxf')}", f".")
		return input_dwg.replace('.dwg', '.dxf')
