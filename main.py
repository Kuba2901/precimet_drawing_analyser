# import src.drawing_analyser as drawing_analyser

# file_name = "assets/1.dxf"
# analyser = drawing_analyser.DrawingAnalyser("Test", file_name)
# print(analyser)


import src.pm_analyser as pm_analyser
file_name = 'assets/3.dxf'
analyser = pm_analyser.PMAnalyser(file_name)
print(analyser)