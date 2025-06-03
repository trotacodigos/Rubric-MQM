from evaluator import base
from evaluator.slot_scenarios.gemba import DefaultTemplate, DefaultPrompt


class Template(DefaultTemplate):
    """
    Extended Template class that appends detailed category definitions
    to the base category line.
    """

    @property
    def category_line(self) -> str:
        """
        Combines base category labels with detailed definitions.
        """
        base_obj = base.BaseTemplate(self.with_ref)
        return base_obj.category_line + '\n\n' + self.category_definition

    @property
    def category_definition(self) -> str:
        """
        Returns detailed explanations for each error category.
        """
        definitions = {
            "Addition": (
                "Extra content not in the original text that introduces repetition, "
                "unnecessary details, or redundancy. It may distort the message and confuse readers."
            ),
            "Mistranslation": (
                "Inaccurate translation or misinterpretation due to poor word choice. "
                "It alters the original meaning and intent."
            ),
            "Omission": (
                "Missing essential elements from the source text, leading to loss of meaning, "
                "context, or nuance required for full comprehension."
            ),
            "Untranslated text": (
                "Portions of the source language remain in the translation, resulting in an incomplete rendering."
            ),
            "Grammar": (
                "Incorrect usage of grammar such as tense, verb form, pronouns, agreement, or articles, "
                "which disrupts fluency or comprehension."
            ),
            "Inconsistency": (
                "Variations in tone, structure, or terminology that undermine the fluency or coherence of the text."
            ),
            "Punctuation": (
                "Errors in punctuation, prepositions, quotation marks, or hyphenation that impair clarity and flow."
            ),
            "Source issue": (
                "Ambiguities or errors in the source text (e.g., unclear phrasing) that hinder accurate translation."
            ),
            "Incorrect word order": (
                "Deviation from natural or logical word order, leading to confusion or altered emphasis."
            ),
            "Terminology": (
                "Inappropriate or inconsistent use of technical or specialized terms that misrepresent meaning or context."
            ),
            "No-error": (
                "Flawless translation preserving meaning, tone, style, and grammatical correctness."
            )
        }

        return '\n'.join(
            f"{category}: {description}" for category, description in definitions.items()
        )

    
class Prompt(DefaultPrompt):
    def __init__(self,
                 source_lang: str,
                 target_lang: str,
                 source_seg: str,
                 target_seg: str,
                 reference_seg=None,
                 scale=None,):
        super().__init__(
            source_lang=source_lang,
            target_lang=target_lang,
            source_seg=source_seg,
            target_seg=target_seg,
            reference_seg=reference_seg)
        self.template_obj = Template(self.with_ref)