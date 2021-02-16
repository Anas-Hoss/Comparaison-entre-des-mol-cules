#!/usr/bin/python

import urllib.request
import gzip
import dictionnaire as dic
import os
import sys
import MoleculeClass as mol
import time

##Download##

# Recupere le nom du fichier a telecharger depuis une url
def getFileName(url):
	if url.startswith("ftp://"):
		return getFtpName(url)
	elif url.startswith("http://") or url.startswith("https://"):
		return getHttpName(url)
	else:
		return 0

# Recupere le nom du fichier a telecharger depuis une url http
def getHttpName(url):
	try:
		f = urllib.request.urlopen(url)
		filename= f.info().get_filename()
		return filename
	except:
		return 1

# Recupere le nom du fichier a telecharger depuis une url - protocole FTP
def getFtpName(url):
    lst = url.split("/")
    return lst[-1]

# Telecharge un fichier avec l'url
def download(url):
	if(mol.isInt(url)):
		url = 'https://www.ebi.ac.uk/chebi/saveStructure.do?sdf=true&chebiId=' + url + '&imageId=0'
	
	filename = getFileName(url)
	if(filename == 0):
		print("Le parseur n'a pas tenu compte de l'url '" + url + "'")
		return None
	elif(filename != 1):
		print("Telechargement de {0} ...".format(filename))
	try:
		urllib.request.urlretrieve(url, "download/" + filename)
		print("Telechargement reussi")
		return "download/" + filename
	except:
		print("Une erreur est survenue durant le telechargement de " + url);
		return None


##Traitement de fichiers##

# Decoupe les donnees par molecule
def fileProcessing(filename,update):
	print("Lecture du fichier ...")
	debut = time.time()
	if filename.endswith(".gz"):
		fileProcessingGZ(filename,update)
	elif filename.endswith(".sdf"):
		fileProcessingSDF(filename,update)
	else:
		print("Le parseur n'a pas tenu compte du fichier '" + filename.replace("download/","") + "'")
	print("Duree totale du traitement en secondes : "  + str(time.time() - debut))

# Decoupe les donnees (d'un fichier SDF compresse au format gz) par molecule
def fileProcessingGZ(filename,update):
	i = 0
	the_file = gzip.open(filename, 'rb')
	content = []
	for line in the_file:
		content.append(line.decode())
		if(line.decode().startswith("$$$$")):
			#traitement de la molecule
			dataProcessing(content,update)
			##########################
			i += 1
			content = []
	the_file.close()
	print(str(i) + " molecules trouvees")

# Decoupe les donnees (d'un fichier SDF) par molecule
def fileProcessingSDF(filename, update):
	with open(filename,"r") as molFile:
		content = []
		for line in molFile:
			content.append(line)
			if(line.startswith("$$$$")):
				#traitement de la molecule
				dataProcessing(content, update)
				##########################
				content = []

# Attribue une couleur à un atome avec le dictionnaire
def donnerCouleur(atome):
	if(atome in dic.colors.keys()):
		return dic.colors[atome]
	else:
		print("Cle : \"" + atome + "\" non repertoriee dans le dictionnaire")
		return 0

# Retire des multiples espaces pour en laisser un seul 
def supprimerEspaces(line):
	while "  " in line:
		line = line.replace("  ", " ")
	return line

# Si le nombre d'atomes et d'aretes sont colles alors on identifie ou se situe la separation, sinon ils sont lues l'un apres l'autre
def getDimensions(line):
	a = 0; b = 0
	# Les deux nombres sont superieurs a 99
	if(len(line[0]) == 6):
		a = int(line[0][0] + line[0][1] + line[0][2])
		b = int(line[0][3] + line[0][4] + line[0][5])
	# Le nombre d'aretes est superieur a 100 mais pas le nombre d'atomes
	elif(len(line[0]) == 5):
		# Le nombre d'atomes est inferieur a 100
		a = int(line[0][0] + line[0][1])
		b = int(line[0][2] + line[0][3] + line[0][4])
	# Le nombre d'atomes est inferieur a 100
	elif(len(line[0]) == 4):
		a = int(line[0][0])
		b = int(line[0][1] + line[0][2] + line[0][3])
	# Les deux nombres ont une separation
	else:
		a = int(line[0])
		b = int(line[1])
	return a,b

# Decalage des indices apres suppression des hydrogenes
def soustractionH(indice, numero_H):
	i = 0
	for indiceH in numero_H:
			if(indiceH < indice):
				i += 1
	return indice - i

# Traitement des donnees d'une seule molecule
def dataProcessing(strMol,update):
	id_problem = False
	m = mol.molecule()
	i = 0
	nb_aretes = 0
	nb_sommets = 0
	numero_H = []
	# Tant que toutes les lignes n'ont pas ete utilises
	while i < len(strMol):
		if("V2000" in strMol[i]):
			line = supprimerEspaces(strMol[i].strip()).split(" ")
			nb_sommets, nb_aretes = getDimensions(line)
			i += 1
			for j in range(nb_sommets): # lecture des atomes places en colonne 4 sur la ligne
				line = supprimerEspaces(strMol[i].strip()).split(" ")
				color = donnerCouleur(line[3])
				if(color == 0):
					id_problem = True
				if(color != 1):
					m.colorerSommet(j - len(numero_H), color)
				else:
					numero_H.append(j)
				i += 1
			nb_sommets -= len(numero_H)
			m.setNb_sommets(nb_sommets)
			for j in range(nb_aretes):
				line = supprimerEspaces(strMol[i].strip()).split(" ")
				a = 0; b = 0;
				if(len(line) == 7):
					a = int(line[0])-1
					b = int(line[1])-1
				elif(len(line) == 6): #les indices sur les aretes sont collés
					a,b = getDimensions(line)
					a -= 1
					b -= 1
				if(not(a in numero_H or b in numero_H)): #garder seulement les aretes non lies aux hydrogenes
						m.ajoutArete(soustractionH(a, numero_H), soustractionH(b, numero_H), line[2])
				
				i += 1
		elif ("> <name>" in strMol[i].lower() or "> <chebi name>" in strMol[i].lower()):
			i += 1
			m.nom = strMol[i].rstrip('\n')
		elif ("formula" in strMol[i].lower()):
			i += 1
			m.formule = strMol[i].rstrip('\n')
		elif ("> <chebi id>" in strMol[i].lower() or "> <id>" in strMol[i].lower()):
			i += 1
			m.chebiID = strMol[i].rstrip('\n').lower().replace("chebi:","")
			
		i += 1
		
	if(id_problem):
		print("La molécule " + str(m.chebiID) + " contient un atome inconnu")
	m.save(update)

# Traitement des arguments
def argvProcessing():
	update = False
	if(len(sys.argv) > 1):
		for arg in sys.argv[1:]:
			if(arg.lower() in "-u"):
				update = True
				print("Update active")
		for arg in sys.argv[1:]:
			if(not(arg.lower() in "-u")):
				filename = download(arg)
				if(not(filename == None)):
					fileProcessing(filename,update)

# Demarrage du programme
def main():
	debut = time.time()
	argvProcessing()
	print("Temps total en secondes : " + str(time.time() - debut) + "\n")
main()
