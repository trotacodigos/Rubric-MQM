from rubric_mqm import base
from rubric_mqm.slot_scenarios.gemba import DefaultPrompt

from typing import Optional, Dict, Type
from functools import cached_property


class Template(base.BaseTemplate):
    """
    MQM-style rubric template with a numerical severity scale.

    [Scale of Error Severity]
    {severity rubric}
    
    [Instruction]
    {source} segment
    {translation} segment

    {instruction}
    
    {assistant}

    """
    
    # Static rubric definitions for efficiency
    _rubric_map = {
        4: (
            "Scale 1: Slight wording change with no impact on clarity or intent.\n"
            "Scale 2: Alters wording but message and intent remain mostly clear.\n"
            "Scale 3: Noticeable impact on comprehension; may slightly distort intent.\n"
            "Scale 4: Substantial distortion; translation is unfaithful and potentially misleading.\n"
        ),
        8: (
            "Scale 1: No impact on comprehension or intent.\n"
            "Scale 2: Slight alteration of wording; message intact.\n"
            "Scale 3: Some impact on clarity; intent remains clear.\n"
            "Scale 4: Clarity affected; message slightly distorted.\n"
            "Scale 5: Understanding impaired; intent partially altered.\n"
            "Scale 6: Meaning distorted; clarity compromised.\n"
            "Scale 7: Substantial misinterpretation of message and intent.\n"
            "Scale 8: Translation is unfaithful and misleading.\n"
        ),
        100: (
            "10: Negligible impact; intent remains fully intact.\n"
            "20: Minor wording issue; message preserved.\n"
            "30: Slight clarity issue; intent is clear.\n"
            "40: Slight misunderstanding possible, but message understood.\n"
            "50: Affects clarity; some interpretation needed.\n"
            "60: Distorts part of the message; ambiguous intent.\n"
            "70: Alters message significantly; misunderstanding likely.\n"
            "80: Core meaning is misinterpreted.\n"
            "90: Serious miscommunication; original intent lost.\n"
            "100: Translation is misleading and completely unfaithful."
        )
    }

    def __init__(self, scale: int, with_ref=False):
        super().__init__(with_ref)
        if scale not in (4, 8, 100):
            raise ValueError(f"Invalid scale: {scale}. Choose from 4, 8, or 100.")
        self.scale = scale

    @property
    def severity_line(self):
        """
        Overrides BaseTemplate severity_line with numerical rubric.
        """
        return (
            f"Evaluate the severity of each error on a scale from 1 to {self.scale}, "
            "following the rubric below."
        )

    @property
    def rubric_lines(self) -> str:
        """
        Returns the rubric lines based on the specified severity scale.
        """
        rubric = self._rubric_map[self.scale]
        return f"Outlined below is the definition for the severity scale:\n{rubric}"

    def create(self) -> str:
        """
        Generates full rubric-based prompt including rubric and classification criteria.
        """
        return self.structure.format(
            segment=self.rubric_lines + "\n\n" + super().language_segments,
            instruction=super().instruction,
            criteria=super().category_line + "\n\n" + self.severity_line + (
                "\n\nReturn the result as a Python dictionary with error span as keys "
                "and a dictionary of error category and severity as values.")
        )
        


class Prompt(DefaultPrompt):
    """
    A scale-controlled prompt wrapper for RubricMQMPrompt.
    
    Args:
        scale (int): Maximum score used in MQM annotation (4, 8, or 100).
    """

    _scaled_answer_map = {
            4: {
                'ende': (
                    "MQM annotations:\n"
                    "\"involvement\" - mistranslation - 4\n"
                    "\"the account holder\" - omission - 3\n"
                    "\"wäre\" - grammar - 2\n"),
                'encz': (
                    "MQM annotations:\n"
                    "\"ve Vídni\" - addition - 3\n"
                    "\"the stop-start\" - omission - 2\n"
                    "\"partaje\" - terminology - 1\n"),
                'zhen': (
                    "MQM annotations:\n"
                    "\"of high-speed rail\" - addition - 4\n"
                    "\"go to the reviews\" - mistranslation - 3\n")
            },
            8: {
                'ende': (
                    "MQM annotations:\n"
                    "\"involvement\" - mistranslation - 7\n"
                    "\"the account holder\" - omission - 6\n"
                    "\"wäre\" - grammar - 3\n"),
                'encz': (
                    "MQM annotations:\n"
                    "\"ve Vídni\" - addition - 6\n"
                    "\"the stop-start\" - omission - 5\n"
                    "\"partaje\" - terminology - 1\n"),
                'zhen': (
                    "MQM annotations:\n"
                    "\"of high-speed rail\" - addition - 8\n"
                    "\"go to the reviews\" - mistranslation - 6\n")
            },
            100: {
                'ende': (
                    "MQM annotations:\n"
                    "\"involvement\" - mistranslation - 73\n"
                    "\"the account holder\" - omission - 59\n"
                    "\"wäre\" - grammar - 42\n"),
                'encz': (
                    "MQM annotations:\n"
                    "\"ve Vídni\" - addition - 87\n"
                    "\"the stop-start\" - omission - 68\n"
                    "\"partaje\" - terminology - 34\n"),
                'zhen': (
                    "MQM annotations:\n"
                    "\"of high-speed rail\" - addition - 93\n"
                    "\"go to the reviews\" - mistranslation - 88\n")
            }
        }
    
    def __init__(self,
                 scale: int,
                 source_lang: str,
                 target_lang: str,
                 source_seg: str,
                 target_seg: str,
                 reference_seg: Optional[str] = None):
        if scale not in (4, 8, 100):
            raise ValueError(f"Invalid scale: {scale}. Must be 4, 8, or 100.")
        super().__init__(
            source_lang=source_lang,
            target_lang=target_lang,
            source_seg=source_seg,
            target_seg=target_seg,
            reference_seg=reference_seg,
        )
        self.scale = scale
        self.template_obj = Template(self.scale)

    
    def set_icl_examples(self) -> Dict[str, base.ICL_Example]:
        """
        Returns modified few-shot ICL examples with scale and answer injected.
        """
        examples = super().set_icl_examples()
        for lang, ex in examples.items():
            ex.prompt_cls = Prompt
            ex.scale = self.scale
            ex.answer = self._scaled_answer_map[self.scale][lang]
        return examples

    @cached_property
    def icl_examples(self) -> Dict[str, Dict[str, str]]:
        """
        Returns ICL examples formatted as prompt lines.
        """
        return {lang: ex.prompt_lines for lang, ex in self.set_icl_examples().items()}