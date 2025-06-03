from evaluator.slot_scenarios.gemba import DefaultPrompt
    
    
class Prompt(DefaultPrompt):
    
    _shot_map = {
        'ende': {
            'source_seg': ("I do apologise about this, we must gain permission from <v>the "
                    "account holder</v> to discuss an order with another person, I "
                    "apologise if this was done previously, however, I would not be able "
                    "to discuss this with yourself without the account holders permission."),
            'target_seg': ("Ich entschuldige mich dafür, wir müssen die Erlaubnis "
                    "einholen, um eine Bestellung mit einer anderen Person zu besprechen. Ich "
                    "entschuldige mich, falls dies zuvor geschehen <v>wäre</v>, aber ohne die Erlaubnis "
                    "des Kontoinhabers wäre ich nicht in der Lage, dies mit <v>dir</v> "
                    "<v>involvement</v> <v>permission</v>."),
            'answer': ("MQM annotations:\n"
                     "Critical:\n"
                     "no-error\n"
                     "Major:\n"
                     "mistranslation - \"involvement\"\n"
                     "punctuation - \";\"\n"
                     "omission - \"the account holder\"\n"
                     "untranslated text - \"permission\"\n"
                     "Minor:\n"       
                     "grammar - \"wäre\"\n"),
        },
        'encz': {
            'source_seg': ("Talks have resumed in Vienna to <v>trying</v> to revive the "
                        "nuclear pact, with both sides trying to gauge the prospects of success after the "
                        "latest exchanges in <v>the stop-start</v> negotiations."),
            'target_seg': ("Ve Vídni se <v>ve Vídni</v> obnovily rozhovory o oživení jaderného "
                        "paktu, přičemž obě <v>partaje</v> se snaží posoudit vyhlídky na úspěch "
                        "po posledních výměnách v jednáních."),
            'answer': ("MQM annotations:\n"
                       "Critical:\n"
                       "source issue - \"trying\"\n"
                       "Major:\n"
                       "addition - \"ve Vídni\"\n"
                       "omission - \"the stop-start\"\n"
                       "Minor:\n"
                       "terminology - \"partaje\"\n"),
        },
        'zhen': {
            'source_seg': ("大众点评乌鲁木齐家居卖场频道为您提供高铁居然之家地址，"
                        "电话，营业时间等最新商户信息， 找装修公司，就上大众点评"),
            'target_seg': ("Urumqi Home Furnishing Store Channel provides <v>with you</v> the latest "
                       "business information such as the address, telephone number, business "
                       "hours, <v>etc.,</v> <v>of high-speed rail</v>, and find a decoration "
                       "<v>incorporation</v>, and <v>go to the reviews</v>."),
            'answer': ("MQM annotations:\n"
                       "Critical:\n"
                       "addition - \"of high-speed rail\"\n"
                       "Major:\n"
                       "mistranslation - \"go to the reviews\"\n"
                       "Minor:\n"
                       "incorrect word order - \"with you\""
                       "inconsistency - \"incorporation\"")
        }
    
    }
    
    def set_icl_examples(self):
        examples = DefaultPrompt.set_icl_examples()
        for lang, ex in examples.items():
            this_map = self._shot_map[lang]
            ex.source_seg = this_map['source_seg']
            ex.target_seg = this_map['target_seg']
            ex.answer = this_map['answer']
        return examples
    
    @property
    def icl_examples(self):
        return {lang: ex.prompt_lines for lang, ex in self.set_icl_examples().items()}