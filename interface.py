import streamlit as st

col1, col2, col3 = st.columns(3)

with col2:
    st.image("logo_coinche.png")

col1, col2, col3 = st.columns(3)

with col1:
    points_partie = st.number_input("Nombre de points :", min_value=500, max_value=5000, step = 500)

with col2:
    st.write('Equipe 1 :')
    Joueur1 = st.text_input("Joueur 1", "😎")
    Joueur2 = st.text_input("Joueur 2", "😁")

with col3:
    st.write('Equipe 2 :')
    Joueur3 = st.text_input("Joueur 3", "🫡")
    Joueur4 = st.text_input("Joueur 4", "🤑")
    


if Joueur1 and Joueur2 and Joueur3 and Joueur4 :
    st.page_link("pages/jeu.py", label="Accéder au Jeux !", icon="♣️")
