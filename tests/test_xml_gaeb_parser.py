# pytest ini import source folder lv_explorer
# vscode settings includes folder lv_explorer for type hinting

# ----- for direct debugging ------
def debugger_is_active() -> bool:
    return hasattr(sys, 'gettrace') and sys.gettrace() is not None

if debugger_is_active:
    import os, sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..\\gaeb_parser')))
# ----- for direct debugging ------

lv_file_name = "Pruefdatei GAEB DA XML 3.3 - Bauausfuehrung - V 04 04 2024.x83"
lv_file = os.path.abspath(os.path.join(os.path.dirname(__file__), f".\\official_tests_gaeb_da_xml_3_3\\bauausfuehrung\\{lv_file_name}"))

from xml_gaeb_parser import XmlGaebParser

def test_gaebDaXmlImport():
    parser = XmlGaebParser(lv_file)
    df = parser.get_df()
    assert (df.columns == ['Projekt', 'OZ', 'Gewerk', 'Untergewerk', 'Kurztext', 'Qty', 'QU', 'TLK', 'Langtext']).all()
    assert df.loc[0,"Projekt"] ==  parser.project_name
    assert df.__len__() == 35

# ----- for direct debugging ------
if debugger_is_active:
    test_gaebDaXmlImport()