from django.db import connections, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
import rest_api.models
import bcrypt

# Stolen from django docs
def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def mk_ouvrages(cursor, new_series, new_editeurs, new_auteurs):
    #cursor.execute("SELECT b1.* FROM book as b1, book as b2 WHERE b1.serial_id = b2.serial_id AND b1.id != b2.id GROUP BY b1.id;")
    
    cursor.execute("SELECT * FROM author_to_book;")
    dict_atb =  dictfetchall(cursor)
    cursor.execute("SELECT * FROM book;")

    for row in dictfetchall(cursor):
        e = None
        try:
            e = rest_api.models.Editeur.objects.get(pk=new_editeurs[row['editor_id']])
        except (ObjectDoesNotExist, KeyError):
            pass

        s = None
        try:
            s = rest_api.models.Serie.objects.get(pk=new_series[row['serial_id']])
        except (ObjectDoesNotExist, KeyError):
            pass

        print row
        if s != None:
            v = rest_api.models.Volume(
                cote=row['reference'],
                titre=row['title'],
                date_entree=row['buy_date'],
                editeur=e,
                is_manga=(row['kind'] == 'm'),
                serie=s,
                nouveaute=False,
                numero=row['serial_nb']
            )
            v.save()
            for row2 in dict_atb:
                a = None
                if row2['book_id'] == row['id']:
                    try:
                        print row2
                        a = rest_api.models.Auteur.objects.get(pk=new_series[row2['author_id']])
                        v.auteurs.add(a)
                    except (ObjectDoesNotExist, KeyError):
                        pass
            v.save()
        else:
            c = None
            try:
                c = rest_api.models.Categorie.objects.get(pk=row['reference'][0:2])
            except ObjectDoesNotExist:
                print "!------Discard------!"
                print row
                print row['reference'][0:2]
                pass

            if c != None:
                o = rest_api.models.OneShot(
                    cote=row['reference'],
                    titre=row['title'],
                    date_entree=row['buy_date'],
                    editeur=e,
                    is_manga=(row['kind'] == 'm'),
                    nouveaute=False,
                    prefix=row['reference'][2:5],
                    categorie=c
                )
                o.save()
                for row2 in dict_atb:
                    a = None
                    if row2['book_id'] == row['id']:
                        try:
                            print row2
                            a = rest_api.models.Auteur.objects.get(pk=new_series[row2['author_id']])
                            o.auteurs.add(a)
                        except (ObjectDoesNotExist, KeyError):
                            pass
                o.save()


def mk_editeurs(cursor):
    cursor.execute("SELECT * FROM editor WHERE name != '';")

    d = dict()

    for row in dictfetchall(cursor):
        e = rest_api.models.Editeur(
            nom=row['name']
        )
        e.save()
        d.setdefault(row['id'], e.id)

    return d

def mk_categories():
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
        nom="Classique Aventure, Policier"
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
        nom="Comique, Divers"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=85,
        nom="Langue Etrangere"
    )
    c.save()

    c = rest_api.models.Categorie(
        prefix=86,
        nom="Manhwa"
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

def mk_series(cursor):
    cursor.execute("SELECT serial.*, reference FROM serial, book WHERE book.serial_id = serial.id GROUP BY serial.id;")

    d = dict()

    for row in dictfetchall(cursor):
        c = None
        ref = row['reference'][0:2]
        try:
            c = rest_api.models.Categorie.objects.get(pk=ref if ref != 28 else 29)
        except ObjectDoesNotExist:
            print "!------Discard------!"
            print row
            print row['reference'][0:2]
            pass

        if c != None:
            s = rest_api.models.Serie(
                nom=row['title'],
                prefix=row['reference'][2:5],
                categorie = c
            )
            s.save()
            d.setdefault(row['id'], s.id)

    return d

def mk_utilisateurs(cursor):
    cursor.execute("SELECT * FROM user;")

    for row in dictfetchall(cursor):
        u = rest_api.models.Utilisateur(
            id=row['student_number'],
            nom=row['lastname'],
            prenom=row['firstname'],
            mail=row.get('mail','') if row.get('mail','') != '' else row.get('firstname','')+'.'+row.get('lastname','')+'@insa-lyon.fr',
            telephone=row['phone'],
            adresse=row['address']
        )
        u.save()
        s = bcrypt.gensalt(12)
        a = rest_api.models.Authentification(
            salt = s,
            hash = bcrypt.hashpw("aubry", s),
            api_key = bcrypt.hashpw("So long and thanks for the fish!", s),
            utilisateur = u
        )
        a.save()

def mk_auteurs(cursor):
    cursor.execute("SELECT * FROM author;")

    d = dict()
    
    for row in dictfetchall(cursor):
        a = rest_api.models.Auteur(
            nom=row['name']
        )
        a.save()
        d.setdefault(row['id'], a.id)

    return d

def mk_all():
    cursor = connections['old'].cursor()
    cursor.execute("DELETE FROM serial WHERE title = 'One Shot';")
    cursor.execute("DELETE FROM serial WHERE title = 'Hotel';")
    cursor.execute("DELETE FROM serial WHERE title = 'Reset';")
    cursor.execute("DELETE FROM serial WHERE title = 'Un bus passe';")
    cursor.execute("DELETE FROM serial WHERE title = 'Le Passage';")
    cursor.execute("DELETE FROM serial WHERE title = 'La Page Blanche';")
    cursor.execute("DELETE FROM serial WHERE title = 'Montrez-moi le chemin';")
    cursor.execute("DELETE FROM book WHERE reference = '';")
    cursor.execute("DELETE FROM user WHERE student_number = '';")

    new_editeurs = mk_editeurs(cursor)
    mk_categories()
    new_series = mk_series(cursor)
    new_auteurs = mk_auteurs(cursor)
    cursor2= connections['old'].cursor()
    mk_ouvrages(cursor, new_series, new_editeurs, new_auteurs)
    mk_utilisateurs(cursor)

if __name__ == '__main__':
    mk_all()


