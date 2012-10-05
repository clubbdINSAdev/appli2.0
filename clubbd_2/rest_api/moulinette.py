from django.db import connections, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
import rest_api.models

# Stolen from django docs
def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def mk_volumes(cursor):
    cursor.execute("SELECT b1.* FROM book as b1, book as b2 WHERE b1.serial_id = b2.serial_id AND b1.id != b2.id GROUP BY b1.id;")

    for row in dictfetchall(cursor):
        e = None
        try:
            e = rest_api.models.Editeur.objects.get(pk=row['editor_id'])
        except ObjectDoesNotExist:
            pass

        s = None
        try:
            s = rest_api.models.Serie.objects.get(pk=row['serial_id'])
        except ObjectDoesNotExist:
            pass
        
        v = rest_api.models.Volume(
            cote=row['reference'],
            titre=row['title'],
            date_entree=row['buy_date'],
            id_editeur=e,
            is_manga=(row['kind'] == 'm'),
            id_serie=s,
            numero=row['serial_nb']
        )

        v.save()

def mk_editeur(cursor):
    cursor.execute("SELECT name FROM editor WHERE name != ''")
    for name in cursor.fetchall():
        e = rest_api.models.Editeur(
            nom=name[0]
        )
        e.save()

def mk_categorie():
    c = rest_api.models.Categorie(
        prefix=3,
        nom="Humour"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=4,
        nom="Heroic Fantaisy"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=5,
        nom="Science Fiction"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=6,
        nom="Western"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=7,
        nom="Historique"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=8,
        nom="Policier"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=9,
        nom="Comics, Divers"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=10,
        nom="Fantastique"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=22,
        nom="Classique Sport Mecanique"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=23,
        nom="Classique Humour"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=26,
        nom="Classique Western"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=27,
        nom="Classique Historique"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=28,
        nom="Classique Policier"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=29,
        nom="Classique Divers?"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=69,
        nom="Erotique"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=81,
        nom="Shonen"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=82,
        nom="Shojo"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=83,
        nom="Seinen"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=84,
        nom="Comique, Divers?"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=85,
        nom="Langue Etrangere"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=86,
        nom="inconnu ?"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=87,
        nom="Oneshot"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=96,
        nom="Hentai"
    )
    c.save()

def mk_serie(cursor):
    cursor.execute("SELECT serial.*, reference FROM serial, book WHERE book.serial_id = serial.id GROUP BY serial.id;")

    for row in dictfetchall(cursor):
        c = None
        try:
            c = rest_api.models.Categorie.objects.get(pk=row['reference'][0:2])
        except ObjectDoesNotExist:
            print row
            print row['reference'][0:2]
            pass

        if c != None:
            s = rest_api.models.Serie(
                nom=row['title'],
                prefix=row['reference'][2:5],
                id_categorie = c
            )
            s.save()

def mk_all():
    cursor = connections['old'].cursor()

    mk_editeur(cursor)
    mk_categorie()
    mk_serie(cursor)
    mk_volumes(cursor)
    # ...


