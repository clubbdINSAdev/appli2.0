from django.db import models

# Create your models here.
class Editeur(models.Model):
    nom = models.CharField(unique=True, max_length=64)

class Tag(models.Model):
    tag = models.CharField(max_length=64)

class Ouvrage(models.Model):
    isbn = models.IntegerField(null=True)
    ean = models.IntegerField(null=True)
    cote =  models.CharField(max_length=10, primary_key=True)
    titre = models.CharField(max_length=64, null=True)
    description = models.TextField(null=True)
    date_entree = models.DateField(null=True)
    editeur = models.ForeignKey(Editeur, null=True)
    is_manga = models.BooleanField()
    tags = models.ManyToManyField(Tag)
    empruntable = models.BooleanField()

class Utilisateur(models.Model):
    id = models.BigIntegerField(primary_key=True)
    nom = models.CharField(max_length=64)
    prenom = models.CharField(max_length=64)
    mail = models.EmailField(null=True)
    telephone = models.CharField(max_length=64, null=True)
    adresse = models.TextField(null=True)

class Authentification(models.Model):
    login = models.CharField(max_length=64, unique=True)
    hash = models.CharField(max_length=512, blank=False)
    salt = models.CharField(max_length=512, blank=False)
    utilisateur = models.ForeignKey(Utilisateur)

class Categorie(models.Model):
    prefix = models.IntegerField(primary_key=True)
    nom = models.CharField(unique=True, max_length=64)

class Serie(models.Model):
    nom = models.CharField(max_length=64)
    prefix = models.CharField(max_length=6)
    categorie = models.ForeignKey(Categorie)

class OneShot(Ouvrage):
    categorie = models.ForeignKey(Categorie)

class Volume(Ouvrage):
    serie = models.ForeignKey(Serie)
    numero = models.IntegerField()

class Emprunt(models.Model):
    utilisateur = models.ForeignKey(Utilisateur)
    ouvrage = models.ForeignKey(Ouvrage, unique=True)
    date = models.DateField()

class Historique(models.Model):
    utilisateur = models.ForeignKey(Utilisateur)
    ouvrage = models.ForeignKey(Ouvrage)
    date_deb = models.DateField()
    duree = models.BigIntegerField()

class Plan(models.Model):
    nom = models.CharField(unique=True, max_length=64)
    nb_ouvrage = models.BigIntegerField()
    duree = models.BigIntegerField()
    prix = models.BigIntegerField()

class Abonnement(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, unique=True)
    plan = models.ForeignKey(Plan)
    date_deb = models.DateField()

class AbonnementHistorique(models.Model):
    utilisateur = models.ForeignKey(Utilisateur)
    plan = models.ForeignKey(Plan)
    date_deb = models.DateField()

class Avis(models.Model):
    note = models.BigIntegerField(null=True)
    critique = models.TextField(null=True)
    utilisateur = models.ForeignKey(Utilisateur)

class AvisSerie(Avis):
    serie = models.ForeignKey(Serie)

class AvisOuvrage(Avis):
    ouvrage = models.ForeignKey(Ouvrage)

class Poste(models.Model):
    nom = models.CharField(unique=True, max_length=64)
    droits = models.BigIntegerField()

class Actif(models.Model):
    utilisateur = models.ForeignKey(Utilisateur)
    poste = models.ForeignKey(Poste)
