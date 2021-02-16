#include "Lib.h"

//Le retour doit etre free() plus tard
char* concatenate(char* s1, char* s2) {
	if(!s1 || !s2) return NULL;
	char* s3 = malloc((strlen(s1) + strlen(s2) + 1) * sizeof(char));
	strcpy(s3,s1); strcat(s3,s2);
	return s3;
}

//Compte le nombre de caracteres sur une ligne puis sauvegarde dans un tableau toute la ligne
char* read_line(FILE* f) {
	if(!f) return NULL;
	
	//Calcul de la taille de chaine de caractere a stocker
	int len = -1;
	char c;
	do {
		if(!fscanf(f,"%c",&c)) {
			return NULL;
		}
		len++;
	} while(c != '\n');
	fseek(f, -len - 1, SEEK_CUR);
	
	//Allocation de memoire
	char *line = NULL;
	line = malloc((len + 1) * sizeof(char));
	if(!line) return NULL;
	
	//Lecture de la ligne
	for(int i = 0; i < len; i++) {
		fscanf(f,"%c",&line[i]);
	}
	line[len] = '\0';
	fscanf(f,"%c",&c);
	return line;
}

//Retourne 1 si la chaine de caractere est un entier positif, 0 sinon
int isInt(char* id) {
	int size = strlen(id);
	for(int i = 0; i < size; i++) if(id[i] > '9' || id[i] < '0') return 0;
	return 1;
}

//Genere le chemin vers le fichier de la molecule selon l'identifiant
char* id_to_path(char* id, char *directory) {
	char *conc = NULL;
	conc = concatenate(directory, id);
	return conc;
}
