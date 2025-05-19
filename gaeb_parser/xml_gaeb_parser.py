import pandas as pd
from bs4 import BeautifulSoup

# gaeb xml layout with linked functions
# (m) means multiple objects possible
# (r) special of itwo
#
# <GAEB>    (-> _parse_gaeb())
#   <GAEBInfo>
#   <PrjInfo>
#   <Award>     (-> _parse_award())
#       <AwardInfo>
#       <OWN>
#       <AddText>   (-> _parse_pretext())
#       <BoQ>       (-> _parse_boq())
#           <BoQInfo>
#           <BoQBody>   (-> _parse_body(level = 0))
#               <PerfDescr> (r)
#                   <PerfNo>
#                   <PerfLbl>
#                   <Description>   (m)
#                       <WICNo>     (r)
#                       <CompleteText>
#                           <DetailTxt>
#               <Remark>    (m)(-> _parse_item())
#                   <Description>
#                       <WICNo>     (r)
#                       <CompleteText>
#                           <DetailTxt>
#                           <OutlineText>
#               <BoQCtgy>  (m)("Hauptgewerke")
#                   <LblTx>
#                   <BoQBody>   (-> _parse_body(level = 1))
#                       <BoQCtgy>   (m)("Untergewerke")
#                           <LblTx>
#                           <BoQBody>
#                               <Itemlist>  (-> _parse_item_list())
#                                   <Remark>    (m)(-> _parse_item())("Hinweise")
#                                       <Description>
#                                           <WICNo>     (r)
#                                           <CompleteText>
#                                               <DetailTxt>     (-> _parse_detail_text())("Langtext")
#                                               <OutlineText>   ("Kurztext")
#                                   <Item>      (m)(-> _parse_item())("Positionen")
#                                       <Qty>   
#                                       <QU>psch</QU>
#                                       <Description>
#                                           <WICNo>     (r)
#                                           <CompleteText>
#                                               <DetailTxt>     (-> _parse_detail_text())("Langtext")
#                                               <OutlineText>   ("Kurztext")
#                                       <SumDescr>Yes</SumDescr>
#                                       <SubDescr>      (m)(__parse_item())
#                                           <SubDNo>01</SubDNo>
#                                           <Description>
#                                               <WICNo>     (r)
#                                               <CompleteText>
#                                                   <DetailTxt>     (-> _parse_detail_text())("Langtext")
#                                                   <OutlineText>   ("Kurztext")
#                                   <MarkupItem>(m)(-> _parse_item())("Zuschlag")
#                                       <MarkupType>
#                                       <Description>
#                                           <WICNo>     (r)
#                                           <CompleteText>
#                                               <DetailTxt>
#                                               <OutlineText>


# example usage see tests

class XmlGaebParser():
    """parses gaeb files and saves them as a table in pandas dataframe"""
    def __init__(self, file_path: str):
        self.project_name = None
        self.project_id = None
        self.dict_list = []
        self.oz = [None] * 3
        self.soup = None
        self._df = pd.DataFrame()
        self.std_title = ["(Gewerklos)", "(Untergewerklos)", "(Positionslos)"]
        self.title = self.std_title

        # text import settings
        self.text_translation_ul_insert_breaks_at_br = False
        self.text_translation_insert_breaks_at_br = True
        self.text_translation_insert_breaks_after_paragraph = True
        self.text_translation_insert_breaks_after_text = False

        self.load_df(file_path)

    def get_df(self):
        """returns resulting pd df"""
        return self._df

    def load_df(self, file_path: str):
        """ loads *.x8? gaeb file, parses it and and saves it into object._df (-> use get_df()) """

        with open(file_path, 'r', encoding='utf-8') as file:
            xmlContent = file.read()
        soup = BeautifulSoup(xmlContent, 'xml')
        for child in soup.children:
            if child.name == None:
                pass
            elif child.name == 'GAEB':
                self._parse_gaeb(child) 
            else:
                print(f"GAEB Parser: Element with name {child.name} with parent {soup.name} not parsed")

    # internal functions
    def _translate_text_supplement(self, soup: BeautifulSoup) -> str:

        # parse header of item        
        try:
            type = soup['Kind']
        except:
            type = ""

        try:
            id = soup['MarkLbl']
        except:
            id = ""

        # parse text
        
        if type == "Owner":
            typestr = "AT"
        elif type == "Bidder":
            typestr = "BT"
        else:
            typestr = ""

        text = "[" + typestr + id + "]"

        if soup.name is not None:
            for compl in soup.children:                          # can be <ComplCaption>, <ComplBody> or <ComplTail/>
                if compl.name == None:
                    continue
                elif compl.name == 'ComplCaption':
                    text += "["
                    text += self._parse_detail_text(compl)
                elif compl.name == 'ComplBody':
                    text += "["
                    text += self._parse_detail_text(compl)
                    text += "]"
                elif compl.name == 'ComplTail':
                    text += self._parse_detail_text(compl)
                    text += "]"
                else:
                    print("GAEB Parser: Unknown element in text supplement element")
        return text

    def _translate_ul(self, ul_soup: BeautifulSoup) -> str:
        text = ""
        for li in ul_soup.children:
            if li.name == None:
                continue
            elif li.name == 'li':
                for span in li.children:
                    if span.name == None:
                        pass
                    elif span.name == 'span':
                        text += span.text.strip()
                    elif span.name == 'br':
                        if self.text_translation_ul_insert_breaks_at_br == False:
                            text += "\n"
                    else:
                        print("GAEB Parser: Error in list element")
                
            else:
                print("GAEB Parser: Error in list element")
            text += "\n"
        return text
                

    def _parse_detail_text(self, textSoup: BeautifulSoup) -> str:
        text = ""
        # check 
        if textSoup.name is None:
            return text

        for child in textSoup.children:
            if child.name == None:
                pass
            elif child.name == 'Text':
                text += self._parse_detail_text(child)
                if  self.text_translation_insert_breaks_after_text:
                    text += "\n"
            elif child.name == 'span':  # finally found text
                text += child.text
            elif child.name == 'br' and  self.text_translation_insert_breaks_at_br:
                text += "\n"
            elif child.name == 'p':                 # segment is a paragraph 'p'
                text += self._parse_detail_text(child)
                if  self.text_translation_insert_breaks_after_paragraph:
                    text += "\n"
                
            elif child.name == 'TextComplement':  # segment is for bidder or owner inputs
                text += self._translate_text_supplement(child)
            elif child.name == 'ul':
                text += self._translate_ul(child)
            else:
                print(f"GAEB Parser: textelement {child.name} not translated")
                
        return text

    def _parse_complete_text(self, text_soup: BeautifulSoup):
        short_text = ""
        long_text = ""
        for child in text_soup.children:
            if child.name == None:
                pass
            elif child.name == 'DetailTxt':
                long_text = self._parse_detail_text(child)
            elif child.name == 'OutlineText':
                short_text = child.text.strip()
            elif child.name in ['ComplTSA', 'ComplTSB']:
                pass # text includes text complements -> parsed as text in parse_detail_text()
            else:
                print(f"GAEB Parser: In item '{text_soup.name}' text with name '{child.name}' not parsed")

        return short_text, long_text

    def _parse_gaeb(self, soup: BeautifulSoup):

        for child in soup.children:
            if child.name == None:
                pass
            elif child.name == 'GAEBInfo':
                pass
                # parse info about gaeb exporter
            elif child.name == 'PrjInfo':
                for subchild in child.children:
                    if subchild.name == None:
                        pass
                    elif subchild.name == 'NamePrj':
                        self.project_id = subchild.text.strip()
                    elif subchild.name == 'LblPrj':
                        self.project_name = subchild.text.strip()
                    else:
                        print(f"GAEB Parser: Subelement with name {subchild.name} in {child.name} not parsed")
                pass
                # parse info project details
            elif child.name == 'Award':
                self._parse_award(child)
            else:
                print(f"GAEB Parser: Element with name {child.name} of parent {soup.name} not parsed")
        return


    def _parse_award(self, soup: BeautifulSoup):
        for child in soup.children:
            if child.name == None:
                pass
            elif child.name in ['DP', 'AwardInfo', 'OWN']:
                pass
            elif child.name == 'AddText':
                self._parse_pretext(child)
            elif child.name == 'BoQ':
                self._parse_boq(child)
            else:
                print(f"GAEB Parser: Element with name {child.name} of item {soup.name} not parsed")

        # _parse_pretext() and _parse_boq() with subfunctions work on self.dict_list -> pack into df
        self._df = pd.DataFrame(self.dict_list, columns=['Projekt', 'OZ', 'Gewerk', 'Untergewerk', 'Kurztext', 'Qty', 'QU', 'TLK', 'Langtext'])
        

    def _parse_pretext(self, item_soup):
        pretext_short_text = item_soup.find('OutlineAddText').text.strip()
        detailAddText = item_soup.find('DetailAddText')
        pretext_long_text = self._parse_detail_text(detailAddText)

        result = {
            'Projekt': self.project_name,
            'OZ' : "-",
            'Gewerk': self.std_title[0],
            'Untergewerk' : self.std_title[1],
            'Kurztext' : pretext_short_text,
            'Qty': "",
            'QU': "",
            'TLK': "",
            'Langtext': pretext_long_text
        }
        self.dict_list.append(result)

    def _parse_boq(self, soup: BeautifulSoup):
        for child in soup.children:
            if child.name == None:
                pass
            elif child.name == 'BoQInfo':
                print("GAEB Parser: LV settings not parsed")
                pass
            elif child.name == 'BoQBody':
                self._parse_body(child)
            else:
                print(f"GAEB Parser: Element with name {child.name} of parent {soup.name} not parsed")


    def _parse_body(self, soup: BeautifulSoup, level=0):
        for child in soup.children:
            if child.name == None:
                pass
            elif child.name == 'Remark':        # remark at top level
                self._parse_item(child, level)
            elif child.name == 'BoQCtgy':       # A sub dir
                self.oz[level] = child['RNoPart']
                for subchild in child.children:
                    if subchild.name == None:
                        pass
                    elif subchild.name == 'LblTx':
                        self.title[level] = subchild.text.strip()
                        pass
                    elif subchild.name == 'BoQBody':
                        self._parse_body(subchild, level + 1)
                    else:
                        print(f"GAEB Parser: Subelement with name {subchild.name} in {child.name} not parsed")
            elif child.name == 'BoQInfo':       # info of sub dir
                pass
            elif child.name == 'Itemlist':      # items
                self._parse_item_list(child, level)
            else:
                print(f"GAEB Parser: Element with name {child.name} of parent {soup.name} not parsed")

    def _parse_item_list(self, soup: BeautifulSoup, level):
        for item in soup.children:
            if item.name == None:
                continue
            elif item.name in ['PerfDescr', 'Item', 'Remark', 'MarkupItem']:   # Hinweis, Beschreibungen, Positionen and Zuschlag all handled the same
                self._parse_item(item, level)

                # check if item has subitems
                subitems = item.find_all('SubDescr')
                for subitem in subitems:
                    self._parse_item(subitem, level + 1)

            else:
                print(f"GAEB Parser: Element with name {item.name} of itemlist {soup.name} not parsed")
                continue

        return
    
    def _parse_item(self, item_soup: BeautifulSoup, level):
        # parse header of item        
        try:
            item_id = item_soup['ID']
        except:
            item_id = ""

        try:
            rno_part = item_soup['RNoPart']
        except:
            rno_part = ""

        try:
            rno_index = item_soup['RNoIndex'] # sub indexes
            rno_part = rno_part + '.' + rno_index
        except:
            pass # no rno index

        # parse subitems
        qty = ""
        qu = ""
        langtext = ""
        textoutltxt = "(Positionslos)"
        tlk_text = ""

        for child in item_soup.children:
            if child.name == None:
                pass
            elif child.name == 'Qty':
                qty = child.text
            elif child.name == 'QtySpec': # used in subpositions, is always 'Yes'
                pass
            elif child.name == 'QU':
                qu = child.text
            elif child.name == 'Description':
                for subchild in child.children:
                    if subchild.name == None:
                        pass
                    elif subchild.name == 'CompleteText':
                        textoutltxt, langtext = self._parse_complete_text(subchild)
                    elif subchild.name == 'WICNo':
                        tlk_link = subchild.text
                        tlk_text = tlk_link.replace(" ", "")
                    else:
                        print(f"GAEB Parser: In item '{item_soup.name}' with id '{item_id}' text with name '{subchild.name}' not parsed")

            elif child.name == 'CompleteText': # for remarks
                textoutltxt, langtext = self._parse_complete_text(child)
            elif child.name == 'SubDescr':
                # print("GAEB Patser: Subelements not parsed")
                pass # get parsed later
            elif child.name == 'SubDNo': # used in subpositions, number of position
                subno = child.text
                rno_part = rno_part + '.' + subno
                pass
            else:
                print(f"GAEB Parser: In item '{item_soup.name}' with id '{item_id}' child with name '{child.name}' not parsed")

        # determine oz with saved ones
        if level == 0:
            oz_text = ""
        elif level == 1:
            oz_text = self.oz[0] + '.' + self.oz[1]
        elif level == 2:
            self.oz[2] = rno_part
            oz_text = self.oz[0] + '.' + self.oz[1] + '.' + self.oz[2]
        elif level == 3:
            oz_text = self.oz[0] + '.' + self.oz[1] + '.' + self.oz[2] + rno_part
        else:
            print(f"GAEB Parser: Level {level} not used")

        # pack and save
        parsed_dict = ({
            'Kurztext' : textoutltxt,
            'Qty': qty,
            'QU': qu,
            'TLK': tlk_text,
            'Langtext': langtext,
            'Projekt': self.project_name,
            'OZ': oz_text,
            'Gewerk': self.title[0],
            'Untergewerk': self.title[1],
            })
            
        self.dict_list.append(parsed_dict)

        return
    

