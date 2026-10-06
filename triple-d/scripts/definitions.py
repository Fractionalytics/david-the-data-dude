"""Category definitions and Jev questions for the Diner / Drive-In / Dive classifier.

This is the one file to edit when iterating on classification. Bump
DEFINITIONS_VERSION on any change so cached answers from older definitions
are not mixed with new ones.
"""

import re

from typesafe_sdk import Choice, Noul

DEFINITIONS_VERSION = "v2"  # v2: Dive includes hole-in-the-wall taquerias
MODEL = "jev-1.13.0"  # pinned; aliases move

# Two policies, both computed in build_final.py (name rules win in both):
#   strict: Jev's 4-way Choice. "Other" stays large; this supports the video's hook.
#   forced: the Choice option with the highest probability among Diner / Drive-In / Dive,
#           ignoring "Other" ("if Guy had to pick"). The Choice is used rather than the
#           Nouls because Nouls are absolute and not comparable across categories:
#           the Dive Noul runs high for any casual place, so its argmax picked Dive ~60% of the time.
#           "Guy shrugs": if there is no unique best of the three (Jev returns probabilities
#           rounded to 2 decimals, so a confident "Other" leaves all three at 0.00), the
#           restaurant stays "Other". Taking the first column instead labeled ~500 shrugs "Diner".
# The three Noul scores are still reported as independent 0-1 likelihoods.

DEFINITIONS = {
    "Diner": (
        "A casual, sit-down American eatery built around comfort food and quick table or counter service: "
        "counter seating or booths, breakfast served (often all day), short-order cooking, burgers, sandwiches, "
        "blue-plate specials. Includes classic chrome/railcar diners, luncheonettes, coffee shops, and "
        "family cafes serving breakfast and lunch."
    ),
    "Drive-In": (
        "A place where food is ordered at a window, counter, or from a car and is typically eaten in the car, "
        "outdoors, or taken away: carhop drive-ins, drive-thrus, walk-up stands, roadside shacks, dairy bars, "
        "burger stands, and food trucks or carts. Little or no indoor table service."
    ),
    "Dive": (
        "An unpretentious, no-frills joint with a gritty or worn-in character: a bar, tavern, or pub that serves "
        "food, or a tiny hole-in-the-wall eatery in an unremarkable location (strip mall, gas station, back of a "
        "market), including hole-in-the-wall taquerias and taco shops. Locals' spot, cheap, casual, often "
        "cash-only or quirky decor."
    ),
    "Other": (
        "Does not fit Diner, Drive-In, or Dive: for example a full-service or upscale restaurant, bistro, "
        "brewery taproom, deli or market counter, bakery, pizzeria, BBQ or ethnic restaurant with conventional "
        "table service and no dive-like character."
    ),
}

# Deterministic name rules run before the model. The first match wins.
NAME_RULES = [
    ("Drive-In", re.compile(r"\bdrive[\s-]?ins?\b|\bdrive[\s-]?thru\b", re.I)),
    ("Diner", re.compile(r"\bdiner\b", re.I)),
    ("Dive", re.compile(r"\bdive\b", re.I)),
]

QUESTIONS = {
    "category": Choice(
        instructions=(
            "Based on the restaurant's name, Yelp categories, description, and signature dishes, "
            "which kind of place is this restaurant?"
        ),
        criteria=DEFINITIONS,
    ),
    "is_diner": Noul(instructions=f"Is this restaurant a diner? A diner is: {DEFINITIONS['Diner']}"),
    "is_drive_in": Noul(instructions=f"Is this restaurant a drive-in? A drive-in is: {DEFINITIONS['Drive-In']}"),
    "is_dive": Noul(instructions=f"Is this restaurant a dive? A dive is: {DEFINITIONS['Dive']}"),
}


def name_rule(name: str) -> str | None:
    for category, pattern in NAME_RULES:
        if pattern.search(name or ""):
            return category
    return None


# --- "Other" buckets: what the non-DDD restaurants actually are -------------------------
# Asked only of restaurants whose strict classification is "Other". Diners, Drive-Ins and
# Dives keep their category in the detailed column. Bump BUCKETS_VERSION on any change.
BUCKETS_VERSION = "b1"

BUCKETS = {
    "Sandwiches & delis": "Sandwich shops and delis where the sandwich is the main event: subs, hoagies, cheesesteaks, po'boys, Jewish or Italian delis.",
    "BBQ & smokehouses": "Barbecue joints and smokehouses built around smoked meats: brisket, ribs, pulled pork, pitmasters.",
    "Pizza & Italian": "Pizzerias and Italian or Italian-American restaurants: pizza, pasta, red-sauce classics.",
    "Seafood": "Seafood-focused places: fish houses, crab, oyster, lobster or clam shacks, fish markets with a kitchen.",
    "Mexican & Latin": "Mexican, Tex-Mex, Central and South American, Cuban, Puerto Rican and Caribbean restaurants.",
    "Southern, Cajun & soul": "Southern comfort food, soul food, Cajun, Creole and Lowcountry cooking.",
    "Global kitchens": "Cuisines from Europe, Asia, Africa, the Middle East, the Mediterranean or the Pacific Islands (Greek, Korean, Thai, Indian, Polish, German, Hawaiian, Ethiopian and so on), but not Italian or Latin American.",
    "New American bistros": "Chef-driven, farm-to-table or creative New American restaurants and bistros, including small-plates and upscale-casual spots.",
    "Brewpubs & bars": "Breweries, brewpubs, gastropubs, taverns, and cocktail or wine bars where the bar is central and the food is serious, without dive-bar grit.",
    "Bakeries, cafes & desserts": "Bakeries, coffee shops and cafes, donut, pie, ice cream and dessert shops.",
    "Breakfast & brunch": "Restaurants centered on breakfast or brunch (pancakes, biscuits, egg dishes) that are not classic diners.",
    "Butchers & markets": "Butcher shops, markets, grocery or specialty food stores, cheese shops, food halls and farm stands with a food counter.",
}

BUCKET_QUESTIONS = {
    "bucket": Choice(
        instructions=(
            "This restaurant is not a classic diner, drive-in or dive. Based on its name, Yelp categories, "
            "description and signature dishes, which kind of restaurant is it? Choose its main specialty or format."
        ),
        criteria=BUCKETS,
    ),
}
