from rubric_mqm import base
from typing import Optional, Dict


class DefaultTemplate(base.BaseTemplate):
    """GEMBA-MQM"""
    @property
    def category_line(self):
        return ("The categories of errors are: accuracy (addition, mistranslation, omission, "
                "untranslated text), fluency (grammar, inconsistency, punctuation), "
                "source issue, incorrect word order, terminology (inappropriate for context, "
                "inconsistent use), or no-error.")
    


class DefaultPrompt(base.BasePrompt):
    _answer_map = {
            'ende': (
                "MQM annotations:\n"
                "Critical:\nno-error\n"
                "Major:\naccuracy/mistranslation - \"involvement\"\n"
                "accuracy/omission - \"the account holder\"\n"
                "Minor:\nfluency/grammar - \"wäre\"\n"
            ),
            'encz': (
                "MQM annotations:\n"
                "Critical:\nno-error\n"
                "Major:\naccuracy/addition - \"ve Vídni\"\n"
                "accuracy/omission - \"the stop-start\"\n"
                "Minor:\nterminology/inappropriate for context - \"partaje\"\n"
            ),
            'zhen': (
                "MQM annotations:\n"
                "Critical:\naccuracy/addition - \"of high-speed rail\"\n"
                "Major:\naccuracy/mistranslation - \"go to the reviews\"\n"
                "Minor:\nno-error\n"
            )
        }
    
    def __init__(self,
                 source_lang: str,
                 target_lang: str,
                 source_seg: str,
                 target_seg: str,
                 reference_seg: Optional[str] = None,
                 scale=None,):
        super().__init__(
            source_lang=source_lang,
            target_lang=target_lang,
            source_seg=source_seg,
            target_seg=target_seg,
            reference_seg=reference_seg,
            has_shot=True,
        )
        self.scale = None
        self.template_obj = DefaultTemplate(self.with_ref)

    def generate_message(self):
        return super().generate_message(self.icl_examples)
    
    @property
    def icl_examples(self) -> Dict[str, str]:
        """Returns only the prompt lines from ICL examples."""
        return {lang: ex.prompt_lines for lang, ex in DefaultPrompt.set_icl_examples().items()}

    @classmethod
    def set_icl_examples(cls) -> Dict[str, base.ICL_Example]:
        """Returns few-shot examples keyed by language pair."""
        return {
            'ende': base.ICL_Example(
                prompt_cls=cls,
                source_lang='English',
                target_lang='German',
                source_seg=(
                    "I do apologise about this, we must gain permission from <v>the "
                    "account holder</v> to discuss an order with another person, I "
                    "apologise if this was done previously, however, I would not be able "
                    "to discuss this with yourself without the account holder’s permission."
                ),
                target_seg=(
                    "Ich entschuldige mich dafür, wir müssen die Erlaubnis einholen, um "
                    "eine Bestellung mit einer anderen Person zu besprechen. Ich entschuldige "
                    "mich, falls dies zuvor geschehen <v>wäre</v>, aber ohne die Erlaubnis "
                    "des Kontoinhabers wäre ich nicht in der Lage, dies mit <v>dir</v> "
                    "<v>involvement</v>."
                ),
                answer=cls._answer_map['ende']
            ),
            'encz': base.ICL_Example(
                prompt_cls=cls,
                source_lang='English',
                target_lang='Czech',
                source_seg=(
                    "Talks have resumed in Vienna to try to revive the nuclear pact, "
                    "with both sides trying to gauge the prospects of success after the "
                    "latest exchanges in <v>the stop-start</v> negotiations."
                ),
                target_seg=(
                    "Ve Vídni se <v>ve Vídni</v> obnovily rozhovory o oživení jaderného "
                    "paktu, přičemž obě <v>partaje</v> se snaží posoudit vyhlídky na úspěch "
                    "po posledních výměnách v jednáních."
                ),
                answer=cls._answer_map['encz']
            ),
            'zhen': base.ICL_Example(
                prompt_cls=cls,
                source_lang='Chinese',
                target_lang='English',
                source_seg=(
                    "大众点评乌鲁木齐家居卖场频道为您提供高铁居然之家地址，"
                    "电话，营业时间等最新商户信息， 找装修公司，就上大众点评"
                ),
                target_seg=(
                    "Urumqi Home Furnishing Store Channel provides you with the latest "
                    "business information such as the address, telephone number, business "
                    "hours, <v>etc.,</v> <v>of high-speed rail</v>, and find a decoration "
                    "company, and <v>go to the reviews</v>."
                ),
                answer=cls._answer_map['zhen']
            )
        }

    