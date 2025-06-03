from evaluator.slot_scenarios import deeprubric
from typing import Optional


class RubricMQMTemplate(deeprubric.Template):
    def __init__(self, with_ref=False):
        super().__init__(with_ref=with_ref, scale=100)
    

class RubricMQMPrompt(deeprubric.Prompt):
    def __init__(self,
                 source_lang: str,
                 target_lang: str,
                 source_seg: str,
                 target_seg: str,
                 reference_seg: Optional[str] = None,
                ):
        super().__init__(
            scale=100,
            source_lang=source_lang,
            target_lang=target_lang,
            source_seg=source_seg,
            target_seg=target_seg,
            reference_seg=reference_seg,
        )
        self.template_obj = RubricMQMTemplate(self.with_ref)

