"""Jev question for classifying surnames by origin (categories approved by David 2026-10-11).

Categories follow the "Origins of particular surnames" section of
https://en.wikipedia.org/wiki/Surname (Wikipedia spells it "cognominal").
"Compound" is decided in code (build step), not by Jev: a surname is compound when it
joins two surnames (hyphen, or two words neither of which is a particle like De/La/Van).

Bump DEFINITIONS_VERSION on any change so cached answers are not mixed.
Options are listed with "Other" last; Jev leans toward the first option.
"""
from typesafe_sdk import Choice

DEFINITIONS_VERSION = "v5"  # v5: dropped the rule sending Chinese/Korean romanizations to Other (David). v4: etymology may be web-researched, "best-supported origin". v3: Spanish -ez patronymic rule; Chinese/Korean romanizations are Other. v2: Wiktionary etymology added to state. v1: name + birth country only
MODEL = "jev-1.13.0"  # pinned; aliases move

SURNAME_TYPE = {
    "Patronymic": (
        "Comes from the given name of a father or male ancestor, or from a clan named after one: "
        "Johnson, Jones, Williams, Peterson, Rodríguez, Hernández, Martínez, MacDonald, O'Brien, Ivanov. "
        "A surname that is simply a man's given name (Martin, Thomas, Henry) counts here, and so do "
        "Spanish and Portuguese surnames formed with -ez, -az, -iz or -oz (Velázquez from Velasco, "
        "Díaz, Muñoz, Ortiz, Báez)."
    ),
    "Matronymic": (
        "Comes from the given name of a mother or female ancestor: Beaton, Marion, Madison (Maud's son), "
        "Molson, De Paula."
    ),
    "Cognominal": (
        "Comes from a nickname describing the first bearer: appearance, colour, size or strength "
        "(Brown, Short, Little, Armstrong, Moreno, Rubio), personality or behaviour (Gutman, Bueno), "
        "ethnic or national origin as a people (Scott, Walsh, French), or an office the bearer only "
        "resembled and did not hold (King, Bishop, Knight, Pope)."
    ),
    "Ornamental/artificial": (
        "Invented or adopted from decorative words, not from a place, parent, job or trait of the "
        "first bearer, usually when surnames became required: Rosenkrantz, Gyldenstierne, Goldstein, "
        "Lindqvist, many Swedish and Ashkenazi Jewish surnames."
    ),
    "Acquired/assigned": (
        "Given to the first bearer by others or chosen at a turning point rather than inherited: "
        "names given to foundlings (Esposito, Innocenti, Trovato, Expósito), names given to enslaved people, "
        "or names freed people chose for themselves (Freeman)."
    ),
    "Occupational": (
        "Comes from the first bearer's job, trade or actual office: Smith, Miller, Taylor, Baker, "
        "Walker (a cloth fuller), Cooper, Herrera (a smith's workshop), Zapata (shoemaker), "
        "Steward, Chamberlain."
    ),
    "Toponymic": (
        "Comes from a place: where the first bearer lived, a landscape feature near their home, or the "
        "town, farm or estate they came from: Hill, Wood, Brooks, Rivera, Washington, Matsumoto "
        "('base of the pine'), Yamamoto ('base of the mountain'), Tanaka ('middle of the rice field'), "
        "Castillo, Mendoza."
    ),
    "Patronage": (
        "Comes from serving or following a patron, saint or religious figure, including Spanish and "
        "Portuguese devotional surnames: Hickman ('Hick's man'), Kilpatrick ('follower of St Patrick'), "
        "De Jesús, De la Cruz, Santos, De los Santos, Encarnación, Concepción, Trinidad."
    ),
    "Other": (
        "The origin is unknown, or several origins are equally likely with no main one, or the spelling "
        "arose by coincidence."
    ),
}

QUESTIONS = {
    "surname_type": Choice(
        instructions=(
            "Classify the surname in `surname` by how the surname originally arose (its etymology). "
            "`etymology` is what surname dictionaries say about the surname, possibly for several "
            "languages or origins, the most likely first; base the answer on its best-supported "
            "origin when it explains one, otherwise on your own knowledge.`birth_country` is where this player was born; "
            "use it only as a hint to the language the surname comes from. Judge the surname's "
            "origin, not the player."
        ),
        criteria=SURNAME_TYPE,
    ),
}
