from ultralytics import YOLO
from PIL import Image
import streamlit as st
import io
import pandas as pd
import numpy as np
import cv2
import torch
from time import sleep


# Importation du modèle d'IA et création de variables de jeu
model = YOLO("best_tarot.pt")

cartes_coinche = {
    0: "9_Pique",
    1: "9_Trefle",
    2: "9_Coeur",
    3: "9_Carreau",
    4: "10_Pique",
    5: "10_Trefle",
    6: "10_Coeur",
    7: "10_Carreau",
    8: "Valet_Pique",
    9: "Valet_Trefle",
    10: "Valet_Coeur",
    11: "Valet_Carreau",
    12: "Dame_Pique",
    13: "Dame_Trefle",
    14: "Dame_Coeur",
    15: "Dame_Carreau",
    16: "Roi_Pique",
    17: "Roi_Trefle",
    18: "Roi_Coeur",
    19: "Roi_Carreau",
    20: "As_Pique",
    21: "As_Trefle",
    22: "As_Coeur",
    23: "As_Carreau"
}

contrats_possibles = list(range(80, 701, 10))

contrats_possibles.extend(['Capot', 'Générale'])

points_non_atout = {'9':0, '10':10, 'Valet':2, 'Dame':3, 'Roi':4, 'As':11}
points_atout = {'9':14, '10':10, 'Valet':20, 'Dame':3, 'Roi':4, 'As':11}

annonces_points = {
    'Tierce':20,
    'Belote':20,
    'Cinquante':50,
    'Carré':100,
    'Cent':100,
    'Carré de 9':150,
    'Carré de Valets':200
}

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "annonce_def_key" not in st.session_state:
    st.session_state.annonce_def_key = 0

if "annonce_at_key" not in st.session_state:
    st.session_state.annonce_at_key = 0

if "points_DataFrame" not in st.session_state:
    st.session_state.points_DataFrame = pd.DataFrame()
if "equipe1" not in st.session_state:
    st.session_state.equipe1 = "1"
if "equipe2" not in st.session_state:
    st.session_state.equipe2 = "2"
if "point" not in st.session_state:
    st.session_state.point = "69"
if "valider_tour" not in st.session_state:
    st.session_state.valider_tour = False


# Création de fonction de fonctionnement
def filtrer_et_supprimer_doublons(liste):
    # Étape 1 : Compter les occurrences des valeurs
    compte = {}
    for valeur in liste:
        if valeur in compte:
            compte[valeur] += 1
        else:
            compte[valeur] = 1
    
    # Étape 2 : Garder les valeurs qui apparaissent au moins deux fois
    valeurs_repeetees = {valeur for valeur, c in compte.items() if c > 1}
    
    # Étape 3 : Supprimer les doublons tout en gardant une seule occurrence de chaque valeur
    resultat = []
    vu = set()
    for valeur in liste:
        if valeur in valeurs_repeetees and valeur not in vu:
            resultat.append(valeur)
            vu.add(valeur)

    resultat_trie = sorted(resultat)
    
    return resultat_trie

def detection_cartes(image):
    #image = Image.open(uploaded_file)
    results = model(image)
    result_image = results[0].plot()

    liste_idx_labels = results[0].boxes.cls
    liste_idx_labels_int = liste_idx_labels.to(dtype=torch.int)
    liste_idx_labels = liste_idx_labels_int.tolist()
    
    liste_idx_labels_cleaned = filtrer_et_supprimer_doublons(liste_idx_labels)

    liste_cartes = [cartes_coinche[idx] for idx in liste_idx_labels_cleaned]
    
    
    return liste_cartes, result_image

def ajouter_point(atout, contrat, annonce_attaque, annonce_defence, is_Capot, is_Generale, cartes):

    points_attaque_plis = 0
    points_defence_plis = 0

    points_attaque_annonce = 0
    points_defence_annonce = 0

    is_fait = False

    # Ajouter les points des annonces  
    for annonce in annonce_attaque:
        points_attaque_annonce += annonces_points[annonce]
    for annonce in annonce_defence:
        points_defence_annonce += annonces_points[annonce]

    # S'il y a capot
    if (contrat == "Capot") :
        if (is_Capot is True) :
            
            points_attaque = 250 + points_attaque_annonce + points_defence_annonce
            points_defence = 0
            is_fait = True
            return(points_attaque, points_defence, is_fait)
        
        else:

            points_attaque = 0
            points_defence = 250 + 160 + points_defence_annonce
            is_fait = False
            return(points_attaque, points_defence, is_fait)

    # S'il y a Générale
    if (contrat == "Générale") :
        if (is_Generale is True) :
        
            points_attaque = 500 + points_attaque_annonce + points_defence_annonce
            points_defence = 0
            is_fait = True
            return(points_attaque, points_defence, is_fait)

        else : 

            points_attaque = 0
            points_defence = 500 + 160 + points_defence_annonce
            is_fait = False
            return(points_attaque, points_defence, is_fait)
    
    # Ajout de la valeur des cartes des plis
    valeurs_cartes = []

    for carte in cartes:
        if carte.split("_")[1] == atout :
            valeurs_cartes.append(points_atout[carte.split("_")[0]])
        else : 
            valeurs_cartes.append(points_non_atout[carte.split("_")[0]])

    points_cartes_pli = sum(valeurs_cartes)

    points_defence_plis += points_cartes_pli
    points_attaque_plis += (162 - points_cartes_pli)

    points_attaque = points_attaque_plis + points_attaque_annonce
    points_defence = points_defence_plis + points_defence_annonce

    if (points_attaque >= contrat) and (points_attaque > points_defence):

        is_fait = True
        return(points_attaque + int(contrat), points_defence, is_fait)
    
    else :
        is_fait = False
        return(0, 162 + points_defence_annonce + int(contrat), is_fait)

def drop_element(element, lst):
    try:
        lst.remove(element)
    except ValueError:
        print(f"L'élément {element} n'est pas dans la liste.")

def update_key():
    st.session_state.uploader_key += 1
    st.session_state.annonce_def_key += 1
    st.session_state.annonce_at_key += 1

def fin_partie():
    st.balloons()
    sleep(3)
    for key in st.session_state.keys():
        del st.session_state[key]
    st.switch_page("Accueil.py")





# Code Streamlit pour l'interface

col1, col2, col3 = st.columns(3)

with col2:
    st.image("logo_coinche_fondblanc.png")
    

st.write("Suivi des scores :")

tableau_score = st.dataframe(st.session_state.points_DataFrame, use_container_width = True)

formulaire_pli = st.expander("Fin de manche")

with formulaire_pli:

    #with st.form("my_form"):
    st.session_state.equipe_attaque = st.selectbox(
    "Qui attaque ?",
    (st.session_state["equipe1"], st.session_state["equipe2"]),
    )

    st.session_state.contrat = st.selectbox(
    "Quel est le contrat ?",
    contrats_possibles,
    )

    st.session_state.atout = st.selectbox(
    "Quel est l'atout ?",
    ("Pique", "Trefle", "Coeur", "Carreau"),
    )

    st.session_state.annonce_attaque = st.multiselect(
        "Annonce de l'attaque ⚔️",
        ["Tierce", "Cinquante", "Cent", "Belote", "Carré", "Carré de 9", "Carré de Valets"],
        key=f"annonce_attaque_{st.session_state.annonce_at_key}"
    )

    st.session_state.annonce_defence = st.multiselect(
        "Annonce de la defence 🛡️",
        ["Tierce", "Cinquante", "Cent", "Belote", "Carré", "Carré de 9", "Carré de Valets"],
        key=f"annonce_defence_{st.session_state.annonce_def_key}"
    )

    col1_, col2_ = st.columns(2)
    with col1_ :
        st.session_state.is_Capot = st.checkbox("Capot")
        st.session_state.is_General = st.checkbox("Générale")
    with col2_ :
        st.session_state.is_coinche = st.checkbox("Coinché&nbsp;&nbsp;🔥")
        st.session_state.is_surcoinche = st.checkbox("Sur-Coinché&nbsp;&nbsp;🔥🔥")

    uploaded_file = st.file_uploader(
        "Photo des plis de la défence 🛡️", type="jpg", key=f"uploader_{st.session_state.uploader_key}"
    )

    #submitted = st.button("Charger la photo", use_container_width=True)

    #if submitted:

    if uploaded_file is not None:
        
        liste_cartes, result_image = detection_cartes(Image.open(uploaded_file))
        
        cartes_pli = st.multiselect(
        "Carte détéctées :",
        ["9_Pique", "9_Trefle", "9_Coeur", "9_Carreau", "10_Pique", "10_Trefle", "10_Coeur", "10_Carreau", "Valet_Pique", "Valet_Trefle", "Valet_Coeur", "Valet_Carreau", "Dame_Pique", "Dame_Trefle", "Dame_Coeur", "Dame_Carreau", "Roi_Pique", "Roi_Trefle", "Roi_Coeur", "Roi_Carreau", "As_Pique", "As_Trefle", "As_Coeur", "As_Carreau"],
        liste_cartes
        )

        if st.session_state.equipe_attaque == st.session_state.equipe1 :
            st.session_state.equipe_defence = st.session_state.equipe2
        else :
            st.session_state.equipe_defence = st.session_state.equipe1

        #atout, contrat, annonce_attaque, annonce_defence, is_Capot, is_Generale
        st.session_state.points_attaque_plis, st.session_state.points_defence_plis, st.session_state.is_fait = ajouter_point(st.session_state.atout, st.session_state.contrat, st.session_state.annonce_attaque, st.session_state.annonce_defence, st.session_state.is_Capot, st.session_state.is_General, cartes_pli)
        
        #if result_image.dtype != np.uint8:

        result_image = (255.0 / result_image.max() * (result_image - result_image.min())).astype(np.uint8)

        # Convertir l'image résultante en BGR pour s'assurer que les couleurs sont correctes
        result_image_bgr = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR)

        # Convertir l'image BGR en PIL Image
        result_image_pil = Image.fromarray(result_image_bgr)

        st.image(result_image_pil, caption="Detection des cartes par l'IA")

        if st.session_state.is_coinche : 
            st.session_state.points_attaque_plis = st.session_state.points_attaque_plis*2
            st.session_state.points_defence_plis = st.session_state.points_defence_plis*2
        
        if st.session_state.is_surcoinche : 
            st.session_state.points_attaque_plis = st.session_state.points_attaque_plis*4
            st.session_state.points_defence_plis = st.session_state.points_defence_plis*4

        if st.session_state.is_fait is True :
            st.success(f"L'attaque de {st.session_state.equipe_attaque} réussi pour {st.session_state.points_attaque_plis} points", icon="⚔️")
        else :
            st.warning(f"La défense de {st.session_state.equipe_defence} pour {st.session_state.points_defence_plis} points", icon="🛡️")

        st.session_state.valider_tour = True

    else :
        pass


if st.session_state.valider_tour is True : 

    enregistrer_ = st.button("Valider le tour", use_container_width = True, on_click=update_key)

    if enregistrer_ :

        is_fini = False

        try :

            if st.session_state.points_DataFrame.shape[0] != 0 :

                data_to_add = [
                    {st.session_state.equipe_attaque: st.session_state.points_attaque_plis + st.session_state.points_DataFrame[st.session_state.equipe_attaque].iloc[-1], 
                    st.session_state.equipe_defence: st.session_state.points_defence_plis + st.session_state.points_DataFrame[st.session_state.equipe_defence].iloc[-1]}
                ]

                data_df = pd.DataFrame(data_to_add)
                # Ajout des lignes au DataFrame
                st.session_state.points_DataFrame = pd.concat([st.session_state.points_DataFrame, data_df], ignore_index=True)

            else :
                data_to_add = [
                    {st.session_state.equipe_attaque: st.session_state.points_attaque_plis, 
                    st.session_state.equipe_defence: st.session_state.points_defence_plis}
                ]

                data_df = pd.DataFrame(data_to_add)

                # Ajout des lignes au DataFrame
                st.session_state.points_DataFrame = pd.concat([st.session_state.points_DataFrame, data_df], ignore_index=True)

                # Verifier si la partie est finie
            for col in st.session_state.points_DataFrame.columns:
                st.session_state.point = st.session_state.points_DataFrame[col].iloc[-1]
                if(st.session_state.point > st.session_state.points_partie) :
                    is_fini = True 
                
        except :
            pass

        st.session_state.equipe_defence = None

        if is_fini is True :
            fin_partie()

        st.session_state.valider_tour = False

        st.rerun()



    


  
     











