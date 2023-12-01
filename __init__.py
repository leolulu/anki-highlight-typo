import re
import threading

from anki.notes import Note
from aqt import gui_hooks

from .highlight_word_rule import complex_rules, simple_rules
from .spellchecker import SpellChecker
from .utils import StopwordsManager

spell_checker = SpellChecker(language="en")
sm = StopwordsManager()


def highlight_entry(changed: bool, note: Note, current_field_idx: int):
    field_names = note.keys()
    if "释义例句等详细内容" in field_names:
        if field_names[current_field_idx] not in ["单词", "释义例句等详细内容", "来源例句"]:
            return False
    if_changed_wrong = highlight_wrong(note, current_field_idx)
    if_changed_word = highlight_word(note, current_field_idx)
    return if_changed_word or if_changed_wrong


def highlight_word_impl(word_value_provided, content, if_changed):
    content_data_to_use = content
    content_data_to_use = content_data_to_use.replace(r"<br>", " ")
    content_data_to_use = re.sub(r"<span .*?<\/span>", "", content_data_to_use)
    word_values = re.findall(word_value_provided, content_data_to_use, re.IGNORECASE)
    for word_value in set(word_values):
        if_changed = True
        print(f"highlight word: {word_value}")
        highlighted_word = f'<span style="color: rgb(219, 147, 23);">{word_value}</span>'
        content = content.replace(word_value, highlighted_word)
    return if_changed, content


def highlight_word(note: Note, current_field_idx: int):
    note_items = dict(note.items())
    if "单词" not in note_items:
        return False
    if note.keys()[current_field_idx] != "释义例句等详细内容":
        return False
    word_value = note_items["单词"]
    if_changed = False
    content = note.fields[current_field_idx]

    for deformer in simple_rules:
        if_changed, content = highlight_word_impl(deformer(word_value), content, if_changed)

    for complex_rule in complex_rules:
        conditioner, deformers = complex_rule
        if conditioner(word_value):
            for deformer in deformers:
                if_changed, content = highlight_word_impl(deformer(word_value), content, if_changed)

    if_changed, content = highlight_word_impl(word_value, content, if_changed)
    note.fields[current_field_idx] = content
    return if_changed


def highlight_wrong(note: Note, current_field_idx: int):
    if_changed = False
    content = note.fields[current_field_idx]
    content_data_to_use = content
    content_data_to_use = content_data_to_use.replace(r"<br>", " ")
    content_data_to_use = re.sub(r"<u .*?<\/u>", "", content_data_to_use)
    words = re.split(r"[ ,\.\/']", content_data_to_use)
    words = [i for i in words if re.search(r"^[a-zA-Z]*$", i)]
    words = [i for i in words if len(i) >= 3]
    words = [i for i in words if i != ""]
    misspelled_words = spell_checker.unknown(words)
    misspelled_words = [i for i in misspelled_words if i not in sm.stopwords]
    threading.Thread(target=sm.extend_stopwords).start()
    for word in misspelled_words:
        if_changed = True
        print(f"Typo found: {word}")
        highlighted_word = f'<u style="text-decoration-style: wavy; text-decoration-color: red; text-decoration-thickness: 1px;">{word}</u>'
        content = content.replace(word, highlighted_word)
    for result in re.findall(r"(<u .*?>(.*?)<\/u>)", content):
        whole_part, word = result
        print(f"[DEBUG]check if right: {word}")
        wrong_words = spell_checker.unknown([word])
        if not wrong_words:
            if_changed = True
            content = content.replace(whole_part, word)
    note.fields[current_field_idx] = content
    return if_changed


gui_hooks.editor_did_unfocus_field.append(highlight_entry)
