"""County master-demographics source → standard mappings (extracted from survivorship SQL).

Used by scripts/seed_county_master_crosswalk.py only.

Design:
  - Crosswalk rows map **source strings county systems store** → **exchange/reporting standards**
    (CDCREC OMB rollup, BCP 47). They do not replace Value_Set_Members (HL7 expansion).
  - `mapping_type=exclude` mirrors SQL WHERE / survivorship null treatment.
  - `mapping_type=rollup` for race/ethnicity/SexID county logic; `exact` for language → BCP 47.
  - County language *reporting groups* (Asian, European (other)) stay in Dictionary survivorship
    text — not duplicated here unless we add a future county_rollup table.

Source: SHIE master-demographics workbook — race_expanded_population / ethnicity /
language_expanded_population CASE blocks (Mark B / county).
"""

from __future__ import annotations

# (source_value, county_race_group_label) — RaceGroup CASE in SQL
RACE_SOURCE_TO_COUNTY_GROUP: tuple[tuple[str, str], ...] = (
    ("African American", "Black or African American"),
    ("American Indian", "American Indian or Alaska Native"),
    ("American Indian or Alaska Native", "American Indian or Alaska Native"),
    ("Asian", "Asian"),
    ("Asian /White", "More than one race"),
    ("Asian/ White", "More than one race"),
    ("Asian Indian", "Asian"),
    ("Black", "Black or African American"),
    ("Black or African American", "Black or African American"),
    ("Black Or African American /White", "More than one race"),
    ("Black Or African American/ White", "More than one race"),
    ("Cambodian", "Asian"),
    ("CAUCASIAN", "White"),
    ("Causasian", "White"),
    ("Chinese", "Asian"),
    ("DTS", "Unknown"),
    ("Eskimo", "American Indian or Alaska Native"),
    ("Filipino", "Asian"),
    ("Guamanian or Chamorro", "Native Hawaiian or Other Pacific Islander"),
    ("Japanese", "Asian"),
    ("Korean", "Asian"),
    ("Laotian", "Asian"),
    ("More than one race", "More than one race"),
    ("NAT AMER/ESK/ALEUT", "American Indian or Alaska Native"),
    ("Nat Amer/Esk/Aleut", "American Indian or Alaska Native"),
    ("Native American/Alaskan / White", "More than one race"),
    ("Native American/Alaskan /Black", "More than one race"),
    ("Native American/ Alaskan/ White", "More than one race"),
    ("Native American/ Alaskan/ Black", "More than one race"),
    ("Native Hawaiian", "Native Hawaiian or Other Pacific Islander"),
    ("Native Hawaiian or Other Pacific Islander", "Native Hawaiian or Other Pacific Islander"),
    ("Other Pacific Islander", "Native Hawaiian or Other Pacific Islander"),
    ("Other Race", "Other Race"),
    ("Samoan", "Native Hawaiian or Other Pacific Islander"),
    ("U", "Unknown"),
    ("Unknown", "Unknown"),
    ("Unknown/Not Reported", "Unknown"),
    ("Unknown/ Not Reported", "Unknown"),
    ("Vietnamese", "Asian"),
    ("White", "White"),
)

# SQL WHERE Race NOT IN (...) — exclude from aggregates (mapping_type exclude)
RACE_AGGREGATE_EXCLUDES: frozenset[str] = frozenset(
    {"U", "Unknown", "Unknown/Not Reported", "Unknown/ Not Reported", "DTS", "Other Race"}
)

# (source_value, county_ethnicity_group_label)
ETHNICITY_SOURCE_TO_COUNTY_GROUP: tuple[tuple[str, str], ...] = (
    ("Cuban", "Hispanic or Latino"),
    ("Declined To Specify", "Unknown"),
    ("Hispanic or Latino", "Hispanic or Latino"),
    ("Mexican", "Hispanic or Latino"),
    ("Mexicano", "Hispanic or Latino"),
    ("MU Unknown Do Not Use", "Unknown"),
    ("NOT HISPANIC", "Not Hispanic or Latino"),
    ("Not Hispanic", "Not Hispanic or Latino"),
    ("Not Hispanic or Latino", "Not Hispanic or Latino"),
    ("Patient Refused", "Unknown"),
    ("Puerto Rican", "Hispanic or Latino"),
    ("Unk/Decline", "Unknown"),
    ("Unknown", "Unknown"),
)

ETHNICITY_AGGREGATE_EXCLUDES: frozenset[str] = frozenset(
    {
        "Unknown",
        "Unk/Decline",
        "MU Unknown Do Not Use",
        "Declined To Specify",
        "Patient Refused",
    }
)

# (source_token, normalized_display, bcp47_tag) — Language CASE block 1 + ISO 639-2 aliases
# bcp47 empty → row omitted unless listed in LANGUAGE_NEEDS_REVIEW
LANGUAGE_SOURCE_TO_BCP47: tuple[tuple[str, str, str], ...] = (
    ("Achinese", "Achinese", "ace"),
    ("Abkhazian", "Abkhazian", "ab"),
    ("Afrikaans", "Afrikaans", "af"),
    ("Albanian", "Albanian", "sq"),
    ("Amharic", "Amharic", "am"),
    ("Arabic", "Arabic", "ar"),
    ("ara", "Arabic", "ar"),
    ("Armenian", "Armenian", "hy"),
    ("ASL", "Sign language", "ase"),
    ("Basque", "Basque", "eu"),
    ("Bengali", "Bengali", "bn"),
    ("Berber (Other)", "Berber", "ber"),
    ("Bosnian", "Bosnian", "bs"),
    ("Bulgarian", "Bulgarian", "bg"),
    ("Burmese", "Burmese", "my"),
    ("mya", "Burmese", "my"),
    ("Cambodian", "Cambodian", "km"),
    ("CAM", "Cemuhî", "cam"),
    ("Cantonese", "Cantonese", "yue"),
    ("Catalan; Valencian", "Catalan; Valencian", "ca"),
    ("Central Khmer", "Central Khmer", "km"),
    ("Chinese", "Chinese", "zh"),
    ("zho", "Chinese", "zh"),
    ("WU", "Chinese", "zh"),
    ("Croatian", "Croatian", "hr"),
    ("Danish", "Danish", "da"),
    ("Dari", "Dari", "prs"),
    ("Dravidian (Other)", "Dravidian", "inc"),
    ("Dutch", "Dutch", "nl"),
    ("nld", "Dutch", "nl"),
    ("English", "English", "en"),
    ("eng", "English", "en"),
    ("Esperanto", "Esperanto", "eo"),
    ("Ethiopic", "Ethiopic", "gez"),
    ("FAR", "Fataleka", "far"),
    ("Faroese", "Faroese", "fo"),
    ("Farsi", "Farsi", "fa"),
    ("Fijian", "Fijian", "fj"),
    ("Filipino", "Filipino", "fil"),
    ("French", "French", "fr"),
    ("Georgian", "Georgian", "ka"),
    ("German", "German", "de"),
    ("Greek, Modern (1453-)", "Modern Greek", "el"),
    ("Gujarati", "Gujarati", "gu"),
    ("Hebrew", "Hebrew", "he"),
    ("Hindi", "Hindi", "hi"),
    ("hin", "Hindi", "hi"),
    ("Hungarian", "Hungarian", "hu"),
    ("Igbo", "Igbo", "ig"),
    ("Indonesian", "Indonesian", "id"),
    ("Italian", "Italian", "it"),
    ("Japanese", "Japanese", "ja"),
    ("jpn", "Japanese", "ja"),
    ("Karen", "Karen", "kar"),
    ("Khotanese", "Khotanese", "kho"),
    ("Korean", "Korean", "ko"),
    ("Lao", "Lao", "lo"),
    ("Laotian", "Laotian", "lo"),
    ("Latin", "Latin", "la"),
    ("Lingala", "Lingala", "ln"),
    ("Lithuanian", "Lithuanian", "lt"),
    ("Macedonian", "Macedonian", "mk"),
    ("Malay", "Malay", "ms"),
    ("Malayalam", "Malayalam", "ml"),
    ("Mam", "Mam", "mam"),
    ("Mandingo", "Mandingo", "mnk"),
    ("Mandarin", "Mandarin", "cmn"),
    ("Mien", "Mien", "ium"),
    ("Mongolian", "Mongolian", "mn"),
    ("Navajo; Navaho", "Navajo; Navaho", "nv"),
    ("Nepali", "Nepali", "ne"),
    ("Oromo", "Oromo", "om"),
    ("Panjabi; Punjabi", "Panjabi; Punjabi", "pa"),
    ("Persian", "Persian", "fa"),
    ("Philippine (Other)", "Philippine", "phi"),
    ("Polish", "Polish", "pl"),
    ("Portuguese", "Portuguese", "pt"),
    ("Pushto; Pashto", "Pushto; Pashto", "ps"),
    ("Quechua", "Quechua", "qu"),
    ("Romani", "Romani", "rom"),
    ("Romanian; Moldavian; Moldovan", "Romanian; Moldavian; Moldovan", "ro"),
    ("Russian", "Russian", "ru"),
    ("rus", "Russian", "ru"),
    ("Samoan", "Samoan", "sm"),
    ("Serbian", "Serbian", "sr"),
    ("Sign Language", "Sign Language", "sgn"),
    ("sgn", "Sign Language", "sgn"),
    ("Sinhala; Sinhalese", "Sinhala; Sinhalese", "si"),
    ("Slavic (Other)", "Slavic", "sla"),
    ("Somali", "Somali", "so"),
    ("Spanish", "Spanish", "es"),
    ("spa", "Spanish", "es"),
    ("Sundanese", "Sundanese", "su"),
    ("Swahili", "Swahili", "sw"),
    ("Swedish", "Swedish", "sv"),
    ("Tagalog", "Tagalog", "tl"),
    ("tgl", "Tagalog", "tl"),
    ("Tai (Other)", "Tai", "tai"),
    ("Tamil", "Tamil", "ta"),
    ("Telugu", "Telugu", "te"),
    ("Thai", "Thai", "th"),
    ("Tibetan", "Tibetan", "bo"),
    ("Tigrigna", "Tigrigna", "ti"),
    ("Tigrinya", "Tigrigna", "ti"),
    ("tir", "Tigrigna", "ti"),
    ("Tonga (Nyasa)", "Tonga (Nyasa)", "tog"),
    ("Tonga (Tonga Islands)", "Tonga (Tonga Islands)", "to"),
    ("Turkish", "Turkish", "tr"),
    ("Twi", "Twi", "tw"),
    ("Ukrainian", "Ukrainian", "uk"),
    ("Undetermined", "Undetermined", "und"),
    ("und", "Undetermined", "und"),
    ("Urdu", "Urdu", "ur"),
    ("Uzbek", "Uzbek", "uz"),
    ("Vietnamese", "Vietnamese", "vi"),
    ("vie", "Vietnamese", "vi"),
    ("Wolof", "Wolof", "wo"),
    ("Yoruba", "Yoruba", "yo"),
)

# SQL WHERE LanguageID NOT IN / survivorship excludes
LANGUAGE_AGGREGATE_EXCLUDES: frozenset[str] = frozenset(
    {
        "und",
        "Undetermined",
        "Declined to specify",
        "Declined to spec",
        "SPE",
        "OTHER",
        "Other",
    }
)

# Steward review — present in county SQL but BCP 47 not confident without validation
LANGUAGE_NEEDS_REVIEW: frozenset[str] = frozenset({"SPE"})

SEXID_SOURCE_TO_BIRTHSEX: tuple[tuple[str, str, str, str], ...] = (
    ("M", "M", "Male", "exact"),
    ("F", "F", "Female", "exact"),
    ("Male", "M", "Male", "rollup"),
    ("Female", "F", "Female", "rollup"),
    ("Male to Female", "F", "Female", "rollup"),
    ("Female to Male", "M", "Male", "rollup"),
)

SEXID_AGGREGATE_EXCLUDES: frozenset[str] = frozenset({"U", "Unknown", "Any", "Unknown/ Other"})

# County race group label → CDCREC OMB code (Table 5 → exchange standard)
COUNTY_RACE_GROUP_TO_CDCREC: dict[str, tuple[str, str]] = {
    "Black or African American": ("2054-5", "Black or African American"),
    "American Indian or Alaska Native": ("1002-5", "American Indian or Alaska Native"),
    "Asian": ("2028-9", "Asian"),
    "Native Hawaiian or Other Pacific Islander": ("2076-8", "Native Hawaiian or Other Pacific Islander"),
    "Native Hawaiian/ Pacific Islander": ("2076-8", "Native Hawaiian or Other Pacific Islander"),
    "White": ("2106-3", "White"),
    "Other Race": ("2131-1", "Other Race"),
    "More than one race": ("2131-1", "Other Race"),
}

COUNTY_ETHNICITY_GROUP_TO_CDCREC: dict[str, tuple[str, str]] = {
    "Hispanic or Latino": ("2135-2", "Hispanic or Latino"),
    "Not Hispanic or Latino": ("2186-5", "Not Hispanic or Latino"),
}
