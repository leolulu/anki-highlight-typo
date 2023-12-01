import urllib.request


class StopwordsManager:
    def __init__(self) -> None:
        self.stopwords = set()
        self.extend_stopwords()

    def extend_stopwords(self):
        try:
            url = "https://gitee.com/leolulu2/my_spellcheck_exitword/raw/master/exit_words.txt"
            response = urllib.request.urlopen(url, timeout=10)
            text = response.read().decode("utf-8")
            for i in filter(lambda x: x != "", text.split("\n")):
                self.stopwords.add(i.strip())
            print(f"Successfully update stopwords.")
        except Exception as e:
            print(f"Error while getting online stopwords: {e}")
