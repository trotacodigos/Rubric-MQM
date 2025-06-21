from rubric_mqm.slot_scenarios import deepcat, deepshot


class Prompt(deepcat.Prompt):
    
    _shot_map = deepshot.Prompt._shot_map
    
    def set_icl_examples(self):
        examples = deepcat.Prompt.set_icl_examples()
        for lang, ex in examples.items():
            this_map = self._shot_map[lang]
            ex.source_seg = this_map['source_seg']
            ex.target_seg = this_map['target_seg']
            ex.answer = this_map['answer']
        return examples
    
    @property
    def icl_examples(self):
        return {lang: ex.prompt_lines for lang, ex in self.set_icl_examples().items()}