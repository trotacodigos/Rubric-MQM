from rubric_mqm.slot_scenarios import deeprubric


class Template(deeprubric.Template):
    """
    Severity-based template class with support for 4, 8, or 100-point evaluation scales.
    """

    _sqm_map = {
        4: (
            "Evaluate the severity of each error on a scale from 1 to 4:\n"
            "1 - Minimal error with no impact on clarity.\n"
            "2 - Minor alteration with limited effect.\n"
            "3 - Noticeable impact on comprehension.\n"
            "4 - Significant error that substantially distorts the message."
        ),
        8: (
            "Evaluate the severity of each error on a scale from 1 to 8:\n"
            "1 - No impact on comprehension or intent.\n"
            "3 - Somewhat affects clarity while intent remains clear.\n"
            "5 - Affects understanding and partially alters intent.\n"
            "8 - Makes the translation unfaithful and misleading."
        ),
        100: (
            "Evaluate the severity of each error on a continuous scale from 1 to 100:\n"
            "10 - Negligible impact; message intact.\n"
            "30 - Minimal effect on clarity.\n"
            "50 - Affects clarity; some interpretation needed.\n"
            "70 - Substantial misunderstanding.\n"
            "90 - Serious miscommunication; intent lost.\n"
            "100 - Translation completely unfaithful and misleading."
        )
    }

    @property
    def severity_line(self):
        """
        Returns the appropriate severity description based on the defined scale.
        """
        return self._sqm_map.get(self.scale, "Invalid severity scale.")

    def create(self) -> str:
        """
        Generates full rubric-based prompt including rubric and classification criteria.
        """
        return self.structure.format(
            segment=super().language_segments,
            instruction=super().instruction,
            criteria=super().category_line + "\n\n" + self.severity_line + (
                "\n\nReturn the result as a Python dictionary with error span as keys "
                "and a dictionary of error category and severity as values.")
        )
    

class Prompt(deeprubric.Prompt):
    """
    Prompt class using the customized Template with scale-based severity description.
    """

    def __init__(self,
                 scale: int,
                 source_lang: str,
                 target_lang: str,
                 source_seg: str,
                 target_seg: str,
                 reference_seg=None):
        super().__init__(
            scale=scale,
            source_lang=source_lang,
            target_lang=target_lang,
            source_seg=source_seg,
            target_seg=target_seg,
            reference_seg=reference_seg,
        )
        self.template_obj = Template(self.scale)
        
    def set_icl_examples(self):
        examples = super().set_icl_examples()
        for lang, ex in examples.items():
            ex.prompt_cls = Prompt
        return examples