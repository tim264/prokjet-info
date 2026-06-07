# -*- coding: utf-8 -*-
"""

@author: Gaudin Timothé & Martin thibault
"""
from cpiece import *
from cmemen import *

class Echiquier:
    """
    Gère la logique du jeu : état de la grille, tour de jeu et règles.
    Contient une matrice 8x8 d'objets de type Piece.
    """
    def __init__(self):
        """
        Initialise un plateau et définit le premier tour aux blancs.
        -return: None
        """
        self.grille = [[None for _ in range(8)] for _ in range(8)]
        self.tour = "blanc"
        self.historique = []
    def deplacer_piece(self, depart, arrivee):
        """
        Permet de déplacer une pièce. Vérifie la légalité et l'état d'échec.
        -param depart: tuple (ligne, col) d'origine.
        -param arrivee: tuple (ligne, col) de destination.
        -return: True si le mouvement est validé, False sinon.
        """
        piece = self.grille[depart[0]][depart[1]]

        if piece is None:
            return False

    # tour de jeu
        if piece.couleur != self.tour:
            print(f"ce n'est pas le tour des {piece.couleur}s")
            return False

    # mouvement possible
        if arrivee not in piece.mouvements_possibles(self):
            return False
    
        self.sauvegarder_dans_memento()

    #  simulation du coup
        sauvegarde = self.grille[arrivee[0]][arrivee[1]]

        self.grille[arrivee[0]][arrivee[1]] = piece
        self.grille[depart[0]][depart[1]] = None
        ancienne_pos = piece.position
        piece.position = arrivee

    #si roi en échec -> on annule
        if self.roi_en_echec(piece.couleur):
            self.grille[depart[0]][depart[1]] = piece
            self.grille[arrivee[0]][arrivee[1]] = sauvegarde
            piece.position = ancienne_pos
            return False

    #  coup accepté -> changement de tour
        self.tour = "noir" if self.tour == "blanc" else "blanc"
        adversaire = self.tour
        
        if self.est_echec_et_mat(adversaire):
            print(f"ÉCHEC ET MAT ! {piece.couleur} gagne !")
        return True
        
    def sauvegarder_dans_memento(self):
        """Crée un memento de l'état actuel et l'ajoute à l'historique."""
        self.historique.append(Memento(self.grille, self.tour))

    def restaurer_depuis_memento(self):
        """Recule d'un état en restaurant le dernier memento de l'historique."""
        if not self.historique:
            return False
        
        dernier_memento = self.historique.pop()
        # CORRECTION ICI : On récupère la grille et le tour stockés
        self.grille, self.tour = dernier_memento.obtenir_etat()
        
        # Recalculer correctement la position interne stockée dans chaque pièce
        for l in range(8):
            for c in range(8):
                if self.grille[l][c] is not None:
                    self.grille[l][c].position = (l, c)
        return True
    
    def trouver_roi(self, couleur):
        """Parcourt la grille pour localiser le Roi d'une couleur donnée.
        -param couleur: str ("blanc" ou "noir") représentant la couleur du Roi recherché.
        -return: tuple (ligne, col) représentant la position du Roi, ou None si non trouvé."""
        for l in range(8):
            for c in range(8):
                piece = self.grille[l][c]
                if isinstance(piece, Roi) and piece.couleur == couleur:
                    return (l, c)
        return None
    
    def case_attaquee(self, ligne, col, couleur_adverse):
        """Parcourt la grille pour voir si une la pièce donnée entrée est attaquée par une des pièces adverses.
        -param ligne: int, index de la ligne de la case à vérifier.
        -param col: int, index de la colonne de la case à vérifier.
        -param couleur_adverse: str ("blanc" ou "noir") représentant la couleur de l'attaquant potentiel.
        -return: True si la case est attaquée, None (ou False implicite) sinon."""
        for l in range(8):
            for c in range(8):
                piece = self.grille[l][c]
    
                if piece is not None and piece.couleur == couleur_adverse:
                    if (ligne, col) in piece.mouvements_possibles(self):
                        return True
        

    
    def roi_en_echec(self, couleur):
        """Détermine si le Roi de la couleur indiquée est attaqué.
        -param couleur: str ("blanc" ou "noir") représentant la couleur du Roi à vérifier.
        -return: True si le Roi est en échec, False sinon."""
        roi_pos = self.trouver_roi(couleur)
        if roi_pos is None:
            print('échec')
            return False
    
        ligne, col = roi_pos
        adversaire = "noir" if couleur == "blanc" else "blanc"
    
        return self.case_attaquee(ligne, col, adversaire)
    
    
    def coups_possibles(self, couleur):
        """Calcule l'intégralité des coups légaux pour un joueur.
        -param couleur: str ("blanc" ou "noir") du joueur dont on veut les coups.
        -return: list de tuples au format ((l_dep, c_dep), (l_arr, c_arr)) listant les coups légaux."""
        coups = []
    
        for l in range(8):
            for c in range(8):
                piece = self.grille[l][c]
                if piece is not None and piece.couleur == couleur:
                    depart = (l, c)
                    for arrivee in piece.mouvements_possibles(self):
                        # simulation
                        sauvegarde = self.grille[arrivee[0]][arrivee[1]]
                        ancienne_pos = piece.position
    
                        self.grille[arrivee[0]][arrivee[1]] = piece
                        self.grille[l][c] = None
                        piece.position = arrivee
    
                        en_echec = self.roi_en_echec(couleur)
    
                        # annulation
                        self.grille[l][c] = piece
                        self.grille[arrivee[0]][arrivee[1]] = sauvegarde
                        piece.position = ancienne_pos
    
                        if not en_echec:
                            coups.append((depart, arrivee))
    
        return coups
    def est_echec_et_mat(self, couleur):
        """
        Vérifie si le joueur est en échec et mat en regardant s'il y a échec ainsi que les coups possibles.
        -param couleur: str ("blanc" ou "noir") du joueur à tester.
        -return: True si le joueur est échec et mat, False sinon.
        """
        if not self.roi_en_echec(couleur):
            return False
    
        return len(self.coups_possibles(couleur)) == 0
    
    def exporter_etat(self):
        """
        Exporte l'état du plateau sous forme de dictionnaire pour la sauvegarde JSON.
        -return: list de dictionnaires contenant les données de chaque pièce présente sur la grille.
        """
        etat = []
        for l in range(8):
            for c in range(8):
                piece = self.grille[l][c]
                if piece:
                    etat.append({
                        "type": type(piece).__name__,
                        "couleur": piece.couleur,
                        "position": [l, c]
                    })
        return etat
    
    
    def creer_piece(self,type_piece, couleur, position):
        """
        Méthode utilisée pour reconstruire le plateau lorsque l'on récupère une ancienne partie.
        -param type_piece: str, le nom textuel de la classe de la pièce (ex: "Pion", "Tour").
        -param couleur: str ("blanc" ou "noir").
        -param position: tuple (ligne, col) de la pièce à instancier.
        -return: Une instance d'une sous-classe de Piece, ou None si le type n'est pas reconnu.
        """
        pieces_disponibles = {
            "Pion": Pion,
            "Tour": Tour,
            "Cavalier": Cavalier,
            "Fou": Fou,
            "Reine": Reine,
            "Roi": Roi
        }
        if type_piece in pieces_disponibles:
            return pieces_disponibles[type_piece](couleur, position)
        return None
    
    def importer_etat(self, data):
        """
        Reconstruit le plateau depuis un dictionnaire JSON.
        -param data: dict contenant les clés "tour" et "grille" issues du fichier de sauvegarde.
        -return: None
        """
        self.grille = [[None for _ in range(8)] for _ in range(8)]
        self.tour = data.get("tour", "blanc")
        for p_data in data.get("grille", []):
            l, c = p_data["position"]
            piece = self.creer_piece(p_data["type"], p_data["couleur"], (l, c))
            self.grille[l][c] = piece
    
