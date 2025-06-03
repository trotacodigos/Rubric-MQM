from evaluator import base


class Template(base.BaseTemplate):
    """EAPrompt"""
    def __init__(self):
        super().__init__()
        self.structure = "{instruction}\n{segment}\n\n{criteria}"
        
    @property
    def instruction(self):
        if self.with_ref:
            ref_part = " and reference"
        else:
            ref_part = ""

        return (f"Based on the given source{ref_part}, identify the major and minor "
                "errors in this segment. Use the template above to answer the following question:")
        
    @property
    def language_segments(self):
        line = (
            "Source: {source_seg}\n"
            "Translation: {target_seg}"
        )
        if self.with_ref:
            line += "\nReference: {reference_seg}"
        return line
    
                           
    @property
    def severity_line(self):
        return ("Note that Major errors refer to actual translation or grammatical "
                "errors, and Minor errors refer to smaller imperfections, and purely "
                "subjective opinions about the translation.")        

    
    
class Prompt(base.BasePrompt):

    def __init__(self,
                 source_lang: str,
                 target_lang: str,
                 source_seg: str,
                 target_seg: str,
                 reference_seg: str,
                 scale=None,):
        super().__init__(
            source_lang=source_lang,
            target_lang=target_lang,
            source_seg=source_seg,
            target_seg=target_seg,
            reference_seg=reference_seg,)
        self.system_prompt = None
        self.with_ref = True
        self.template_obj = Template(self.with_ref)
        
    def generate_message(self, icl_examples: dict):
        messages = []
        if icl_examples is not None: # oneshot
            for sentence, example in icl_examples.items():
                messages.extend([
                    {
                        'role': 'user',
                        'content': sentence,
                    },
                    {
                        'role': 'assistant',
                        'content': example,
                    }
                ])
        # instruction:
        messages.append(
            {
                'role': 'user',
                'content': self.create(self.template_obj)
            }
        )
        return messages
    
    def generate_examples(self):
        assert self.source_lang in ('English', 'Chinese'), "Do not support the source language!"
        assert self.target_lang in ('German', 'English'), "Do not support the target language!"
        
        lang_pair = {'English': 'en', 'Chinese': 'zh', 'German': 'de'}
        src_lang = lang_pair.get(self.source_lang)
        tgt_lang = lang_pair.get(self.target_lang)
        
        obj = base.ICLExample(with_ref=True,
                              source_lang=self.source_lang,
                              target_lang=self.target_lang,)
        
        # ZHEN
        obj.source_seg = ("中新网北京9月27日电 (记者 杜燕)为加强节前市场监管执法，"
                          "北京市市场监管局在国庆节前 夕检查各类经营主体2000余户。")
        obj.target_seg = ("<v>BEIJING</v>, Sept. 27 (Reporter Du Yan) In order to "
                       "strengthen market <v>supervision</v> and law enforcement before "
                       "the <v>festival</v>, the <v>Beijing Municipal Market Supervision "
                       "Bureau</v> inspected more than 2,000 <v>households of various</v> "
                       "business <v>subjects</v> on the eve of the National Day.")
        obj.reference_seg = ("Chinanews.com Report on September 27 in Beijing (Journalist "
                       "Du Yan) The Beijing Administration for Market Regulation inspected "
                       "more than 2,000 operating entities of different types before the "
                       "National Day holiday to strengthen pre-holiday market regulation "
                       "and law enforcement.")
        
        zhen = obj.create(self.template_obj)
        zhen_example = ("Major errors:\n"
                        "(1) “BEIJING” – Omission\n"
                        "(2) “subjects” – Mistranslation\n"
                        "Minor errors:\n"
                        "(1) “households of various” – Mistranslation\n"
                        "(2) “festival” – Mistranslation\n"
                        "(3) “supervision” – Mistranslation\n"
                        "(4) “Beijing Municipal Market Supervision Bureau” – Inappropriate for context\n"
                        #"(5) “BEIJING” – Spelling)"
                       )
        
        # ENDE
        obj.source_lang = ("They were addressed to her son, who has autism and lives in a private care "
                        "facility, she said. But instead of her son's name inside when you opened them,"
                        "the letters said Dear Maine's Department of Health and Human Services -- in "
                        "Cincinnati, she told local media.")
        obj.target_seg = ("<v>Sie</v> <v>wurden</v> an ihren Sohn gerichtet, der Autismus hat und in "
                        "einer privaten Pflegeeinrichtung lebt, sagte sie. Aber anstelle des Namens "
                        "ihres Sohnes <v>im Inneren</v>, als Sie sie öffneten, <v>sagten</v> die "
                        "<v>Briefe</v> <v>Dear Maine 's Department of Health and Human Services</v> "
                        "-- in Cincinnati, sagte sie den lokalen Medien.")
        obj.reference_seg = ("Sie seien an ihren Sohn adressiert, der an Autismus leidet und in einer privaten"
                        "Pflegeeinrichtung lebt, sagte sie. Aber als Sie die Briefe öffnete, stand "
                        "darin nicht der Name ihres Sohnes, sondern sie waren an das Gesundheitsministerium "
                        "von Maine gerichtet, in Cincinnati, wie sie den lokalen Medien sagte.")
        ende = obj.create(self.template_obj)
        ende_example = ("Major errors:\n"
                        "(1) “Sie” – Mistranslation\n"
                        "(2) “Dear Maine 's Department of Health and Human Services” – Untranslated text\n"
                        "Minor errors:\n"
                        "(1) “sagten” – Mistranslation\n"
                        "(2) “im Inneren” – Mistranslation\n"
                        "(3) “Briefe ,,” – Omission\n"
                        "(4) “wurden” – Grammar\n"
                        #"(5) “im Inneren, als Sie sie öffneten, sagten die Briefe” – Awkward Style\n"
                       )
        data = {'ende': {'sentence': ende, 'example': ende_example},
               'zhen': {'sentence': zhen, 'example': zhen_example}}
            
        return data.get(src_lang + tgt_lang)
    