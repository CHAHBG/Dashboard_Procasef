
        tooltip=["mois:N", "Type:N", "Nombre:Q"]
    ).properties(height=400)
    
    st.altair_chart(bar_chart, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📈 Évolution de l'objectif cumulé")
    
    area_chart = alt.Chart(df).mark_area(opacity=0.3, color="lightblue").encode(
        x=alt.X("mois:N", title="Mois", sort=list(df["mois"])),
        y=alt.Y("objectif_total:Q", title="Objectif Cumulé"),
        tooltip=["mois:N", "objectif_total:Q"]
    ).properties(height=350)
    
    ligne_levés = alt.Chart(pd.DataFrame({
        "y": [realises_total],
        "text": ["Levés actuels"]
    })).mark_rule(color='green', strokeDash=[4, 4]).encode(
        y='y:Q'
    ) + alt.Chart(pd.DataFrame({
        "y": [realises_total],
        "text": [f"↳ {realises_total:,} levés"]
    })).mark_text(align="left", dx=5, dy=-5, color="green").encode(
        y="y:Q",
        text="text:N"
    )
    
    st.altair_chart(area_chart + ligne_levés, use_container_width=True)
    
    # Animation des vagues en bas de page
    st.markdown("---")
    st.subheader("🌊 Progression globale")
    
    # Créer les colonnes pour afficher trois vagues côte à côte
    wave_cols = st.columns(3)
    
    # Progression totale
    wave_cols[0].markdown(
        wave_animation(
            realises_total, 
            objectif_total, 
            f"{progression_pct:.1f}% total"
        ), 
        unsafe_allow_html=True
    )
    
    # Moyenne mensuelle (exemple)
    mois_ecoules = len(df)
    moyenne_mensuelle = realises_total / mois_ecoules if mois_ecoules > 0 else 0
    objectif_mensuel_moyen = df["objectif_mensuel"].mean()
    pourcentage_mensuel = (moyenne_mensuelle / objectif_mensuel_moyen * 100) if objectif_mensuel_moyen > 0 else 0
    
    wave_cols[1].markdown(
        wave_animation(
            moyenne_mensuelle, 
            objectif_mensuel_moyen, 
            f"{pourcentage_mensuel:.1f}% mensuel"
        ), 
        unsafe_allow_html=True
    )
    
    # Projection de fin d'année (exemple)
    projection_annuelle = (realises_total / mois_ecoules) * 12 if mois_ecoules > 0 else 0
    pct_projection = (projection_annuelle / objectif_total * 100) if objectif_total > 0 else 0
    
    wave_cols[2].markdown(
        wave_animation(
            projection_annuelle, 
            objectif_total, 
            f"{pct_projection:.1f}% projeté"
        ), 
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    st.subheader("📋 Données complètes")
    st.dataframe(df, use_container_width=True)

# Appel de la fonction principale
if __name__ == "__main__":
    afficher_projections_2025()
