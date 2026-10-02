"""Build the PowerPoint decks in the ITI template style: python3 build_pptx.py 1 2 4 5"""
import importlib
import os
import sys

import pptlib

sys.modules["lib"] = pptlib  # lesson modules do `from lib import *`

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "iti_template.pptx")
OUT = os.path.join(HERE, "..", "pptx")

META = {
    1: ("ITI_Database_Course_Lesson_1_Introduction.pptx", ("Introduction to ", "Databases"),
        ("Up next · Lesson 2", "Lesson 2 · ERD", "From words to **diagrams**.",
         "We turn a business narrative into entities, attributes and relationships — the COMPANY database first.")),
    2: ("ITI_Database_Course_Lesson_2_ERD.pptx", ("Entity Relationship ", "Diagrams"),
        ("Up next · Lesson 3", "Lesson 3 · Mapping", "Every ERD becomes **tables**.",
         "Seven mapping steps turn the diagrams from today into relations, primary keys and foreign keys.")),
    4: ("ITI_Database_Course_Lesson_4_SQL.pptx", ("Structured Query ", "Language"),
        ("Up next · Lesson 5", "Lesson 5 · Normalization", "Is the design **good**?",
         "Functional dependencies and normal forms: how to spot redundancy and remove update anomalies.")),
    5: ("ITI_Database_Course_Lesson_5_Normalization.pptx", ("", "Normalization"),
        ("Course complete", "Database Fundamentals", "From narrative to **normalized** SQL.",
         "ERD → tables → `CREATE TABLE` → queries → normal forms. Keep practising on real data.")),
}

os.makedirs(OUT, exist_ok=True)
for n in map(int, sys.argv[1:]):
    fname, split, closing = META[n]
    mod = importlib.import_module(f"lesson{n}")
    deck = mod.build()
    deck.cover_split = split
    deck.closing = closing
    total = deck.write(os.path.join(OUT, fname), TEMPLATE)
    print(f"lesson{n}: {total} slides -> pptx/{fname}")
