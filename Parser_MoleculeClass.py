#!/usr/bin/python

import os
from collections import OrderedDict

liteStr = "lite/"
completeStr = "complete/"

class molecule:
	def __init__(self):
		self.nb_sommets = 0
		self.aretes = []
		self.colorsSommets = {}
		self.formule = "undefined"
		self.nom = "undefined"
		self.chebiID = -1
		self.degre = []
		self.v = []
		self.e = []
		self.lab = []
		self.ptn = []
	
	# Ajoute une arete a la liste et met a jour le tableau d des degre de Nauty
	def ajoutArete(self, depart, arrivee, typeLiaison):
		self.aretes.append(str(depart) + " " + str(arrivee) + " " + str(typeLiaison))
		
		self.degre[depart] += 1
		self.degre[arrivee] += 1
	
	# Ajoute dans le dictionnaire de couleurs de la molecule la couleur d'un atome
	def colorerSommet(self, sommet, color):
		self.colorsSommets[str(sommet)] = color
	
	# Initialisation de variables de la molecule grace au nombre de sommets
	def setNb_sommets(self, n):
		self.nb_sommets = n
		for i in range(self.nb_sommets):
			self.degre.append(0)
			self.v.append(0)
	
	# Cree une chaine de caractere dont le contenu est fait selon le format de fichier choisit
	def toString(self):
		string = ""
		string += self.nom + "\n"
		string += self.formule + "\n"
		string += str(self.nb_sommets) + "\n"
		string += str(len(self.aretes)) + "\n"
		string += "\n"
		
		for i in range(self.nb_sommets): 
			string += str(self.degre[i]) 
			string += " " + str(self.v[i]) 
			string += " " + str(self.lab[i]) 
			string += " " + str(self.ptn[i]) + "\n"
		string += "\n"
		
		for a in self.e:
			string += str(a) + " "
		string = string.rstrip()
		return string
	
	# Calcule et formate les informations manquantes ou potentiellement incorrectes puis sauvegarde la molecule parsee pour Nauty
	def save(self, overwrite):
		
		self.partitionner()
		self.sparsenautyAretes()
		self.formule = formaterFormule(self.formule)
		
		strSave = ""
		if("undefined" in self.formule):
			strSave = liteStr + str(self.chebiID)
		else:
			strSave = completeStr + str(self.chebiID)
		
		if(overwrite or os.path.exists(strSave) == False):
			with open(strSave, "w") as molFile:
				molFile.write(self.toString())
	
	# Calcule le contenu des tableaux v et e pour Nauty
	def sparsenautyAretes(self):
		if(self.nb_sommets > 0):
			self.v[0] = 0;
			n = [0]
			for i in range(1,self.nb_sommets):
				self.v[i] = self.v[i-1] + self.degre[i-1]
				n.append(0)
				
			for i in range(len(self.aretes)*2):
				self.e.append(0)
			
			for i in range(len(self.aretes)):
				tmp = self.aretes[i].split(" ")
				tmpv1 = int(tmp[0])
				tmpv2 = int(tmp[1])
				self.e[self.v[tmpv1]+n[tmpv1]] = tmpv2
				self.e[self.v[tmpv2]+n[tmpv2]] = tmpv1
				n[tmpv1] += 1
				n[tmpv2] += 1
	
	# Calcule le contenu des tableaux lab et ptn pour Nauty
	def partitionner(self):
		colors = []
		for k,v in self.colorsSommets.items():
			if(v not in colors):
				colors.append(v)
		colors = sorted(colors)
		for c in colors:
			for i in range(self.nb_sommets):
				if(self.colorsSommets[str(i)] == c):
					self.lab.append(i)
					self.ptn.append(1)
			self.ptn[-1] = 0
		

# Retourne vrai si le parametre character est un entier, faux sinon
def isInt(character):
	try:
		character = int(character)
		return True
	except:
		return False

# Retourne vrai si le caractere est une lettre majuscule, faux sinon
def isUpper(character):
	nb = ord(character)
	if(nb >= ord('A') and nb <= ord('Z')):
		return True
	else:
		return False

# trie par ordre alphabetique d'atomes
# exemples :
# 	C5H10O2; (C3H6O.C2H4O)n => C5H10O2  
# 	C9H11N2O4SR 			=> C9H11N2O4RS
def formaterFormule(formule):
	if(formule in "undefined"):
		return formule
	
	# Separation
	formate = {}
	atome = ""
	nombre = ""
	lettre = True
	for i in range(len(formule)):
		c = formule[i]
		
		if(isInt(c)):
			nombre += c
			lettre = False
		else:
			if(not lettre):
				formate[atome] = nombre
				nombre = ""
				atome = ""
			elif(isUpper(c)):
				formate[atome] = ""
				nombre = ""
				atome = ""
			if(ord(c) == ord(';')):
				break; 
			atome += c
			lettre = True	
	if(isInt(c)):
		formate[atome] = nombre
	else:
		formate[atome] = ""
	
	# Trie et remise en chaine de caractere
	formate = OrderedDict(sorted(formate.items(), key=lambda t: t[0]))
	formule = ""
	for k,v in formate.items():
		formule += k + v
	return formule.strip()
