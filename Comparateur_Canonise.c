#include "Lib.h"

typedef struct {
	char* nom;
	char* formule;
	sparsegraph* sg;
	int *lab;
	int *ptn;
	int *orbits;
} Molecule;

//Libere la memoire allouee a une molecule
void freeMolecule(Molecule *m) {
	sparsegraph* sg = m->sg;
	if(m->nom) {
		free(m->nom);
		if(m->formule)	free(m->formule);
		if(m->sg) {
			SG_FREE(*sg);
			free(m->sg);
		}
		if(m->lab)		free(m->lab);
		if(m->ptn)		free(m->ptn);
		if(m->orbits)	free(m->orbits);
	}		
	
}

//Initialise une instance la structure Molecule
void initMolecule(Molecule* m) {
	m->nom		= NULL;
	m->formule	= NULL;
	m->sg		= NULL;
	m->lab		= NULL;
	m->ptn		= NULL;
	m->orbits	= NULL;
}

//Allocation de la memoire pour la molecule
int mallocMolecule(Molecule *m, int nv, int nde) {
	//~ printf("Initialisation d'une molecule\n");
	m->sg = malloc(sizeof(sparsegraph));
	
	m->lab = malloc(nv * sizeof(int));
	m->ptn = malloc(nv * sizeof(int));
	m->orbits = malloc(nv * sizeof(int));
	if(!(m->sg && m->lab && m->ptn && m->orbits) && nv > 0) {
		return 0;
	}
	sparsegraph* sg = m->sg;
	SG_INIT(*sg);
	
	SG_ALLOC(*sg, nv, nde * 2, "echec alloc sparsegraph");
	m->sg = sg;
	m->sg->nv = nv;
	m->sg->nde = nde * 2;
	if((!(m->sg->d && m->sg->v) && nv > 0) || (!m->sg->e && nde > 0)) {
		return 0;
	}
	//~ printf("Initialisation de la molecule reussi\n");
	return 1;
}

//Lire le fichier de molecule que genere le Parser
int lireMolecule(char *path, Molecule *m, int color, int all) {
	if(!path || !m) return 0;
	initMolecule(m);
	if(!all) printf("Lecture du fichier : %s\n",path);
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
	
	if(!mallocMolecule(m, tab[0], tab[1])) {
		printf("Erreur durant l'initialisation de la molecule\n");
		fclose(f);
		return 0;
	}
	
	for(int i = 0; i < m->sg->nv; i++) {
		result_lecture = fscanf(f,"%d %zu %d %d", &m->sg->d[i], &m->sg->v[i], &m->lab[i], &m->ptn[i]);
		if(result_lecture != 4) {	
			printf("Erreur (tableaux en colonne). Le fichier ne correspond pas au format attendu\n");
			fclose(f);
			return 0;
		}
		if(!color) { //Ne pas tenir compte de la couleur
			if(i == m->sg->nv - 1)	m->ptn[i] = 0;
			else					m->ptn[i] = 1;
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
	if(!all) printf("Lecture reussi\n");
	sortlists_sg(m->sg);
	return 1;
}

//Calcule le graphe canonisé de la molecule
int canonise(Molecule *m, optionblk* options, statsblk* stats, int all) {
	//~ printf("Canonisation de la molecule\n");
	sparsegraph* canon = NULL;
	canon = malloc(sizeof(sparsegraph));
	if(!canon) return 0;
	SG_INIT(*canon);
	sparsenauty(m->sg,m->lab,m->ptn,m->orbits,options,stats,canon);
	SG_FREE(*(m->sg));
	free(m->sg);
	m->sg = canon;
	if(!all) printf("Canonisation de la molecule reussi\n");
	return 1;
}

//Sauvegarder le graphe canonise d'une molecule (meme si la forme canonisee existe deja dans l'arborescence de fichiers)
int saveCanonise(Molecule m, char *id, int color, int all) {
	//~ printf("Sauvegarde de la canonisation\n");
	char *path;
	if(color) path = id_to_path(id, savePathC);
	else 	  path = id_to_path(id, savePath);
	if(!path) return 0;
	FILE *f = NULL;
	f = fopen(path, "w");
	if(f) {
		fprintf(f,"%s\n%s\n%d\n%zu\n\n",m.nom, m.formule, m.sg->nv, m.sg->nde);
		for(int i = 0; i < m.sg->nv; i++) {
			fprintf(f,"%d %zu\n",m.sg->d[i], m.sg->v[i]);
		}
		fprintf(f,"\n");
		for(int i = 0; i < m.sg->nde; i++) {
			fprintf(f,"%d ",m.sg->e[i]);
		}
		fclose(f);
		free(path);
		if(!all) printf("Sauvegarde de la canonisation reussi\n");
		return 1;
	}
	printf("Echec de la sauvegarde de la canonisation\n");
	free(path);
	return 0;
}

// (Read, Canonise, Save) Lit une molecule parsee, calcule sa forme canonisee et sauvegarde cette forme canonisee
int RCS(char* id, char *directory, optionblk* options, statsblk* stats, int color, int all) {
	//~ printf("Construction du chemin vers le fichier correspondant à l'identifiant\n");
	char* path = id_to_path(id, directory);
	Molecule m;
	if(lireMolecule(path,&m, color, all)){
		if(canonise(&m, options, stats, all)) {
			saveCanonise(m,id, color, all);
		}
	}
	else {
		if(path) free(path);
		return 0;
	}
	freeMolecule(&m);
	free(path);
	return 1;
}

// Canonise toutes les molecules de la base de donnee
int RCSAll(char *path, optionblk* options, statsblk* stats, int color, int all) {
	DIR * d = opendir(path);
	struct dirent *dir = NULL;
	int i = 0;
	while((dir = readdir(d)) != NULL) {
		if(isInt(dir->d_name)) {
			i++;
			printf("%6d\r",i);
			fflush(stdout);
			RCS(dir->d_name,path, options, stats, color, all);
			//~ printf("\n");
		}
	}
	closedir(d);
}

// Acquisition et activation des parametres
void optionsCanonise(char* argv, int* all, int* color) {
	int size = strlen(argv);
	if(argv[0] == '-') {
		for(int i = 1; i < size; i++) {
			switch(argv[i]) {
				case 'n' : *all = 1;		break;
				case 'c' : *color = 1; 		break;
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
	int color = 0, all = 0;
	//~ printf("Definition des parametres de nauty\n");
	DEFAULTOPTIONS_SPARSEGRAPH(options);
	options.defaultptn = FALSE;
	options.getcanon = TRUE;
	statsblk stats;
	for(int i = 1; i < argc; i++)
		if(!isInt(argv[i]))
			optionsCanonise(argv[i],&all, &color);
			
	if(!all) {
		for(int i = 1; i < argc; i++) {
			if(isInt(argv[i])) {
				if(!RCS(argv[i],Pcomplete, &options, &stats, color, all)) {
					RCS(argv[i],Plite, &options, &stats, color, all);
				}
				printf("\n");
			}
		}
	}
	else {
		printf("Canonisation de toutes les molecules en cours ...\n");
		RCSAll(Plite, &options, &stats, color, all);
		RCSAll(Pcomplete, &options, &stats, color, all);
		printf("Canonisation de toutes les molecules fini\n");
	}
}
