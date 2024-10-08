import operator

METRICS_ALL = [
    "RMSD",
    "P-VALUE",
    "INF-ALL",
    "INF-WC",
    "INF-NWC",
    "INF-STACK",
    "DI",
    "MCQ",
    "TM-SCORE",
    "GDT-TS",
    "BARNABA-eRMSD",
    "CLASH",
]

METRICS = [
    "RMSD",
    "INF-ALL",
    "DI",
    "INF-WC",
    "P-VALUE",
    "TM-SCORE",
    "GDT-TS",
    "εRMSD",
    "lDDT",
    "INF-STACK",
    "INF-NWC",
    "MCQ",
    "tm-score-ost",
    "TM-score",
    "QS-score",
    "CAD",
]
SUB_METRICS = [
    "RMSD",
    "P-VALUE",
    "DI",
    "εRMSD",
    "TM-score",
    "GDT-TS",
    "INF-ALL",
    "lDDT",
]
ALL_MODELS = [
    "mcsym",
    # "ifoldrna",
    "vfold",
    "rnacomposer",
    "simrna",
    "3drna",
    "isrna",
    "rhofold",
    "trrosettarna",
    "vfoldpipeline",
    "rnajp",
    "alphafold3"
]
# Higher is better
ASC_METRICS = ["INF-ALL", "TM-score", "GDT-TS", "lDDT"]
# Lower is better
DESC_METRICS = ["RMSD", "P-VALUE", "DI", "εRMSD", "MCQ"]
PAPER_METRICS = [
    "RMSD",
    "MCQ",
    "DI",
    "P-VALUE",
    "εRMSD",
    "INF-ALL",
    "TM-score",
    "lDDT",
    "GDT-TS",
    "CAD",
]

RNA_CHALLENGES_LENGTH = {
    "rp03": 84,
    "rp04": 126,
    "rp05": 188,
    "rp06": 168,
    "rp07": 185,
    "rp08": 96,
    "rp09": 71,
    "rp11": 57,
    "rp12": 123,
    "rp13": 71,
    "rp14b": 61,
    "rp14f": 61,
    "rp16": 27,
    "rp17": 62,
    "rp18": 71,
    "rp21": 41,
    "rp23": 37,
    "rp24": 112,
    "rp25": 69,
    "rp29": 52,
    "rp32": 49,
    "rp34": 68,
}
RNA_CHALLENGES_LENGTH_SORTED = dict(
    sorted(RNA_CHALLENGES_LENGTH.items(), key=operator.itemgetter(1))
)

CASP_RNA_CHALLENGES_LENGTH = {
    "R1107": 69,
    "R1108": 69,
    "R1116": 157,
    "R1117": 30,
    "R1126": 363,
    "R1128": 238,
    "R1136": 374,
    "R1138": 720,
    "R1149": 124,
    "R1156": 135,
    "R1189": 173,
    "R1190": 173,
}
CASP_RNA_CHALLENGES_LENGTH_SORTED = dict(
    sorted(CASP_RNA_CHALLENGES_LENGTH.items(), key=operator.itemgetter(1))
)
CASP_RNA_NAMES = list(CASP_RNA_CHALLENGES_LENGTH_SORTED.keys())
RNA_NAMES = list(RNA_CHALLENGES_LENGTH_SORTED.keys())
MODELS_TO_GROUP = {
    "MC-Sym": "Template-based",
    "Vfold3D": "Template-based",
    "RNAComposer": "Template-based",
    "3dRNA": "Template-based",
    "IsRNA1": "Ab initio",
    "RhoFold": "Deep learning",
    "trRosettaRNA": "Deep learning",
    "Vfold-Pipeline": "Template-based",
    "RNAJP": "Ab initio",
    "AlphaFold3": "Deep learning"
}
ORDER_MODELS = list(MODELS_TO_GROUP.keys())
MODELS = list(MODELS_TO_GROUP.keys())
COLORS = {
    "Template-based": "#e0aa74",
    "Ab initio": "#A6CF98",
    "Deep learning": "#4999f7",
}
OLD_TO_NEW = {
    "BARNABA-eRMSD": "εRMSD",
    "rnacomposer": "RNAComposer",
    "isrna": "IsRNA1",
    "3drna": "3dRNA",
    "rhofold": "RhoFold",
    # "ifoldrna": "iFoldRNA",
    "vfold": "Vfold3D",
    "eprna": "epRNA",
    "rp14_free": "rp14f",
    "rp14_bound": "rp14b",
    "lddt": "lDDT",
    "trrosettarna": "trRosettaRNA",
    "mcsym": "MC-Sym",
    "vfoldpipeline": "Vfold-Pipeline",
    "rnajp": "RNAJP",
    "alphafold3": "AlphaFold3"
    # "INF-ALL": r"$INF_{all}$"
}


RNASOLO_RAW_CHALLENGES = {
    "1YFG": 64,
    "1XJR": 46,
    "4ENC": 52,
    "4OQU": 97,
    "3LA5": 71,
    "4ZNP": 73,
    "4WFL": 105,
    "7KGA": 89,
    "2QUS": 68,
    "6N5P": 126,
    "3DIL": 173,
    "2A64": 298,
    "8SA3": 210,
    "7D7W": 51,
    "4RUM": 91,
    "6CU1": 79,
    "3OXE": 86,
    "6FZ0": 47,
    "4AOB": 94,
    "2IL9": 135,
    "6UES": 119,
    "4LVW": 89,
    "5T83": 89,
    "1U9S": 155,
    "6PRV": 57,
    "4PQV": 68,
    "3D2V": 77,
    "5NWQ": 40,
    "7ELQ": 45,
}
RNASOLO_LENGTH_SORTED = dict(
    sorted(RNASOLO_RAW_CHALLENGES.items(), key=operator.itemgetter(1))
)

RNASOLO_NAMES = list(RNASOLO_LENGTH_SORTED.keys())

NAMES_TO_BENCHMARK = {
    "RNA_PUZZLES": RNA_NAMES,
    "CASP_RNA": CASP_RNA_NAMES,
    "RNASOLO": RNASOLO_NAMES,
}
NAMES_TO_LENGTH = {
    "RNA_PUZZLES": RNA_CHALLENGES_LENGTH_SORTED,
    "CASP_RNA": CASP_RNA_CHALLENGES_LENGTH_SORTED,
    "RNASOLO": RNASOLO_LENGTH_SORTED,
}
