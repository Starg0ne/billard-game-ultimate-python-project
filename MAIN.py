# Créé par Louis Miramond, Bastien HAM, Tomi, Dawid Ameline, Romain ; dernière modif : 28/03/2025 en Python 3.7

# ========================
# SOMMAIRE
# ========================

# 1 Importations
# 2 Paramètres de la fenêtre
# 3 Couleurs format RVB
# 4 Création des variables
# 5 Création de la fenêtre
# 6 Initialisation des fonds écrans + des polices
# 7 Initialisation des sons
# 8 Création de la classe pour les boules de billard
# 9 Fonction Choc
# 10 Fonction création des boules
# 11 Fonction affichage des textes
# 12 Modification des pseudos
# 13 Admin mod, for fun !
# 14 Modification volume son
# 14.1 Animation début (Merci Gemini !)
# 15 Modification des couleurs
# 16 Caracteristiques des textes (police, taille)
# 17 Création des boutons
# 18 Etat de base des différents écrans
# 19 Boucle principale
# 20 Menu
# 21 Pré lancement
# 22 Règles
# 23 Paramètres
# 24 End Game Billard
# 25 Running
# 26 Error
# 27 Admin Page
# 28 ScoreBoard + suppression score


# ========================
# FIN SOMMAIRE
# ========================


# --- Importation des modules ---
import pygame, math, time, tkinter  as tk
from tkinter import simpledialog
from math import *
import os
import sys
import time
import json
from datetime import datetime
import random

# --- Fonction chargement des fichiers ---
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # If running as a script, base_path is the current directory
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Initialisation de Pygame
pygame.init()


# Paramètres de la fenêtre
LARGEUR, HAUTEUR = 941, 570


# Couleurs au format RVB
blanc = (200, 200, 200)
noir = (0, 0, 0)
rouge = (255, 0, 0)
jaune = (204, 153, 0)
jaune_clair = (255, 255, 153)
vert = (0, 255, 0)
bleu = (0, 0, 255)
orange = (255, 165, 0)
violet = (128, 0, 128)
bleu_fonce = (0, 0, 50)
bleu_clair = (100, 100, 255)
marron = (101, 67, 33)
gris = (50, 50, 50)
coul_ad4 = jaune


# Création des variables
rayon = 10                   # rayon boule
friction = 0.99              # réduction vitesse
tour = 1                     # nb tour d'un joueur
nbr_colision = -1            # nb colision
force_max = 15               # force max d'une boule
GAME_FOND = 0                # couleur du fond
delay = 10                   # delai entre chaque affichage
joueur = 1                   # joueur actif
rebond = 0.9                 # perte vitesse si rebond

clic_son_parametres = False  # état du slider son paramètre

pseudo1 = "Joueur_1"         # Pseudo du Joueur 1
pseudo2 = "Joueur_2"         # Pseudo du Joueur 2

vol_txt = "100"              # Affichage du volume actuel
vol = 100                    # Volume actuel

GAME_NAME = "Billard_Ultimate"                        # Nom du jeu
RELEASE_DATE = "28 Mars 2025"                         # Date de création
CREATOR_NAME = "LOUIS  BASTIEN  TOMI  ROMAIN  DAVID"  # Createur

FIRST_LAUNCH = True                                   # Premier lancement du jeu : pour l'animation

scroll_offset = 0
SCORE_LINE_HEIGHT = 25 # Hauteur d'une ligne de score en pixels (à ajuster selon la taille de votre police)
MAX_VISIBLE_SCORES = 10 # Nombre maximum de scores visibles simultanément (à ajuster)


# Création de la fenêtre
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Billard-Ultimate")


# Définition du chemin de base pour les ressources
if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))



# --- Chargement des données extérieurs du code ---

# image fond écran
fond = pygame.image.load(resource_path('data/image/img_table_billard.jpg'))
fond2 = pygame.image.load(resource_path('data/image/img_billard.jpg'))
fond3 = pygame.image.load(resource_path("data/image/img_billard_NB.jpg"))
fond4 = pygame.image.load(resource_path("data/image/img_uni.jpg"))
fond4 = pygame.transform.scale(fond4, (LARGEUR, HAUTEUR))
fond6 = pygame.image.load(resource_path("data/image/img_erreur404.jpg"))

# caracteristiques des txt (police, taille)
police_casino1 = pygame.font.Font(resource_path("data/police/police_casino.otf"), 50)
police_casino2 = pygame.font.Font(resource_path("data/police/police_casino.otf"), 20)
police_casino3 = pygame.font.Font(resource_path("data/police/police_casino.otf"), 30)

# initialisation des sons
pygame.mixer.init()
son_rebond = pygame.mixer.Sound(resource_path("data/son/son_colision.wav"))
son_trou = pygame.mixer.Sound(resource_path("data/son/son_trou.wav"))
son_bouton = pygame.mixer.Sound(resource_path("data/son/son_bouton1.wav"))
son_mur = pygame.mixer.Sound(resource_path("data/son/son_mur.mp3"))

# Chemin du fichier de sauvegarde des scores
if getattr(sys, 'frozen', False):
    scores_folder = os.path.dirname(sys.executable)
else:
    scores_folder = os.path.dirname(os.path.abspath(__file__))

SCORES_FILE = os.path.join(scores_folder, "scores.json")

# volume
son_mur.set_volume(1)
son_bouton.set_volume(0.4)

# liste des sons
son_liste = [son_bouton, son_rebond, son_trou, son_mur]    # création d'une liste pour gérer tout les sons



# --- Création de la classe pour les boules de billard ---
class Boule:
    def __init__(self, x, y, couleur, ind):
        self.x = x
        self.y = y
        self.couleur = couleur
        self.ind = ind

        self.angle = 0
        self.vitesse_x = 0
        self.vitesse_y = 0

    def deplacement(self):
        global tour, joueur, nbr_colision # permet d'utiliser des variables créer hors de la classe

        # deplacement de la boule
        self.x += self.vitesse_x
        self.y += self.vitesse_y

        # rebond sur les murs
        if self.x >= 855 and 90 < self.y < 410:             # mur droit
            self.vitesse_x = -abs(self.vitesse_x)* rebond
            self.vitesse_y *= rebond
            son_mur.play()

        elif self.x <= 86 and 90 < self.y < 410:            # mur gauche
            self.vitesse_x = abs(self.vitesse_x)* rebond
            self.vitesse_y *= rebond
            son_mur.play()

        elif self.y >= 415 and (90 < self.x < 460 or 475 < self.x < 850):   # mur bas
            self.vitesse_y = -abs(self.vitesse_y)* rebond
            self.vitesse_x *= rebond
            son_mur.play()

        elif self.y <= 85 and (90 < self.x < 460 or 475 < self.x < 830):    # mur haut
            self.vitesse_y = abs(self.vitesse_y)* rebond
            self.vitesse_x *= rebond
            son_mur.play()

        # Détection de si la balle rentre dans le trou ou non.
        lst = [[66, 66], [476, 66], [875, 66], [66, 437], [470, 437], [875, 437]]
        for element in lst:
            dist = sqrt((element[0]-self.x)**2 + (element[1]-self.y)**2)
            sorti = self.exterieur()
            if dist < 22 or sorti:
                self.vitesse_x = 0
                self.vitesse_y = 0
                if self.couleur == blanc:   # Si la blanche rentre
                    self.x = 250
                    self.y = 250
                    tour = 2
                    if nbr_colision != 0:
                        joueur = 2 if joueur == 1 else 1

                elif self.couleur == noir:   # Si la noir rentre
                    return "ENDGAME"

                elif self.couleur == jaune:    # si la jaune rentre
                    self.x = 1000
                    self.couleur = bleu_clair
                    son_trou.play()
                    return "1j"

                elif self.couleur == rouge:   # si la rouge rentre
                    self.x = 1000
                    self.couleur = bleu_clair
                    son_trou.play()
                    return "2j"

        # ralentissement du au frotement
        dist = math.sqrt(self.vitesse_x**2 + self.vitesse_y**2)
        if dist >= 0.5:
            self.vitesse_x *= friction
            self.vitesse_y *= friction

        # arrêt si la boule est trop lente
        else:
            self.vitesse_x = 0
            self.vitesse_y = 0


    def exterieur(self): # si une boule sort à l'extérieur du terrain
        if (self.x >= 870 or self.x <= 70 or self.y >= 435 or self.y <= 65) and (self.vitesse_x != 0 and self.vitesse_y != 0):
            return True


    def colision(self, autre):
        global tour, joueur, nbr_colision, j1_point, j2_point, nbCoups

        dx = autre.x - self.x # distance absisse entre les deux boules
        dy = autre.y - self.y # distance ordonnée entre les deux boules
        distance = math.sqrt(dx**2 + dy**2) # distance entre les deux boules

        if distance < 2 * rayon:  # Si les boules se touchent
            if nbr_colision == 0 and nbCoups > 0:
                if (joueur == 1 and autre.couleur == rouge) or (joueur == 2 and autre.couleur == jaune) or (joueur == 1 and autre.couleur == noir and j1_point != 7) or (joueur == 2 and autre.couleur == noir and j2_point != 7): # si la premiere boule touché n'est pas sa couleur
                    tour = 2                                                                             # alors le joueur adverse à 2 tour
                    joueur = 1 if joueur == 2 else 2                                                     # changement de joueur
            nbr_colision += 1   # compte le nombre de colision

            son_rebond.play() # son du choc

            if distance == 0:    # Évite la division par zéro
                distance = 0.01  # Petite valeur pour forcer la séparation

            # Normalisation du vecteur de collision
            nx, ny = dx / distance, dy / distance

            # Calcul de la vitesse relative dans la direction du choc
            dvx = self.vitesse_x - autre.vitesse_x
            dvy = self.vitesse_y - autre.vitesse_y
            impact = dvx * nx + dvy * ny  # Projection des vitesses

            if impact > 0:  # Vérifie que les boules se rapprochent
            # Échange des vitesses selon l'axe de collision (conservation de la quantité de mouvement)
                self.vitesse_x -= impact * nx
                self.vitesse_y -= impact * ny
                autre.vitesse_x += impact * nx
                autre.vitesse_y += impact * ny

            # Correction de l'empilement
            overlap = (2 * rayon - distance) / 2
            self.x -= overlap * nx
            self.y -= overlap * ny
            autre.x += overlap * nx
            autre.y += overlap * ny

    def jouer(self):
        global force_max, force, angle

        self.vitesse_x = -force * math.cos(angle)
        self.vitesse_y = -force * math.sin(angle)

# --- fin class Boule ---


# Fonction Choc
def choc(boule):
    for idex in range(len(liste)):
        if idex != boule.ind:
            boule.colision(liste[idex])


# création des boules
def creation_boule():
    return [Boule(250, 250, blanc, 0),
             Boule(650, 250, rouge, 1),
             Boule(668, 239, rouge, 2),
             Boule(668, 260, jaune, 3),
             Boule(686, 229, jaune, 4),
             Boule(686, 250, noir, 5),
             Boule(686, 270, rouge, 6),
             Boule(704, 219, rouge, 7),
             Boule(704, 239, jaune, 8),
             Boule(704, 260, rouge, 9),
             Boule(704, 280, jaune, 10),
             Boule(722, 209, jaune, 11),
             Boule(722, 229, rouge, 12),
             Boule(722, 249, jaune, 13),
             Boule(722, 269, jaune, 14),
             Boule(722, 289, rouge, 15)]


# Fonction affichage des textes
def afficher_texte(txt, police, couleur, surface, x, y):
    texte = police.render(txt, True, couleur)
    rect_texte = texte.get_rect(center=(x, y))
    surface.blit(texte, rect_texte)

# Liste des pseudos pré définis

pseu = ["Canard", "Burger", "Ciel", "Botte", "Oxygène", "Violet", "Eternel", "Rappière", "PQ", "Etoile", "Lardon", "Saphyr", "Sauce Piquante", "MAID", "MAXIME", "Karaoke", "Train", "Zoo", "Piece", "Aimant", "Lave", "Herobrine", "Luke", "Anakin", "Yoda", "ProuteMan", "PetFoireux", "AlainTerrieur", "Schtroumpf", "Dark Vadorable", "Jack Sparroquet", "Harry Topper", "Ed Chiériant", "C MOA WESH"]
# Fonction modification des pseudos
def modifier_pseudo():
    random.shuffle(pseu)
    root = tk.Tk()
    root.withdraw()
    nouveau_pseudo = simpledialog.askstring("Pseudo", "Entrez votre pseudo :")
    if nouveau_pseudo:
        if len(nouveau_pseudo) > 12:
            return str(modifier_pseudo())
        else :
            return str(nouveau_pseudo)
    if nouveau_pseudo is None:
        return str(pseu[1])


# ================================
# --- admin mod, for fun ! ---
def admin_mod():
    root = tk.Tk()
    root.withdraw()
    mdp_u = simpledialog.askstring("Admin", "Entrez C0DE Administrateur :")     # Le code est "C0DE Administrateur" :)
    if mdp_u != None and chiffre_message(mdp_u, (1880761, 185710300164040)) == [67, 48, 68, 69, 32, 65, 100, 109, 105, 110, 105, 115, 116, 114, 97, 116, 101, 117, 114] :
        return True
    else:
        return False

def chiffre_message(message, cle_pub):    # Chiffrement Simple, c'est fait exprès...
    lst = []
    for i in message:
        lst.append(ord(i))
    return lst

def admin_value():
    root = tk.Tk()
    root.withdraw()
    rep_u = simpledialog.askstring("DIALOG", "Entrez une valeur numérique :")
    if rep_u == None or rep_u == "":
        return admin_value()
    try:                        # Vérifie qu'il n'y a que des valeurs numériques
        rep_u = float(rep_u)
        return rep_u
    except ValueError:
        return admin_value()
    return rep_u


# Bouton de l'Admin Page
bouton_rayon = pygame.Rect(LARGEUR // 2 -30, HAUTEUR - 100, 60, 60)
bouton_retour_menu = pygame.Rect(30, HAUTEUR // 2, 200, 60)
bouton_ad1 = pygame.Rect(LARGEUR // 3 - 30, HAUTEUR // 3, 60, 60)
bouton_ad2 = pygame.Rect(LARGEUR // 2 - 30, HAUTEUR // 3, 60, 60)
bouton_ad3 = pygame.Rect(LARGEUR // 3 * 2 - 30, HAUTEUR // 3, 60, 60)
bouton_ad4 = pygame.Rect(LARGEUR // 3 - 30,  HAUTEUR // 3 * 2 + 30, 60, 60)
bouton_ad5 = pygame.Rect(LARGEUR // 2 - 30, HAUTEUR // 3 * 2 + 30, 60, 60)
bouton_ad6 = pygame.Rect(LARGEUR // 3 * 2 - 30, HAUTEUR // 3 * 2 + 30, 60, 60)
bouton_ad7 = pygame.Rect(LARGEUR - 130, HAUTEUR // 2, 100, 60)

# --- Fin admin mod ---
# ================================


# Modification volume son
def volume(val, son_liste):
    for i in son_liste:
        val1 = val
        if i == son_bouton:
            val1 = 1 if val1 < 31 else val1
            val1 -= 30 if val1 > 30 else 0
        val1 = 0 if val1 < 0 else val1
        val1 = 100 if val1 > 100 else val1
        val1 = val1 / 100
        i.set_volume(val1)

curseur_son = pygame.Rect(719, 124, 35, 35)   # Curseur des sons


# --- Fonction d'animation d'introduction ---
def intro_animation(screen, SCREEN_WIDTH, SCREEN_HEIGHT, GAME_NAME, RELEASE_DATE, CREATOR_NAME):

    font_title = pygame.font.Font(resource_path("data/police/police_casino.otf"), 72)
    font_info = pygame.font.Font(resource_path("data/police/police_casino.otf"), 36)

    BLACK = (0, 0, 0)
    WHITE = (200, 200, 200)
    GRAY = (211, 211, 211)

    # Phase 1: Écran noir puis fondu du titre
    screen.fill(BLACK)
    pygame.display.flip()
    time.sleep(1)

    alpha_title = 0
    fade_speed = 3

    text_surface_game_name = font_title.render(GAME_NAME, True, WHITE)
    text_rect_game_name = text_surface_game_name.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

    # Boucle de fondu du titre
    while alpha_title < 255:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(BLACK)
        alpha_title += fade_speed
        if alpha_title > 255:
            alpha_title = 255

        text_surface_game_name.set_alpha(alpha_title)
        screen.blit(text_surface_game_name, text_rect_game_name)

        pygame.display.flip()
        pygame.time.Clock().tick(60)
    time.sleep(1)

    # --- Phase 2: Affichage des infos (date, créateur)
    alpha_info = 0
    fade_speed_info = 5
    end_time = pygame.time.get_ticks() + 3000 # Reste affiché 3 secondes avant de finir

    text_surface_release_date = font_info.render(f"Date de sortie : {RELEASE_DATE}", True, GRAY)
    text_rect_release_date = text_surface_release_date.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))

    text_surface_creator = font_info.render(f"Créé par:{CREATOR_NAME}", True, GRAY)
    text_rect_creator = text_surface_creator.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110))

    while pygame.time.get_ticks() < end_time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return

        screen.fill(BLACK)
        screen.blit(text_surface_game_name, text_rect_game_name)

        if alpha_info < 255:
            alpha_info += fade_speed_info
            if alpha_info > 255:
                alpha_info = 255

        text_surface_release_date.set_alpha(alpha_info)
        text_surface_creator.set_alpha(alpha_info)

        screen.blit(text_surface_release_date, text_rect_release_date)
        screen.blit(text_surface_creator, text_rect_creator)

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    # Phase 3: Fondu au noir
    alpha_fade_out = 255
    while alpha_fade_out > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        alpha_fade_out -= fade_speed * 2 # Fondu au noir plus rapide
        if alpha_fade_out < 0:
            alpha_fade_out = 0

        fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_surface.fill(BLACK)
        fade_surface.set_alpha(alpha_fade_out)
        screen.blit(fade_surface, (0, 0)) # Dessine le fondu au-dessus de tout

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# --- Fin de l'introduction ---

# --- Fonctions controle des Scores ---
def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    try:
        with open(SCORES_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError: # Gérer le cas où le fichier est corrompu ou vide
        return []

def save_scores(scores):
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f, indent=2) # indent=2 pour une meilleure lisibilité du JSON

def add_score(joueur1, joueur2, gagnant, temps_partie):
    scores = load_scores()
    date_partie = datetime.now().strftime("%d/%m/%Y") # Format JJ/MM/AAAA
    new_score = {
        "joueur1": joueur1,
        "joueur2": joueur2,
        "gagnant": gagnant,
        "temps_partie": temps_partie,
        "date_partie": date_partie
    }
    scores.append(new_score)
    save_scores(scores)

def delete_score_entry(index):
    scores = load_scores()
    if 0 <= index < len(scores):
        del scores[index]
        save_scores(scores)
        return True
    return False


# Création des Boutons => bouton = rectangle (position, taille)
bouton_jouer = pygame.Rect(211, 211, 200, 60)
bouton_quitter = pygame.Rect(370, 480, 200, 60)
bouton_parametres = pygame.Rect(530, 211, 200, 60)
bouton_retour = pygame.Rect(40, 40, 200, 60)
bouton_pseudo1 = pygame.Rect(211, 431, 200, 60)
bouton_pseudo2 = pygame.Rect(530, 431, 200, 60)
bouton_game_leave = pygame.Rect(900, 520, 30, 30)
bouton_scoreboard = pygame.Rect(370, HAUTEUR // 4 * 3 - 40 , 200, 60)
bouton_delete_scores = pygame.Rect(LARGEUR // 2 - 150, HAUTEUR - 100, 300, 60)

couleur_fond = gris # couleur fond


# état de base des différentes boucles
quitter = True
running = False
menu = True
parametres = False
retour = False
end_game_billard = False
pre_lancement = False
regles = False
error = False
admin_page = False
scoreboard = False


# Animation : joué qu'une fois
if FIRST_LAUNCH:
    intro_animation(fenetre, LARGEUR, HAUTEUR, GAME_NAME, RELEASE_DATE, CREATOR_NAME)
    is_first_launch = False

# --- BOUCLE PRINCIPALE ---
while quitter:                   # Si finie entraîne l'arrêt complet du programme ; état de fin : False
    # Variable qui doivent se reset à chaque changement de page
    liste = creation_boule()     # régénère la liste des boules entre chaque partie
    var = 0
    j1_point = 0
    j2_point = 0
    clic_effectue = False
    toutes_immobiles = False
    nbCoups = -1

    if scoreboard and scroll_offset != 0:
        scroll_offset = 0

    # --- MENU ---
    while menu:
        fenetre.blit(fond2, (0,0))
        for event in pygame.event.get(): # permet de quitter
            if event.type == pygame.QUIT:
                menu = False
                quitter = False

            if event.type == pygame.MOUSEBUTTONDOWN:      # Si clic
                if bouton_jouer.collidepoint(event.pos):  # sur le bouton "jouer" alors début du jeu
                    son_bouton.play()
                    menu = False
                    pre_lancement = True
                if bouton_quitter.collidepoint(event.pos): # Si clic sur le bouton "quitter" : quit
                    son_bouton.play()
                    menu = False
                    quitter = False
                if bouton_parametres.collidepoint(event.pos):      # Si clic sur le bouton paramètres alors ouverture des paramètres
                    son_bouton.play()
                    menu = False
                    parametres = True
                if bouton_scoreboard.collidepoint(event.pos):      # Si clic sur le bouton paramètres alors ouverture des paramètres
                    son_bouton.play()
                    menu = False
                    scoreboard = True

        afficher_texte("B I L L A R D", police_casino1, noir, fenetre, LARGEUR/2, 100)

        x, y = pygame.mouse.get_pos() # enregistre les coordonnée de la souris

        # Effet visuel : changer la couleur des boutons si la souris est dessus
        couleur_jouer = bleu_clair if bouton_jouer.collidepoint((x, y)) else noir       # bouton bleu si souris dessus sinon noir
        couleur_quitter = bleu_clair if bouton_quitter.collidepoint((x, y)) else noir
        couleur_parametres = bleu_clair if bouton_parametres.collidepoint((x, y)) else noir
        couleur_scoreboard = bleu_clair if bouton_scoreboard.collidepoint((x, y)) else noir

        # Dessiner les boutons
        pygame.draw.rect(fenetre, couleur_jouer, bouton_jouer, 10)
        pygame.draw.rect(fenetre, couleur_quitter, bouton_quitter, 10)
        pygame.draw.rect(fenetre, couleur_parametres, bouton_parametres, 10)
        pygame.draw.rect(fenetre, couleur_scoreboard, bouton_scoreboard, 10)

        # Ajouter du texte sur les boutons
        afficher_texte("Jouer", police_casino3, couleur_jouer, fenetre,  bouton_jouer.x + 100, bouton_jouer.y + 30)
        afficher_texte("Quitter", police_casino3, couleur_quitter, fenetre,  bouton_quitter.x + 100, bouton_quitter.y + 30)
        afficher_texte("Paramètres", police_casino3, couleur_parametres, fenetre,  bouton_parametres.x + 100, bouton_parametres.y + 30)
        afficher_texte("Scores", police_casino3, blanc, fenetre,  bouton_scoreboard.x + 100, bouton_scoreboard.y + 30)

        pygame.display.update()


    # --- Pre lancement ---
    while pre_lancement:
        fenetre.blit(fond4, (0,0))
        for event in pygame.event.get(): # permet de quitter
            if event.type == pygame.QUIT:
                pre_lancement = False
                quitter = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if bouton_retour.collidepoint(event.pos):
                    son_bouton.play()
                    menu = True
                    pre_lancement = False
                elif bouton_jouer.collidepoint(event.pos):  # sur le bouton "jouer" alors début du jeu
                    son_bouton.play()
                    start_time_game = 0
                    final_game_time_str = "00:00"
                    start_time_game = pygame.time.get_ticks()
                    time.sleep(0.4)                       # Eviter un tire prématuré

                    running = True
                    pre_lancement = False
                elif  bouton_pseudo1.collidepoint(event.pos):
                    pseudo1 = str(modifier_pseudo())
                elif  bouton_pseudo2.collidepoint(event.pos):
                    pseudo2 = str(modifier_pseudo())
                elif bouton_parametres.collidepoint(event.pos):      # Si clic sur le bouton paramètres alors ouverture des paramètres
                    son_bouton.play()
                    regles = True
                    pre_lancement = False

        afficher_texte("PRE LANCEMENT", police_casino1, blanc, fenetre, LARGEUR/2, 50)

        x, y = pygame.mouse.get_pos() # enregistre les coordonnée de la souris

        # Effet visuel : changer la couleur des boutons si la souris est dessus
        couleur_retour = bleu_clair if bouton_retour.collidepoint((x, y)) else blanc       # bouton bleu si souris dessus sinon noir
        couleur_jouer = bleu_clair if bouton_jouer.collidepoint((x, y)) else blanc
        couleur_pseudo1 = rouge if bouton_pseudo1.collidepoint((x, y)) else blanc
        couleur_pseudo2 = rouge if bouton_pseudo2.collidepoint((x, y)) else blanc
        couleur_parametres = bleu_clair if bouton_parametres.collidepoint((x, y)) else blanc

        # Dessiner les boutons
        pygame.draw.rect(fenetre, couleur_jouer, bouton_jouer, 10)
        pygame.draw.rect(fenetre, couleur_retour, bouton_retour, 10)
        pygame.draw.rect(fenetre, couleur_parametres, bouton_parametres, 10)

        # Ajouter du texte sur les boutons
        afficher_texte("Retour", police_casino3, blanc, fenetre,  bouton_retour.x + 100, bouton_retour.y + 30)
        afficher_texte("Lancer", police_casino3, blanc, fenetre,  bouton_jouer.x + 100, bouton_jouer.y + 30)
        afficher_texte(pseudo1, police_casino3, couleur_pseudo1, fenetre, bouton_pseudo1.x + 100, bouton_pseudo1.y + 30)
        afficher_texte(pseudo2, police_casino3, couleur_pseudo2, fenetre, bouton_pseudo2.x + 100, bouton_pseudo2.y + 30)
        afficher_texte("Balle Jaune", police_casino3, rouge, fenetre, bouton_pseudo1.x + 100, bouton_pseudo1.y-10)
        afficher_texte("Balle Rouge", police_casino3, rouge, fenetre, bouton_pseudo2.x + 100, bouton_pseudo2.y-10)
        afficher_texte("REGLES", police_casino3, blanc, fenetre,  bouton_parametres.x + 100, bouton_parametres.y + 30)

        pygame.display.update()


    # --- Regles ---
    while regles:
        fenetre.blit(fond4, (0,0))
        for event in pygame.event.get(): # permet de quitter
            if event.type == pygame.QUIT:
                regles = False
                quitter = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if bouton_retour.collidepoint(event.pos):
                    son_bouton.play()
                    pre_lancement = True
                    regles = False

        afficher_texte("REGLES", police_casino1, blanc, fenetre, LARGEUR/2, 50)
        afficher_texte("- jouez chacun votre tour en tirant la boule blanche.                                                                   ", police_casino2, blanc, fenetre, LARGEUR/2, HAUTEUR/2 - 100)
        afficher_texte("- Pour gagner, rentrez dans les trous les boules de votre couleur, puis la boule noir. ", police_casino2, blanc, fenetre, LARGEUR/2, HAUTEUR/2 - 60)
        afficher_texte("- Ne rentrez pas la boule Noir tant que vus n avez pas rentrez tous les boules de votre", police_casino2, blanc, fenetre, LARGEUR/2, HAUTEUR/2 - 20)
        afficher_texte("couleur.                                                                                                                                                        ", police_casino2, blanc, fenetre, LARGEUR/2, HAUTEUR/2 + 20)
        afficher_texte("- Tu as un second tour si tu rentres une boule de ta couleur                                                       ", police_casino2, blanc, fenetre, LARGEUR/2, HAUTEUR/2 + 60)
        afficher_texte("- Le joueur adverse à deux tours si la boule blanche                                                                    ", police_casino2, blanc, fenetre, LARGEUR/2, HAUTEUR/2 + 100)
        afficher_texte("- ne touche aucune boule                                                                                  ", police_casino2, blanc, fenetre, LARGEUR/2, HAUTEUR/2 + 140)
        afficher_texte("- touche en premier une boule de l adversaire                                       ", police_casino2, blanc, fenetre, LARGEUR/2, HAUTEUR/2 + 180)
        afficher_texte("- tombe dans un trou                                                                                          ", police_casino2, blanc, fenetre, LARGEUR/2, HAUTEUR/2 + 220)

        x, y = pygame.mouse.get_pos() # enregistre les coordonnées de la souris

        # Effet visuel : changer la couleur des boutons si la souris est dessus
        couleur_retour = blanc if bouton_retour.collidepoint((x, y)) else noir       # bouton bleu si souris dessus sinon noir

        # Dessiner les boutons
        pygame.draw.rect(fenetre, couleur_retour, bouton_retour, 10)

        # Ajouter du texte sur les boutons
        afficher_texte("Retour", police_casino3, blanc, fenetre,  bouton_retour.x + 100, bouton_retour.y + 30)

        pygame.display.update()


    # --- Parametres ---
    while parametres:
        fenetre.blit(fond3, (0,0))
        for event in pygame.event.get(): # permet de quitter
            if event.type == pygame.QUIT:
                parametres = False
                quitter = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if bouton_retour.collidepoint(event.pos):
                    son_bouton.play()
                    menu = True
                    parametres = False
                elif bouton_rayon.collidepoint(event.pos):         # Easter EGG lol
                    st = admin_mod()
                    if st:
                        admin_page = True
                        parametres = False
                    else:
                        parametres = False
                        error = True
                elif curseur_son.collidepoint(event.pos):
                    clic_son_parametres = True

            elif event.type == pygame.MOUSEBUTTONUP:
                clic_son_parametres = False

        if clic_son_parametres:
            x = 549 if x < 549 else x
            x = 749 if x > 749 else x
            curseur_son[0] = x-18
            vol = (curseur_son[0] - 531) // 2
            volume(vol, son_liste)
            vol_txt = str(vol)
            son_rebond.play()



        afficher_texte("PARAMETRES", police_casino1, noir, fenetre, LARGEUR/2, 70)

        x, y = pygame.mouse.get_pos() # enregistre les coordonnée de la souris

        # Effet visuel : changer la couleur des boutons si la souris est dessus
        couleur_retour = bleu_clair if bouton_retour.collidepoint((x, y)) else noir       # bouton bleu si souris dessus sinon noir

        # Dessiner les boutons
        pygame.draw.rect(fenetre, couleur_retour, bouton_retour, 10)
        pygame.draw.line(fenetre, bleu_fonce, (539,140), (754,140), 10)
        pygame.draw.rect(fenetre, jaune_clair, curseur_son, 23)
        pygame.draw.rect(fenetre, rouge, bouton_rayon, 20)

        # Ajouter du texte sur les boutons
        afficher_texte("Retour", police_casino3, noir, fenetre,  bouton_retour.x + 100, bouton_retour.y + 30)
        afficher_texte(vol_txt, police_casino3, jaune_clair, fenetre,  820, 140)
        afficher_texte("VOLUME", police_casino3, jaune_clair, fenetre, 465, 140)
        afficher_texte("NE PAS APPUYER", police_casino2, rouge, fenetre, LARGEUR // 2 - 120, HAUTEUR-70)

        pygame.display.update()


    # --- end game ---
    while end_game_billard:
        fenetre.blit(fond4, (0,0))

        for event in pygame.event.get(): # permet de quitter
            if event.type == pygame.QUIT:
                end_game_billard = False
                quitter = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if bouton_retour.collidepoint(event.pos):
                    son_bouton.play()
                    victoire = ""
                    menu = True
                    end_game_billard = False

        x, y = pygame.mouse.get_pos() # enregistre les coordonnée de la souris

        # Effet visuel : changer la couleur des boutons si la souris est dessus
        couleur_retour = gris if bouton_retour.collidepoint((x, y)) else blanc       # bouton bleu si souris dessus sinon noir

        # Dessiner les boutons
        pygame.draw.rect(fenetre, couleur_retour, bouton_retour, 10)

        # Ajouter du texte sur les boutons
        afficher_texte("MENU", police_casino3, blanc, fenetre,  bouton_retour.x + 100, bouton_retour.y + 30)
        afficher_texte(victoire, police_casino1, blanc, fenetre,  LARGEUR // 2, HAUTEUR // 2)
        afficher_texte("A gagné !!! Félicitation", police_casino1, blanc, fenetre,  LARGEUR // 2, HAUTEUR // 2 + 60)

        afficher_texte(f"Temps de jeu: {final_game_time_str}", police_casino2, blanc, fenetre, LARGEUR // 2, HAUTEUR // 2 + 120)


        pygame.display.update()


    # --- Boucle JEU---
    while running:
        pygame.time.wait(delay)              # pause pour limiter la vitesse de rafraîchissement

        if GAME_FOND == 0:
            fenetre.fill((255, 255, 255))
            fenetre.blit(fond, (0,0))
        elif GAME_FOND == 1:
            fenetre.fill(blanc)
            GAME_FOND = 10

        current_time = pygame.time.get_ticks()
        elapsed_milliseconds = current_time - start_time_game # Garder les millisecondes pour un calcul plus précis
        elapsed_seconds = elapsed_milliseconds // 1000
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        time_text = f"Temps: {minutes:02d}:{seconds:02d}"

        final_game_time_str = f"{minutes:02d}:{seconds:02d}"

        afficher_texte(time_text, police_casino3, blanc, fenetre, LARGEUR - 100, 30)

        afficher_texte("Joueur 1 :    points", police_casino3, bleu_clair, fenetre,  750, 515)
        afficher_texte(str(j1_point), police_casino3, bleu_clair, fenetre,  770, 515)
        afficher_texte("Joueur 2 :   points", police_casino3, bleu_clair, fenetre,  750, 545)
        afficher_texte(str(j2_point), police_casino3, bleu_clair, fenetre,  770, 545)

        if joueur == 1:                   # Affichage des joueurs
            texte = pseudo1
        else:
            texte = pseudo2

        for boule in liste:
            if boule.vitesse_x != 0 or boule.vitesse_y != 0:
                toutes_immobiles = False
                choc(boule)                                    # Vérifie les collisions
                result = boule.deplacement()                    # Mise à jour de la position

                if result == "ENDGAME":                         # Si la boule noire rentre dans un trou + Regarde si il y a une faute
                    if joueur == 1 and j1_point == 7:
                        victoire = pseudo1
                    elif joueur == 2 and j2_point == 7:
                        victoire = pseudo2
                    elif joueur == 1 and j1_point != 7:
                        victoire = pseudo1
                    else :
                        victoire = pseudo2

                    add_score(pseudo1, pseudo2, victoire, final_game_time_str)
                    end_game_billard = True                     # Ecran de fin
                    running = False                             # Fin du jeu

                elif result == "1j":
                    if joueur == 1:
                        tour = 1
                    j1_point += 1

                elif result == "2j":
                    if joueur == 2:
                        tour = 1
                    j2_point += 1

            r = boule.couleur[0]    # données pour les couleurs des boules
            v = boule.couleur[1]
            b = boule.couleur[2]
            centre = 0
            for x in range(30): # affichages de plusieurs cercles avec couleur dégradé jusqu'au blanc : créer un effet 3D
                r += (255 - boule.couleur[0]) // 30     # modifie les données des couleurs (RVB) pour un dégradé
                v += (255 - boule.couleur[1]) // 30
                b += (255 - boule.couleur[2]) // 30
                pygame.draw.circle(fenetre, (r, v, b), (math.floor(boule.x+centre), math.floor(boule.y+centre)), rayon - x/3) # affichage des boules
                centre += 0.15

        if toutes_immobiles:
            if nbr_colision == 0:
                tour = 2
                joueur = 1 if joueur == 2 else 2 # chgmt de joueur
                nbr_colision = -1

            afficher_texte(texte, police_casino3, bleu_clair, fenetre, 100, 530)
            afficher_texte(",  à toi de jouer", police_casino3, bleu_clair, fenetre, 280, 530)


            afficher_texte("coups", police_casino3, bleu_clair, fenetre, 472, 530)
            afficher_texte(str(tour), police_casino3, bleu_clair, fenetre, 418, 530)

            if tour == 0:
                joueur = 2 if joueur == 1 else 1 # chgmt de joueur
                tour = 1

            x, y = pygame.mouse.get_pos() # enregistre les coordonnées de la souris
            dx = x - liste[0].x           # distance souris / boule blanche (dx : ordonné, dy : abscisse)
            dy = y - liste[0].y
            angle = math.atan2(dy, dx) # angle en radian
            force =  min(math.sqrt(dx**2 + dy**2) // 5 , (force_max)) # force

            pygame.draw.line(fenetre, marron, (x, y), (x + math.cos(angle)*300, y + math.sin(angle)*300), 10)
            pygame.draw.line(fenetre, bleu_clair, (liste[0].x, liste[0].y), (liste[0].x + math.cos(angle+pi) * (force*10),  liste[0].y + math.sin(angle+pi) * (force*10)), 5)

            if clic_effectue:                   # Si clic a été enregistré
                distance = sqrt(dx**2 + dy**2)

                # permet le mouvement de la canne
                while distance > 2 * rayon:
                    # nomalisation des vecteurs
                    nx = dx / distance
                    ny = dy / distance
                    x -= (distance // force) * nx
                    y -= (distance // force) * ny

                    # affichage canne (qui se raproche de la boule)
                    pygame.draw.line(fenetre, marron, (x, y), (x + math.cos(angle)*300, y + math.sin(angle)*300), 10)
                    pygame.display.update()

                    # MAJ des variables apres mvt
                    dx = x - liste[0].x
                    dy = y - liste[0].y
                    distance = sqrt(dx**2 + dy**2)

                nbr_colision = 0
                nbCoups += 1
                tour -= 1
                liste[0].jouer() #
                clic_effectue = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quitter = False
            elif event.type == pygame.MOUSEBUTTONUP:
                if bouton_game_leave.collidepoint(event.pos)  :
                    son_bouton.play()
                    menu = True
                    running = False
                if event.button == 1 and toutes_immobiles == True:
                    clic_effectue = True
                                    # Enregistre le clic
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu = True
                    running = False

        # Bouton LEAVE ==============
        couleur_bouton_leave = jaune if bouton_retour.collidepoint((x, y)) else noir
        pygame.draw.rect(fenetre, couleur_bouton_leave, bouton_game_leave, 0)
        pygame.draw.rect(fenetre, rouge, bouton_game_leave, 10)
        afficher_texte("EXIT", police_casino2, noir, fenetre,  bouton_game_leave.x + 15, bouton_game_leave.y - 15)
        # ===========================

        toutes_immobiles = True
        pygame.display.update()



    # --- Dommage ---
    while error:
        fenetre.blit(fond6, (0,0))
        pygame.display.update()
        time.sleep(2)
        error = False
        quitter = False


    # --- Admin Page : modification des caracteristique des boules (vitesse, frotement, taille, ...) ---
    while admin_page:
        fenetre.blit(fond4, (0,0))

        for event in pygame.event.get(): # permet de quitter
            if event.type == pygame.QUIT:
                admin_page = False
                quitter = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if bouton_retour_menu.collidepoint(event.pos):
                    son_bouton.play()
                    menu = True
                    admin_page = False
                elif bouton_ad1.collidepoint(event.pos):
                    son_bouton.play()
                    rayon = int(admin_value())
                    rayon = 20 if rayon > 20 else rayon
                    rayon = 1 if rayon < 1 else rayon
                elif bouton_ad2.collidepoint(event.pos):
                    son_bouton.play()
                    force_max = int(admin_value())
                    force_max = 30 if force_max > 30 else force_max
                    force_max = 1 if force_max < 1 else force_max
                elif bouton_ad3.collidepoint(event.pos):
                    son_bouton.play()
                    friction = int(admin_value())
                    friction = 1 if friction > 1 else friction
                    friction = 0.1 if friction < 0.1 else friction
                elif bouton_ad4.collidepoint(event.pos):
                    son_bouton.play()
                    GAME_FOND = 1 if GAME_FOND == 0 else 0
                    coul_ad4 = rouge if coul_ad4 == jaune else jaune
                elif bouton_ad5.collidepoint(event.pos):
                    son_bouton.play()
                    delay = int(admin_value())
                    delay = 50 if delay > 50 else delay
                    delay = 1 if delay < 1 else delay
                elif bouton_ad6.collidepoint(event.pos):
                    son_bouton.play()
                    rebond = int(admin_value())
                    rebond = 1 if rebond > 1 else rebond
                    rebond = 0.3 if rebond < 0.3 else rebond
                elif bouton_ad7.collidepoint(event.pos):
                    son_bouton.play()
                    rebond = 1
                    delay = 5
                    friction = 1
                    force_max = 30
                    rayon = 20

        x, y = pygame.mouse.get_pos() # enregistre les coordonnée de la souris

        # Effet visuel : changer la couleur des boutons si la souris est dessus
        couleur_retour = bleu_clair if bouton_retour_menu.collidepoint((x, y)) else blanc
        couleur_ad1 = jaune if bouton_ad1.collidepoint((x,y)) else vert
        couleur_ad2 = jaune if bouton_ad2.collidepoint((x,y)) else vert
        couleur_ad3 = jaune if bouton_ad3.collidepoint((x,y)) else vert
        couleur_ad4 = jaune if bouton_ad4.collidepoint((x,y)) else vert
        couleur_ad5 = jaune if bouton_ad5.collidepoint((x,y)) else vert
        couleur_ad6 = jaune if bouton_ad6.collidepoint((x,y)) else vert
        couleur_ad7 = jaune if bouton_ad7.collidepoint((x,y)) else vert


        # Dessiner les boutons
        pygame.draw.rect(fenetre, couleur_retour, bouton_retour_menu, 10)
        pygame.draw.rect(fenetre, vert, bouton_retour_menu, 0)

        pygame.draw.rect(fenetre, vert, bouton_ad1, 10)
        pygame.draw.rect(fenetre, vert, bouton_ad2, 10)
        pygame.draw.rect(fenetre, vert, bouton_ad3, 10)
        pygame.draw.rect(fenetre, vert, bouton_ad4, 10)
        pygame.draw.rect(fenetre, vert, bouton_ad5, 10)
        pygame.draw.rect(fenetre, vert, bouton_ad6, 10)
        pygame.draw.rect(fenetre, vert, bouton_ad7, 10)


        pygame.draw.rect(fenetre, rouge, bouton_ad1, 0)
        pygame.draw.rect(fenetre, rouge, bouton_ad2, 0)
        pygame.draw.rect(fenetre, rouge, bouton_ad3, 0)
        pygame.draw.rect(fenetre, coul_ad4, bouton_ad4, 0)
        pygame.draw.rect(fenetre, rouge, bouton_ad5, 0)
        pygame.draw.rect(fenetre, rouge, bouton_ad6, 0)
        pygame.draw.rect(fenetre, rouge, bouton_ad7, 0)

        # Ajouter du texte sur les boutons
        afficher_texte("MENU", police_casino3, noir, fenetre,  bouton_retour_menu.x + 100, bouton_retour_menu.y + 30)
        afficher_texte("RAYON", police_casino3, couleur_ad1, fenetre,  bouton_ad1.x + 30, bouton_ad1.y - 30)
        afficher_texte("FORCE", police_casino3, couleur_ad2, fenetre,  bouton_ad2.x + 30 , bouton_ad2.y - 30)
        afficher_texte("FRICTION", police_casino3, couleur_ad3, fenetre,  bouton_ad3.x + 30 , bouton_ad3.y - 30)
        afficher_texte("FOND ECRAN", police_casino3, couleur_ad4, fenetre,  bouton_ad4.x + 30 , bouton_ad4.y - 30)
        afficher_texte("DELAY AFFICHAGE", police_casino3, couleur_ad5, fenetre,  bouton_ad5.x + 30 , bouton_ad5.y - 55)
        afficher_texte("PERTE REBOND", police_casino3, couleur_ad6, fenetre,  bouton_ad6.x + 30 , bouton_ad6.y - 30)
        afficher_texte("PRE SET", police_casino3, couleur_ad7, fenetre,  bouton_ad7.x + 50 , bouton_ad7.y - 30)


        pygame.display.update()

    while scoreboard:
        fenetre.blit(fond4, (0,0))
        scores_data = load_scores() # Charger les scores à chaque affichage

        # Définir la zone d'affichage des scores (pour le défilement)
        score_display_start_y = 150                                                 # Où commence la liste des scores
        score_display_end_y = HAUTEUR - 150                                         # Où finit la liste des scores (au-dessus des boutons)
        display_area_height = score_display_end_y - score_display_start_y

        # Calculer la hauteur totale du contenu si tous les scores étaient affichés
        total_content_height = len(scores_data) * SCORE_LINE_HEIGHT

        # Si le contenu est plus grand que la zone d'affichage, nous pouvons défiler
        if total_content_height > display_area_height:
            max_scroll = total_content_height - display_area_height
        else:
            max_scroll = 0 # Pas besoin de défilement

        # Vérifier et ajuster scroll_offset pour ne pas dépasser les limites
        if scroll_offset < 0:
            scroll_offset = 0
        if scroll_offset > max_scroll:
            scroll_offset = max_scroll


        # Afficher les en-têtes
        header_y_offset = score_display_start_y - 30
        afficher_texte("ID partie", police_casino2, jaune_clair, fenetre, 100, header_y_offset)
        afficher_texte("Joueur 1", police_casino2, jaune_clair, fenetre, 250, header_y_offset)
        afficher_texte("Joueur 2", police_casino2, jaune_clair, fenetre, 400, header_y_offset)
        afficher_texte("Gagnant", police_casino2, jaune_clair, fenetre, 550, header_y_offset)
        afficher_texte("Temps", police_casino2, jaune_clair, fenetre, 700, header_y_offset)
        afficher_texte("Date", police_casino2, jaune_clair, fenetre, 850, header_y_offset)


        # Afficher chaque score en appliquant le décalage de défilement
        for i, score in enumerate(scores_data):
            current_y_pos = score_display_start_y + (i * SCORE_LINE_HEIGHT) - scroll_offset

            # Dessiner le score seulement s'il est visible dans la zone d'affichage
            if score_display_start_y <= current_y_pos < score_display_end_y:
                # Utilisez des couleurs différentes pour le gagnant
                winner_color_j1 = blanc
                winner_color_j2 = blanc
                winner_color_gagnant = blanc

                if score["gagnant"] == score["joueur1"]:
                    winner_color_gagnant = jaune_clair # Gagnant en jaune
                elif score["gagnant"] == score["joueur2"]:
                    winner_color_gagnant = jaune_clair # Gagnant en jaune

                afficher_texte(str(i+1), police_casino2, blanc, fenetre, 100, current_y_pos)
                afficher_texte(score["joueur1"], police_casino2, winner_color_j1, fenetre, 250, current_y_pos)
                afficher_texte(score["joueur2"], police_casino2, winner_color_j2, fenetre, 400, current_y_pos)
                afficher_texte(score["gagnant"], police_casino2, winner_color_gagnant, fenetre, 550, current_y_pos)
                afficher_texte(score["temps_partie"], police_casino2, blanc, fenetre, 700, current_y_pos)
                afficher_texte(score["date_partie"], police_casino2, winner_color_gagnant, fenetre, 850, current_y_pos)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                scoreboard = False
                quitter = False
            elif event.type == pygame.MOUSEWHEEL:
                scroll_speed = 2 * SCORE_LINE_HEIGHT # Défile de 2 lignes à la fois
                scroll_offset -= event.y * scroll_speed

                if scroll_offset < 0:
                    scroll_offset = 0
                if scroll_offset > max_scroll:
                    scroll_offset = max_scroll

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if bouton_retour.collidepoint(event.pos):
                    son_bouton.play()
                    scroll_offset = 0
                    menu = True
                    scoreboard = False


        x, y = pygame.mouse.get_pos()


        couleur_retour = gris if bouton_retour.collidepoint((x, y)) else blanc

        pygame.draw.rect(fenetre, couleur_retour, bouton_retour, 10)

        afficher_texte("MENU", police_casino3, blanc, fenetre, bouton_retour.x + 100, bouton_retour.y + 30)
        afficher_texte("TABLEAU DES SCORES", police_casino1, blanc, fenetre, LARGEUR / 2 + 30, 50)

        pygame.display.update()


# Quitter pygame et le programme
pygame.quit()