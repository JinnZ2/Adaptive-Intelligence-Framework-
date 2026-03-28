"""Keyword lexicons for ATBM detection components.

These serve as the baseline heuristic layer. Production deployments
should augment with trained NLP models (see ATBS-module.md Section 4).
"""

# Identity group markers — triggers boundary-lock detection when 2+ distinct types appear
IDENTITY_MARKERS: dict[str, list[str]] = {
    "political": [
        "liberal", "conservative", "left-wing", "right-wing", "democrat",
        "republican", "progressive", "libertarian", "socialist", "populist",
        "woke", "maga", "antifa", "nationalist",
    ],
    "geographic": [
        "urban", "rural", "coastal", "heartland", "inner-city", "suburban",
        "flyover", "red state", "blue state", "southern", "northern",
    ],
    "class": [
        "elite", "working class", "middle class", "upper class", "privileged",
        "underprivileged", "educated", "uneducated", "credentialed",
        "blue collar", "white collar",
    ],
    "cultural": [
        "traditional", "modern", "progressive", "backward", "civilized",
        "indigenous", "mainstream", "alternative", "religious", "secular",
    ],
    "demographic": [
        "boomers", "millennials", "gen-z", "immigrants", "natives",
        "foreigners", "outsiders", "insiders",
    ],
}

# Moralization markers — language that assigns moral weight to group membership
MORAL_MARKERS: list[str] = [
    "should", "ought", "must", "duty", "responsible", "irresponsible",
    "moral", "immoral", "ethical", "unethical", "righteous", "virtuous",
    "sinful", "corrupt", "pure", "impure", "decent", "indecent",
    "worthy", "unworthy", "deserving", "undeserving",
]

# Demonization markers — language that frames groups as threats
DEMON_MARKERS: list[str] = [
    "dangerous", "threat", "menace", "destroy", "destroying", "attack",
    "attacking", "undermine", "undermining", "corrupt", "corrupting",
    "poison", "poisoning", "infect", "infectious", "cancer", "plague",
    "invasion", "invading", "enemy", "enemies", "extremist", "radical",
    "fanatic", "militant", "terrorist",
]

# Father-function narrative templates
FATHER_TEMPLATES: dict[str, list[str]] = {
    "order": [
        "law and order", "discipline", "control", "regulate", "enforce",
        "rules", "structure", "hierarchy", "authority", "obedience",
        "compliance", "submit", "conform",
    ],
    "purity": [
        "pure", "clean", "contaminate", "pollute", "taint", "corrupt",
        "wholesome", "degenerate", "sacred", "profane", "sanctity",
        "defile", "pristine",
    ],
    "blame": [
        "fault", "blame", "responsible for", "caused by", "because of them",
        "their fault", "they did this", "look what they", "thanks to them",
        "they ruined", "they destroyed",
    ],
    "demonize": [
        "evil", "wicked", "vile", "despicable", "reprehensible",
        "abomination", "monster", "predator", "parasite", "vermin",
        "subhuman", "inhuman", "barbaric", "savage",
    ],
    "compliance": [
        "obey", "submit", "fall in line", "do as told", "follow orders",
        "shut up", "know your place", "stay in line", "toe the line",
        "respect authority",
    ],
}

# Pattern-recognition markers — cross-boundary systemic thinking
PATTERN_MARKERS: list[str] = [
    "systemic", "structural", "pattern", "across groups", "regardless of",
    "universal", "shared", "common", "underlying", "root cause",
    "mechanism", "dynamics", "feedback loop", "cascade", "system-level",
    "institutional", "cross-boundary", "substrate-independent",
]

# Systemic-causation markers — language pointing to causes beyond group identity
SYSTEMIC_MARKERS: list[str] = [
    "caused by", "results from", "driven by", "due to", "consequence of",
    "mechanism", "incentive structure", "feedback", "policy", "regulation",
    "economic", "environmental", "historical", "institutional",
    "resource distribution", "power structure", "information asymmetry",
]
