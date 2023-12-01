import re
import threading
import urllib.request

from anki.notes import Note
from aqt import gui_hooks

from .spellchecker import SpellChecker
import re

spell_checker = SpellChecker(language='en')

stopwords = set()


def extend_stopwords():
    global stopwords
    try:
        url = "https://gitee.com/leolulu2/my_spellcheck_exitword/raw/master/exit_words.txt"
        response = urllib.request.urlopen(url, timeout=10)
        text = response.read().decode('utf-8')
        for i in filter(lambda x: x != '', text.split('\n')):
            stopwords.add(i.strip())
        print(f"Successfully update stopwords.")
    except Exception as e:
        print(f"Error while getting online stopwords: {e}")


extend_stopwords()


def highlight(changed: bool, note: Note, current_field_idx: int):
    field_names = note.keys()
    if '释义例句等详细内容' in field_names:
        if field_names[current_field_idx] not in ['单词', '释义例句等详细内容', '来源例句']:
            return False
    if_changed_wrong = highlight_wrong(note, current_field_idx)
    if_changed_word = highlight_word(note, current_field_idx)
    return if_changed_word or if_changed_wrong


def highlight_word_impl(word_value_provided, content, if_changed):
    content_data_to_use = content
    content_data_to_use = content_data_to_use.replace(r'<br>', ' ')
    content_data_to_use = re.sub(r"<span .*?<\/span>", "", content_data_to_use)
    for word_value in re.findall(word_value_provided, content_data_to_use, re.IGNORECASE):
        if_changed = True
        print(f"highlight word: {word_value}")
        highlighted_word = f'<span style="color: rgb(219, 147, 23);">{word_value}</span>'
        content = content.replace(word_value, highlighted_word)
    return if_changed, content


def highlight_word(note: Note, current_field_idx: int):
    note_items = dict(note.items())
    if '单词' not in note_items:
        return False
    if note.keys()[current_field_idx] != '释义例句等详细内容':
        return False
    word_value = note_items['单词']
    if_changed = False
    content = note.fields[current_field_idx]
    if_changed, content = highlight_word_impl(word_value+word_value[-1]+'ing', content, if_changed)
    if_changed, content = highlight_word_impl(word_value+word_value[-1]+'ed', content, if_changed)
    if_changed, content = highlight_word_impl(word_value+'ing', content, if_changed)
    if_changed, content = highlight_word_impl(word_value+'ed', content, if_changed)
    if_changed, content = highlight_word_impl(word_value+'ly', content, if_changed)
    if_changed, content = highlight_word_impl(word_value+'es', content, if_changed)
    if_changed, content = highlight_word_impl(word_value+'er', content, if_changed)
    if_changed, content = highlight_word_impl(word_value+'est', content, if_changed)
    if_changed, content = highlight_word_impl(word_value+'s', content, if_changed)
    if_changed, content = highlight_word_impl(word_value+'t', content, if_changed)
    if word_value.endswith('y'):
        if_changed, content = highlight_word_impl(word_value[:-1]+'ies', content, if_changed)
        if_changed, content = highlight_word_impl(word_value[:-1]+'ily', content, if_changed)
    if word_value.endswith('e'):
        if_changed, content = highlight_word_impl(word_value+'d', content, if_changed)
        if_changed, content = highlight_word_impl(word_value+'r', content, if_changed)
        if_changed, content = highlight_word_impl(word_value+'st', content, if_changed)
        if_changed, content = highlight_word_impl(word_value[:-1]+'ing', content, if_changed)
    if_changed, content = highlight_word_impl(word_value, content, if_changed)
    note.fields[current_field_idx] = content
    return if_changed


def highlight_wrong(note: Note, current_field_idx: int):
    if_changed = False
    content = note.fields[current_field_idx]
    content_data_to_use = content
    content_data_to_use = content_data_to_use.replace(r'<br>', ' ')
    content_data_to_use = re.sub(r"<u .*?<\/u>", "", content_data_to_use)
    words = re.split(r"[ ,\.\/']", content_data_to_use)
    words = [i for i in words if re.search(r"^[a-zA-Z]*$", i)]
    words = [i for i in words if len(i) >= 3]
    words = [i for i in words if i != ""]
    misspelled_words = spell_checker.unknown(words)
    misspelled_words = [i for i in misspelled_words if i not in stopwords]
    threading.Thread(target=extend_stopwords).start()
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


gui_hooks.editor_did_unfocus_field.append(highlight)
