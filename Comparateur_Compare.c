#include "Lib.h"

int cpt_iso = 0;

typedef struct {
	char* id; //ne doit pas etre free()
	char* nom;
	char* formule;
	sparsegraph* sg;
} Graphe;

//Libere la memoire allouee a une molecule
void freeGraphe(Graphe *m) {
	sparsegraph* sg = m->sg;
	if(m->nom) {
		free(m->nom);
		if(m->formule)	free(m->formule);
		if(m->sg) {
			SG_FREE(*sg);
			free(m->sg);
		}
	}
}

//Initialise une instance la structure Graphe
void initGraphe(Graphe *m) {
	m->nom		= NULL;
	m->formule	= NULL;
	m->sg		= NULL;
}

//Allocation de la memoire pour le graphe
int mallocGraphe(Graphe *m, int nv, int nde) {
	//~ printf("Initialisation d'un graphe\n");
	m->sg = malloc(sizeof(sparsegraph));
	
	sparsegraph* sg = m->sg;
	SG_INIT(*sg);
	
	SG_ALLOC(*sg, nv, nde, "echec alloc sparsegraph");
	m->sg = sg;
	m->sg->nv = nv;
	m->sg->nde = nde;
	if((!(m->sg->d && m->sg->v) && nv > 0) || (!m->sg->e && nde > 0)) {
		return 0;
	}
	//~ printf("Initialisation du graphe reussi\n");
	return 1;
}

//Lire le fichier du graphe canonise
int lireGraphe(char *path, Graphe *m) {
	if(!path || !m) return 0;
	initGraphe(m);
	//~ printf("Lecture du fichier : %s\n",path);
	FILE *f = NULL;
	f = fopen(path,"r");
	if(!f) {
		printf("Impossible d'acceder au fichier %s\n",path);
		return 0;
	}
	int tab[2];
	int result_lecture = 0;
	m->nom     = read_line(f);
	m->formule = read_line(f);
	if(!(m->nom && m->formule)) {
		printf("Erreur (nom, formule). Le fichier ne correspond pas au format attendu\n");
		fclose(f);
		return 0;
	}
	result_lecture += fscanf(f,"%d",&tab[0]);
	result_lecture += fscanf(f,"%d",&tab[1]);
	if(result_lecture != 2) {
		printf("Erreur (dimensions). Le fichier ne correspond pas au format attendu\n");
		fclose(f);
		return 0;
	}
	
	if(!mallocGraphe(m, tab[0], tab[1])) {
		printf("Erreur durant l'initialisation du graphe\n");
		fclose(f);
		return 0;
	}
	
	for(int i = 0; i < m->sg->nv; i++) {
		if(fscanf(f,"%d %zu",&m->sg->d[i], &m->sg->v[i]) != 2) {
			printf("Erreur (tableaux en colonne). Le fichier ne correspond pas au format attendu\n");
			fclose(f);
			return 0;
		}
	}
	
	for(int i = 0; i < m->sg->nde; i++) {
		if(!fscanf(f, "%d", &m->sg->e[i])) {
			printf("Erreur (tableau e). Le fichier ne correspond pas au format attendu\n");
			fclose(f);
			return 0;
		}
	}
	
	fclose(f);
	//~ printf("Lecture reussi\n");
	return 1;
}

// Compare 2 formes canoniques de molecules
int compare(Graphe g1, Graphe g2, int formule, int affiche) {
	if(formule) {
		if(!strcmp("undefined",g1.formule)) printf("Attention ! Formule non defini pour %s\n",g1.id);
		if(!strcmp("undefined",g2.formule)) printf("Attention ! Formule non defini pour %s\n",g2.id);
		if(!strcmp(g1.formule, g2.formule)) {
			if(aresame_sg(g1.sg, g2.sg)) {
				printf("%s - %s = [Y]\n\n", g1.id, g2.id);
				return 1;
			}
		}
	} else {
		if(aresame_sg(g1.sg, g2.sg)) {
			printf("%s - %s = [Y]\n\n", g1.id, g2.id);
			return 1;
		}
	}
	if(affiche) printf("%s - %s = [N]\n\n", g1.id, g2.id);
	return 0;
}

// Pour tous les couples d'identifiants possibles, la comparaison est faite pour chaque couple d'identifiant
void compareGraphes(Graphe *graphes, int graphes_sz, int formule, int affiche) {
	if(graphes_sz < 2) printf("Erreur : Le nombre de molecules a comparer n'est pas d'au moins 2\n");
	for(int i = 0; i < graphes_sz - 1; i++)
		for(int j = i + 1; j < graphes_sz; j++)
			cpt_iso += compare(graphes[i],graphes[j], formule, affiche);
}

// Pour chaque identifiant donne, la molecule associee sera comparee a toutes les autres qui ont deja ete canonises
void compareGraphesWithAll(Graphe *graphes, int graphes_sz, int formule, int color, int affiche) {
	printf("Comparaison avec toutes les molecules canonises\n");
	DIR * d;
	char *path, *molPath;
	path = (color)? savePathC : savePath;
	d = opendir(path);
	struct dirent *dir = NULL;
	for(int i = 0; i < graphes_sz; i++) {
		while((dir = readdir(d)) != NULL) {
			if(isInt(dir->d_name)) {
				Graphe g;
				g.id = dir->d_name;
				molPath = id_to_path(g.id, path);
				if(lireGraphe(molPath, &g)) {
					cpt_iso += compare(graphes[i],g, formule, affiche);
				}
				if(molPath) free(molPath);
			}
		}
		if(i != graphes_sz - 1) rewinddir(d);
	}
	closedir(d);
}

// Acquisition et activation des parametres
void optionsComparaison(char* argv, int* all, int* formule, int* color, int *affiche) {
	int size = strlen(argv);
	if(argv[0] == '-' && strlen(argv) > 1) {
		for(int i = 1; i < size; i++) {
			switch(argv[i]) {
				case 'n' : *all = 1;		break;
				case 'f' : *formule = 1; 	break;
				case 'c' : *color = 1; 		break;
				case 'a' : *affiche = 1; 	break;
				default  : printf("Erreur : Option \"%c\" non valable\n", argv[i]); exit(0); break;
			}
		}
	}
	else {
		printf("Erreur : Argument inconnu\n");
		exit(0);
	}
}

int main(int argc, char* argv[]) {
	int grapheCpt = argc - 1;
	int all = 0, formule = 0, color = 0, affiche = 0;
	for(int i = 1; i < argc; i++) {
		if(!isInt(argv[i])) {
			grapheCpt--;
			optionsComparaison(argv[i],&all, &formule, &color, &affiche);
		}
	}
	Graphe *graphes = NULL;
	graphes = malloc(grapheCpt * sizeof(Graphe));
	if(!graphes) {
		printf("Echec d'allocation de memoire\n");
		exit(0);
	}
	int k = 0;
	for(int i = 1; i < argc && k < grapheCpt; i++) {
		if(isInt(argv[i])) {
			//~ printf("Construction du chemin vers le fichier correspondant à l'identifiant\n");
			char* path;
			if(color) 	path = id_to_path(argv[i], savePathC);
			else 		path = id_to_path(argv[i], savePath);
			
			if(!lireGraphe(path, &graphes[k++])){
				k--;
				grapheCpt--;
			}
			else {
				graphes[k-1].id = argv[i];
			}
			if(path) free(path);
		}
	}
	printf("\n");
	if(all) compareGraphesWithAll(graphes, grapheCpt, formule, color, affiche);
	else compareGraphes(graphes, grapheCpt, formule, affiche);
	free(graphes);
	
	if(!cpt_iso) printf("Aucun resultat positif\n");
}
