from plugins.simple_visualizer.simple_visualizer import SimpleVisualizer
from api.models.graph import GraphBuilder
import webbrowser
import tempfile
import os

# Kreiramo USMEREN graf sa ljudima
builder = GraphBuilder(directed=True)

# Prva grupa - Programeri
builder \
    .add_node("marko",
              name="Marko Marković",
              godine=32,
              grad="Beograd",
              zanimanje="Senior Programer",
              programski="Python, JS",
              hobi="Planinarenje") \
    .add_node("jovana",
              name="Jovana Jovanović",
              godine=28,
              grad="Novi Sad",
              zanimanje="Frontend Developer",
              programski="React, Vue",
              hobi="Fotografija") \
    .add_node("petar",
              name="Petar Petrović",
              godine=35,
              grad="Beograd",
              zanimanje="Backend Developer",
              programski="Java, C#",
              hobi="Trčanje") \
    .add_node("ana",
              name="Ana Anić",
              godine=26,
              grad="Niš",
              zanimanje="UX/UI Dizajner",
              alati="Figma, Sketch",
              hobi="Crtanje")

# Druga grupa - Menadžment
builder \
    .add_node("nikola",
              name="Nikola Nikolić",
              godine=42,
              grad="Beograd",
              zanimanje="Project Manager",
              iskustvo="15 godina",
              hobi="Golf") \
    .add_node("milica",
              name="Milica Milić",
              godine=38,
              grad="Novi Sad",
              zanimanje="Team Lead",
              tim="10 ljudi",
              hobi="Čitanje")

# Treća grupa - Pripravnici
builder \
    .add_node("stevan",
              name="Stevan Stević",
              godine=23,
              grad="Kragujevac",
              zanimanje="Pripravnik",
              smer="Informatika",
              hobi="Igrice") \
    .add_node("tamara",
              name="Tamara Tasić",
              godine=24,
              grad="Čačak",
              zanimanje="Pripravnik",
              smer="Dizajn",
              hobi="Muzika")

# Četvrta grupa - Spoljni saradnici
builder \
    .add_node("vladimir",
              name="Vladimir Vladić",
              godine=45,
              grad="London",
              zanimanje="Freelancer",
              klijenti="IBM, Google",
              hobi="Putovanja") \
    .add_node("sandra",
              name="Sandra Sandić",
              godine=31,
              grad="Berlin",
              zanimanje="Konsultant",
              oblast="Agile",
              hobi="Joga")

# DODAJEMO IVICE (usmerene)
# Programeri međusobno
builder \
    .add_edge("e1", "marko", "jovana",
              tip="poznanstvo",
              otkako=2021,
              mesto="Hakaton") \
    .add_edge("e2", "marko", "petar",
              tip="kolega",
              projekat="Aplikacija X",
              godina=2022) \
    .add_edge("e3", "jovana", "ana",
              tip="druženje",
              kafa="nedeljno") \
    .add_edge("e4", "petar", "ana",
              tip="mentorstvo",
              oblast="Backend")

# Menadžment veze
builder \
    .add_edge("e5", "nikola", "marko",
              tip="rukovodilac",
              tim="Programeri",
              od="2019") \
    .add_edge("e6", "nikola", "jovana",
              tip="rukovodilac",
              tim="Frontend") \
    .add_edge("e7", "milica", "petar",
              tip="saradnja",
              projekat="Arhitektura") \
    .add_edge("e8", "nikola", "milica",
              tip="sastanak",
              frekvencija="nedeljno")

# Pripravnici
builder \
    .add_edge("e9", "petar", "stevan",
              tip="mentor",
              oblast="Python",
              napredak="dobar") \
    .add_edge("e10", "ana", "tamara",
              tip="mentor",
              oblast="UI/UX",
              zadaci="redizajn") \
    .add_edge("e11", "stevan", "tamara",
              tip="drugari",
              zajednicki="fakultet")

# Spoljne veze
builder \
    .add_edge("e12", "vladimir", "marko",
              tip="poslovno",
              projekat="Outsourcing",
              plata="po satu") \
    .add_edge("e13", "sandra", "nikola",
              tip="konsultacije",
              tema="Agile tranzicija",
              trajanje="3 meseca") \
    .add_edge("e14", "vladimir", "sandra",
              tip="bivši kolege",
              firma="Tech Corp",
              godina=2018)

# Još neke veze - stvaramo cikluse
builder \
    .add_edge("e15", "stevan", "marko",
              tip="pitanja",
              često="da") \
    .add_edge("e16", "tamara", "ana",
              tip="dodatna obuka",
              termin="vikendom") \
    .add_edge("e17", "marko", "nikola",
              tip="izveštaj",
              period="kvartalno") \
    .add_edge("e18", "milica", "vladimir",
              tip="konsultacije",
              platforma="online")

graf = builder.build()

for node_id, node in graf.nodes.items():
    ime = node.attributes.get('name', node_id)
    zanimanje = node.attributes.get('zanimanje', '')
    grad = node.attributes.get('grad', '')
    print(f"  • {ime} | {zanimanje} | {grad}")

# Vizuelizacija
viz = SimpleVisualizer()
html = viz.render(graf)

# Sačuvaj i otvori
temp = os.path.join(tempfile.gettempdir(), "ljudi_graf.html")
with open(temp, "w", encoding="utf-8") as f:
    f.write(html)

webbrowser.open(f"file://{temp}")