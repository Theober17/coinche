import streamlit as st
import pandas as pd

def main():

    col1, col2, col3 = st.columns(3)

    with col2:
        
        st.image("logo_coinche_fondblanc.png")

        st.session_state.points_partie = st.number_input("Nombre de points :", value=2000, min_value=500, max_value=5000, step = 500)

        st.text("")
        st.write('Equipe 1 :')
        joueur1 = st.text_input("Joueur 1", "😎")
        joueur2 = st.text_input("Joueur 2", "😁")

        st.text("")

        st.write('Equipe 2 :')
        joueur3 = st.text_input("Joueur 3", "🫡")
        joueur4 = st.text_input("Joueur 4", "🤑")

        st.session_state.equipe1 = f"{joueur1} x {joueur2}"
        st.session_state.equipe2 = f"{joueur3} x {joueur4}"

        st.session_state.points_DataFrame = pd.DataFrame(columns=[st.session_state["equipe1"], st.session_state["equipe2"]])

        st.text("")

        jouer = st.button("♣️&nbsp;&nbsp;&nbsp;&nbsp;Jouer&nbsp;&nbsp;&nbsp;&nbsp;♠️", use_container_width = True)
        if jouer : 
            st.switch_page("pages/Jeu.py")

    

if __name__ == "__main__":
    main()

