"""N-Gram-Zählung mit Disk-Cache für die Themenanalyse in eda.ipynb.

Muss als importierbares Modul (nicht als Notebook-Zelle) existieren, damit joblib
eine stabile Cache-Identität berechnen kann: Für Funktionen, die direkt in einer
Notebook-Zelle definiert werden, ist `__module__ == "__main__"` und joblib bildet
den Cache-Pfad dann aus dem Pfad der ipykernel-Verbindungsdatei (z.B.
`...AppData\\Local\\Temp\\ipykernel-<pid>\\...`). Das ändert sich bei jedem
Kernel-Neustart und die enthaltenen Backslashes brechen die Ordnerstruktur unter
Windows (`CacheWarning: Unable to cache to disk`).
"""

from pathlib import Path

import pandas as pd
from joblib import Memory
from sklearn.feature_extraction.text import CountVectorizer

NGRAM_CACHE_DIR = Path(__file__).parent / ".cache" / "ngram_cache"
ngram_memory = Memory(location=NGRAM_CACHE_DIR, verbose=0)

EXTRA_STOP_WORDS = {
    'paper', 'propose', 'proposed', 'method', 'methods', 'result', 'results',
    'approach', 'using', 'used', 'use', 'based', 'show', 'shown', 'study',
    'novel', 'present', 'presented',
}


def _contains_stop_word(term, stop_words):
    return any(word in stop_words for word in term.split())


@ngram_memory.cache
def _count_ngrams(texts, ngram_range, min_df):
    """Tokenisiert und zählt N-Gramme; teuerster Schritt, daher gecacht."""
    vectorizer = CountVectorizer(
        stop_words='english',
        ngram_range=ngram_range,
        token_pattern=r'(?u)\b[a-zA-Z]{3,}\b', # mindestens 3 Buchstaben, um z.B. "AI" oder "ML" zu vermeiden
        min_df=min_df,
    )
    doc_term_matrix = vectorizer.fit_transform(texts)
    counts = doc_term_matrix.sum(axis=0).A1
    return pd.DataFrame({'term': vectorizer.get_feature_names_out(), 'count': counts})


def top_ngrams(texts, ngram_range, top_n=25, min_df=5):
    # Stoppwort-Filter bewusst außerhalb der gecachten Funktion, damit Änderungen an
    # EXTRA_STOP_WORDS sofort wirken, ohne den (teuren) Cache zu invalidieren.
    freq_df = _count_ngrams(texts, ngram_range, min_df)
    freq_df = freq_df[~freq_df['term'].apply(lambda t: _contains_stop_word(t, EXTRA_STOP_WORDS))]
    return freq_df.sort_values('count', ascending=False).head(top_n)
