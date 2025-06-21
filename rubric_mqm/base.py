from typing import Optional, Dict, Any, Type
from dataclasses import dataclass


class BaseTemplate:
    """
    Template for evaluating translation quality with or without a reference segment.

    Structure:
    {source} segment
    {translation} segment
    *{reference} segment (optional)
    
    {instruction}
    
    {assistant}
    """

    def __init__(self, with_ref=False):
        self.with_ref = with_ref
        self.structure = "{segment}\n\n{instruction}\n\n{criteria}"

    @property
    def instruction(self):
        """
        Returns the evaluation instruction based on whether reference is included.
        """
        ref_part = ", reference," if self.with_ref else ""
        return (
            f"Based on the source{ref_part} and machine translation segments "
            "enclosed in triple backticks, identify and classify the types of translation errors."
        )

    @property
    def language_segments(self):
        """
        Returns the segment structure depending on reference inclusion.
        """
        lines = (
            "{source_lang} source: ```{source_seg}```\n"
            "{target_lang} translation: ```{target_seg}```"
        )
        if self.with_ref:
            lines += "\n{target_lang} reference: ```{reference_seg}```"
        return lines

    @property
    def category_line(self):
        """
        Lists predefined error categories.
        """
        return (
            "The categories of errors are: addition, mistranslation, omission, "
            "untranslated text, grammar, inconsistency, punctuation, source issue, "
            "incorrect word order, terminology (inappropriate for context, inconsistent "
            "use), or no-error, according to the provided definitions."
        )

    @property
    def severity_line(self):
        """
        Describes severity levels for translation errors.
        """
        return (
            "Each error must be classified as critical, major, or minor:\n"
            "- Critical: Inhibits comprehension.\n"
            "- Major: Disrupts flow but meaning is understandable.\n"
            "- Minor: Noticeable but does not affect comprehension or flow."
        )

    def create(self) -> str:
        """
        Combines all sections into the full evaluation prompt.
        """
        return self.structure.format(
            segment=self.language_segments,
            instruction=self.instruction,
            criteria=self.category_line + "\n\n" + self.severity_line
        )


class BasePrompt:
    def __init__(self,
                 *,
                 source_lang: str,
                 target_lang: str,
                 source_seg: str,
                 target_seg: str,
                 reference_seg: Optional[str] = None,
                 system_prompt: Optional[str] = None,
                 has_shot: bool = True,
                 scale: int = None,
                ):
        """
        Initialize a prompt generator for MT quality evaluation.

        Args:
            source_lang (str): Source language code or name.
            target_lang (str): Target language code or name.
            source_seg (str): Source segment string.
            target_seg (str): Target segment string.
            reference_seg (str, optional): Human reference translation (optional).
            system_prompt (str, optional): Instruction prompt for the system role.
            has_shot (bool): Whether to include few-shot examples.
        """
        self.system_prompt = system_prompt or (
            "You are an annotator for the quality of machine translation. "
            "Your task is to identify errors and assess their influence "
            "on the quality of the translation."
        )

        self.with_ref = reference_seg is not None
        self.template_obj = BaseTemplate(self.with_ref)
        self.has_shot = has_shot
        self.scale = scale
        self.params = {
            'source_lang': source_lang,
            'target_lang': target_lang,
            'source_seg': source_seg,
            'target_seg': target_seg,
            'reference_seg': reference_seg or None,
        }

    def generate_message(self, shot_dic: Optional[Dict[str, Dict[str, str]]] = None) -> list[dict[str, str]]:
        """
        Generate a sequence of messages to send to a language model.

        Args:
            shot_dic (dict, optional): Few-shot examples in {'example_id': {'question': str, 'answer': str}} format.

        Returns:
            list: List of message dicts with roles and content.
        """
        messages = [{'role': 'system', 'content': self.system_prompt}]

        if self.has_shot and shot_dic:
            for example in shot_dic.values():
                messages.append({'role': 'user', 'content': example['question']})
                messages.append({'role': 'assistant', 'content': example['answer']})

        messages.append({'role': 'user', 'content': self.create_prompt()})
        return messages

    def create_prompt(self) -> str:
        """
        Create the main prompt using the selected template and parameters.

        Returns:
            str: Prompt string formatted with language/segment parameters.
        """
        try:
            template = self.template_obj.create()
            return template.format(**self.params)
        except KeyError as e:
            raise ValueError(f"Missing parameter for prompt formatting: {e}")
    


@dataclass
class ICL_Example:
    prompt_cls: Type  # Class, not instance
    source_lang: str
    target_lang: str
    source_seg: str
    target_seg: str
    answer: str
    scale: Optional[int] = None

    @property
    def prompt_lines(self) -> Dict[str, str]:
        """
        Returns a dictionary with 'question' and 'answer' for few-shot ICL formatting.

        The 'question' is generated from the associated prompt class by instantiating it
        with language segments and an optional severity scale.
        """
        # Dynamically check for scale parameter in class signature
        kwargs = {
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
            "source_seg": self.source_seg,
            "target_seg": self.target_seg
        }
        if self.scale is not None:
            kwargs["scale"] = self.scale

        obj = self.prompt_cls(**kwargs)
        return {
            "question": obj.create_prompt(),
            "answer": self.answer
        }