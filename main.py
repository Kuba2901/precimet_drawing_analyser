import drawing_analyser

file_name = "detal1.dxf"
analyser = drawing_analyser.DrawingAnalyser("Test", file_name)
analyser.analyse()
print(analyser)