simple_rules = [
    lambda word: word + word[-1] + "ing",
    lambda word: word + word[-1] + "ed",
    lambda word: word + "ing",
    lambda word: word + "ed",
    lambda word: word + "ly",
    lambda word: word + "es",
    lambda word: word + "er",
    lambda word: word + "est",
    lambda word: word + "s",
    lambda word: word + "t",
    lambda word: word + "n",
]

complex_rules = [
    [
        lambda word: word.endswith("y"),
        [
            lambda word: word[:-1] + "ies",
            lambda word: word[:-1] + "ily",
            lambda word: word[:-1] + "ier",
            lambda word: word[:-1] + "iest",
        ],
    ],
    [
        lambda word: word.endswith("e"),
        [
            lambda word: word + "d",
            lambda word: word + "r",
            lambda word: word + "st",
            lambda word: word[:-1] + "ing",
        ],
    ],
]
