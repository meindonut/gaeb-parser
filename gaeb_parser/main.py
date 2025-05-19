# example how to use the class XMLGaebParser

from xml_gaeb_parser import XmlGaebParser
import os

lv_file_name = "Pruefdatei GAEB DA XML 3.3 - Bauausfuehrung - V 04 04 2024.x83"
lv_file = os.path.abspath(os.path.join(os.path.dirname(__file__), f"..\\tests\\official_tests_gaeb_da_xml_3_3\\bauausfuehrung\\{lv_file_name}"))

parser = XmlGaebParser(lv_file)
df = parser.get_df()
print(df)