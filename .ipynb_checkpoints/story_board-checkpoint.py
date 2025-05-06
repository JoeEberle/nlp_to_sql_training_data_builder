from IPython.display import Markdown, display, Image
def clean_string(input_string):
    input_string = input_string.replace("‐", " ")  # replace minus signs with blank
    input_string = input_string.replace("﴾", "(")  # squiggle parenthesis with parenthesis 
    input_string = input_string.replace("﴿", ")")  # squiggle parenthesis with parenthesis     

    unwanted_chars = '"\'‐-–:/“”‘’'  # Add any other quote-like or minus/dash characters
    translation_table = str.maketrans('', '', unwanted_chars)

    cleaned_string = input_string.translate(translation_table)
    return cleaned_string


def outmd(definition, file_name = 'storyboard.md'):
    definition = clean_string(definition) 
    with open(file_name, 'a', encoding='utf-8') as f:
        f.write(definition)  
    display(Markdown(definition))
        

