"""Jev questions for classifying Ideabrowser ideas (approved by David 2026-10-07, docs/categories.md).

The one file to edit when iterating on classification. Bump DEFINITIONS_VERSION on any
change so cached answers from older definitions are not mixed with new ones.
Options are listed with "Other" / "Not clear" last; Jev leans toward the first option.
"""
from typesafe_sdk import Choice

DEFINITIONS_VERSION = "v3"  # v3: "Larger companies" renamed "Larger companies & institutions". v2: horizontal tools are classed by the job they do, not the pitch's example
MODEL = "jev-1.13.0"  # pinned; aliases move

WHO_PAYS = {
    "Consumers": "Individuals or families paying for themselves. A parent buying for their kid counts here.",
    "Small & local businesses": (
        "Shops, clinics, contractors, restaurants, agencies and other small teams. "
        "A solo therapist's or contractor's practice counts here, not under Solo professionals."
    ),
    "Solo professionals & creators": (
        "Freelancers, creators, indie hackers, job seekers and one-person operators selling their own work."
    ),
    "Larger companies & institutions": (
        "Mid-size and enterprise companies, enterprise teams, and institutions such as schools, hospitals "
        "and governments. 'Remote teams' or 'companies' with no size stated is Not clear, not this."
    ),
    "Not clear": "The text does not say who pays.",
}

INDUSTRY = {
    "Home services & trades": "HVAC, lawn care, plumbing, cleaning, pool service, contractors working on homes.",
    "Real estate & construction": "Real estate agents, landlords, builders, property managers, construction firms.",
    "Health & medical": "Clinics, doctors, therapists, physical therapy, pharmacy, patient tools.",
    "Fitness, wellness & beauty": "Gyms, coaches, med spas, salons, sleep, nutrition, personal wellness.",
    "Finance, insurance & legal": "Lending, credit, accounting, tax, insurance, law.",
    "Retail & e-commerce": "Online stores, Shopify sellers, product brands, resale.",
    "Food & restaurants": "Restaurants, food brands, groceries, farms.",
    "Marketing, sales & media": "Ads, sales outreach, social media, content creation, newsletters.",
    "Software & AI tools": "Tools for developers, SaaS companies, or AI agents themselves.",
    "Work, hiring & careers": "HR, recruiting, job seekers, freelancers' business admin.",
    "Education & parenting": "Schools, students, tutoring, kids, family logistics.",
    "Travel, events & hospitality": "Hotels, Airbnb hosts, events, tourism.",
    "Hobbies, collectibles & pets": "Collectors, crafts, games, hobbies, pets.",
    "Automotive & transport": "Car buying, dealers, auto repair, fleets.",
    "Other": "A real industry not listed above, such as funeral services, agriculture equipment or government.",
    "Not clear": "The text does not say which industry or life area it serves.",
}

BUSINESS_TYPE = {
    "Software / app": "SaaS, mobile apps, browser extensions, dashboards.",
    "Marketplace": "Connects two sides, such as buyers and sellers or clients and providers.",
    "Service": "Done-for-you, agency, concierge or staffing work where people do the work.",
    "Physical product": "Goods, kits or hardware.",
    "Media, community & data": "Newsletters, directories, reports, indexes or communities.",
    "Not clear": "The text does not say what kind of business it is.",
}

AI_CENTRAL = {
    "Yes": "The idea's core function depends on AI: AI agents, generation, detection or prediction.",
    "No": "AI is not mentioned, or is only a side feature.",
    "Not stated": "The text is too thin to tell.",
}

QUESTIONS = {
    "who_pays": Choice(instructions="Who is the paying customer for this business idea?", criteria=WHO_PAYS),
    "industry": Choice(
        instructions=(
            "Which industry or life area does this business idea serve? "
            "Pick the customer's industry, not the technology used. "
            "If the idea works across many industries and the pitch only uses one as an example, "
            "pick the job it does (for example Marketing, sales & media) instead of the example's industry."
        ),
        criteria=INDUSTRY,
    ),
    "business_type": Choice(instructions="What kind of business is this idea?", criteria=BUSINESS_TYPE),
    "ai_central": Choice(instructions="Is AI central to this product?", criteria=AI_CENTRAL),
}
