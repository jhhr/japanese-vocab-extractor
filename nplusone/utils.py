import re

def escapeText(text):
    # strip characters that trip up kakasi/mecab
    text = text.replace("\n", " ")
    text = text.replace(r'\uff5e', "~")
    # removed strip html
    text = re.sub("<br( /)?>", "---newline---", text)
    text = text.replace("---newline---", "<br>")
    return text
