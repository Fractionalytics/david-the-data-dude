"""Surname helpers shared by the fetch, classify and roster scripts."""
import re

SUFFIX = re.compile(r"\s+(Jr\.?|Sr\.?|II|III|IV|V)$")
PARTICLES = {"de", "del", "la", "las", "los", "van", "von", "der", "den", "da", "dos", "di", "le", "du", "st.", "y"}


def surname(s):
    """MLB's surname with whitespace normalized and any Jr./II/III suffix removed."""
    return SUFFIX.sub("", " ".join(str(s).split())).strip()


def is_compound(s):
    """Two surnames joined: a hyphen, or two or more words that aren't particles (De La Cruz is not)."""
    if "-" in s:
        return True
    words = [w for w in s.split() if w.lower() not in PARTICLES]
    return len(words) > 1


def compound_parts(s):
    return [w for w in re.split(r"[-\s]", s) if w]
