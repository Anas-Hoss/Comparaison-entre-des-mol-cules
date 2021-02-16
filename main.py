#!/usr/bin/python

import os
import webbrowser

# Commandes pour le Parser
def parser(reponse, lower, racine = 1):
	lower = reponse.lower()
	if(racine) :
		os.chdir("./Parser")
	if(lower == "parse all"):
		os.system("python3 Parser.py -u 'ftp://ftp.ebi.ac.uk/pub/databases/chebi/SDF/ChEBI_complete.sdf.gz'")
	elif(lower == "parse 3star"):
		os.system("python3 Parser.py -u 'ftp://ftp.ebi.ac.uk/pub/databases/chebi/SDF/ChEBI_complete_3star.sdf.gz'")
	elif(lower.startswith("parse")):
		os.system("python3 Parser.py " + reponse[6:])
	if(racine) :
		os.chdir("..")

# Commandes pour la Canonisation
def canonise(reponse, lower, racine = 1):
	lower = reponse.lower()
	if(racine) :
		os.chdir("./Comparateur")
	
	if(not os.path.exists("Canonise") and lower.startswith("canonise")):
		os.system("./comp.sh")
		
	if(lower == "canonise all"):
		print("Avec coloration des atomes : ")
		os.system("./Canonise -nc")
		print("Sans coloration des atomes : ")
		os.system("./Canonise -n")
	elif(lower.startswith("canonise ")):
		os.chdir("../Parser")
		reponse_split = reponse[9:].split(" ")
		tab = ""
		for arg in reponse_split:
			try:
				int(arg)
				if(not (os.path.exists("./complete/" + arg) or os.path.exists("./lite/" + arg))):
					tab = tab + " " + arg
			except:
				None
		tab = tab.strip()
		if(len(tab) > 0):
			os.system("python3 Parser.py " + tab)	
		os.chdir("../Comparateur")	
		print("Sans couleur :")
		os.system("./Canonise " + reponse[9:])
		print("Avec couleur :")
		os.system("./Canonise -c " + reponse[9:])
	if(racine) :
		os.chdir("..")

# Commandes pour la Comparaison de molecules
def compare(reponse, lower, racine = 1):
	lower = reponse.lower()
	if(racine) :
		os.chdir("./Comparateur")
	
	if(not os.path.exists("Compare") and lower.startswith("compare")):
		os.system("./comp.sh")
		
	if(lower.startswith("compare ")):
		reponse_split = reponse[8:].split(" ")
		tab = ""
		for arg in reponse_split:
			try:
				int(arg)
				if(not (os.path.exists("./canon/" + arg) and os.path.exists("./canonC/" + arg))):
					tab = tab + " " + arg
			except:
				None
		tab = tab.strip()
		if(len(tab) > 0):
			canonise("canonise " + tab, "canonise " + tab, 0)
		os.system("./Compare " + reponse[8:])
	if(racine) :
		os.chdir("..")

# Commandes pour nettoyer les repertoires de fichiers
def clean(lower):
	if(lower.strip() == "clean"):
		os.chdir("./Parser")
		os.system("./clean.sh")
		os.chdir("../Comparateur")
		os.system("./clean.sh")
		os.chdir("..")
		print("Nettoyage fini")
	else:
		lower_split = lower.split()
		clean_parser = False
		clean_comparateur = False
		for i in range(1,len(lower_split)):
			if(lower_split[i] == "parser"):
				clean_parser = True
			elif(lower_split[i] == "comparateur"):
				clean_comparateur = True
		if(clean_parser):
			os.chdir("./Parser")
			os.system("./clean.sh")
			os.chdir("..")
		if(clean_comparateur):
			os.chdir("./Comparateur")
			os.system("./clean.sh")
			os.chdir("..")
			print("Nettoyage fini")

def openM(reponse):
	if(reponse.startswith("open ")):
		print("Votre navigateur internet va acceder aux molecules souhaites dans quelques instants...")
		reponse_split = reponse.split()
		for arg in reponse_split:
			try:
				if(int(arg) > 0):
					webbrowser.open("https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:" + arg)
			except:
				None

# Affiche l'aide pour savoir quels sont les commandes disponibles
def _help(lower):
	if(lower == "help"):
		print("Commandes disponibles :")
		print("'parse all'\t\tTelecharger toute la base de donnee")
		print("'parse 3star'\t\tTelecharger toutes les molecules 3-Star")
		print("'parse id'\t\tTelecharger les molecules correspondant aux identifiants specifies\n")
		print("'canonise all'\t\tCalcule les formes canonises avec et sans couleur de toutes les molecules telecharges")
		print("'canonise id'\t\tCalculer les formes canonises avec et sans couleur des molecules specifies par leur identifiant\n\n")
		print("'compare id'\t\tCompare les formes canonises des molecules specifies par leur identifiant")
		print("Options disponibles pour 'compare' : ")
		print("'-c'\t\t\tTenir compte de la couleur des atomes")
		print("'-f'\t\t\tComparer les formules brutes")
		print("'-a'\t\t\tAfficher les resultats indiquant que 2 molecules ne sont pas isomorphes")
		print("'-n'\t\t\tChaque molecule specifie par son identifiant sera comparee avec toutes les molecules deja canonises\n\n")
		print("'clean'\t\t Supprime tous les fichiers generes (molecules telecharges, formes canonises, ...")
		print("Options disponibles pour 'clean' : ")
		print("'parser'\t\t supprimer la base de donnees")
		print("'comparateur'\t\t Supprimer les fichiers de molecules avec leur forme canonise et les fichiers resultant de la compilation\n\n")
		print("'open id'\t\tOuvrir sur le navigateur la page web de la molecule pour la visualiser\n\n")
		print("Les commandes Linux 'clean' et 'reset' sont disponibles pour nettoyer les ecritures dans le terminal.")
		print("Pour plus d'informations, consultez le manuel utilisateur.")
		
# Demmarage du programme
def command():
	reponse = ""
	while(not reponse.strip().lower() == "exit"):
		reponse = input("Entrez une commande :\n> ")
		lower = reponse.lower()
		parser(reponse, lower)
		canonise(reponse, lower)
		compare(reponse, lower)
		clean(lower)
		_help(lower)
		openM(lower)
		if(reponse == "reset" or reponse == "clear"):
			os.system(reponse)

command()
