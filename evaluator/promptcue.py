
def create_cue(template: object):
    """Add instructions to the prompt"""
    template.structure = template.structure.replace("{instruction}", 
                    "{instruction} They are enclosed with <v> and </v> tags. DO NOT report tag errors.")
    return template


def remove_tag_from_content(messages: list) -> list:
    new_messages = []
    for message in messages:
        content = message.get('content')
        if content:
            message["content"] = content.replace("<v>", "").replace("</v>", "")
        new_messages.append(message)
    return new_messages
            