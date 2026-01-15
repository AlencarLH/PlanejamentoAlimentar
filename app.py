import streamlit as st
import pandas as pd
import os
import sys

# Garante que o módulo src possa ser importado..
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import load_taco_data, get_foods_from_df
from src.strategies import NutritionalStrategy
from src.genetic_algorithm import GeneticAlgorithm

st.set_page_config(page_title="Planejamento Alimentar", layout="wide", page_icon="🥗")

#CSS CUSTOMIZADO PARA ESTÉTICA DE CARDS ---
st.markdown("""
<style>
    /* Fundo Global */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Container do Card */
    .meal-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box_shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }
    
    /* Cabeçalhos dentro dos cards */
    .meal-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Linha do Alimento */
    .food-item {
        font-size: 0.95rem;
        color: #555;
        padding: 4px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    
    /* Métricas Destacadas */
    .metric-value {
        font-weight: bold;
        color: #2e7d32;
    }
    
    /* Estilo da Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #97bf9a;
        border-right: 1px solid #c8e6c9;
    }
    
    /* Força cores de texto para Preto */
    .stRadio label, p, h1, h2, h3, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    csv_path = os.path.join("data", "taco.csv")
    if not os.path.exists(csv_path):
        return None
    df = load_taco_data(csv_path)
    return get_foods_from_df(df)

# BARRA LATERAL (ENTRADAS) ---
with st.sidebar:

    st.image("https://cdn-icons-png.flaticon.com/512/2515/2515183.png", width=80) 
    st.title("NutriPlan")
    
    st.subheader("Seus Dados")
    weight = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=70.0)
    height = st.number_input("Altura (cm)", min_value=100.0, max_value=250.0, value=170.0)
    age = st.number_input("Idade", min_value=10, max_value=100, value=25)
    gender = st.sidebar.selectbox("Gênero", ["Masculino", "Feminino"])
    
    activity_map = {
        "Sedentário": 1.2, 
        "Leve (1-3x/semana)": 1.375, 
        "Moderado (3-5x/semana)": 1.55, 
        "Intenso (6-7x/semana)": 1.725
    }
    
    activity = st.selectbox("Nível de Atividade", list(activity_map.keys()), index=1)
    activity_factor = activity_map[activity]
    
    gender_code = "M" if gender == "Masculino" else "F"
    
    run_btn = st.button("Gerar Cardápio", type="primary")

#  CONTEÚDO PRINCIPAL ---

# Carregar Data
foods = load_data()
if not foods:
    st.error("Erro: Arquivo `data/taco.csv` não encontrado.")
    st.stop()

if run_btn:
    with st.spinner("Otimizando sua dieta..."):
        # 1.Calcular Metas
        targets = NutritionalStrategy.from_bmi(weight, height, age, gender_code, activity_factor)
        
        # 2. Executar Algoritmo Genético
        ga = GeneticAlgorithm(foods, targets, population_size=150, generations=40)
        best_menus = ga.run()
        
        #Armazenar 
        st.session_state["menus"] = best_menus
        st.session_state["targets"] = targets

#Verificar resultados
if "menus" in st.session_state:
    menus = st.session_state["menus"]
    targets = st.session_state["targets"]
    
    st.markdown(f"<h2 style='color: black;'>📋 Sugestão de Cardápio</h2>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: black;'>As opções são geradas utilizando Algoritmo Genético nos dados da tabela TACO.</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: black; font-weight: bold;'>Meta Proteica (Hipertrofia): {targets.min_proteins:.1f} - {targets.max_proteins:.1f} g</p>", unsafe_allow_html=True)
    
    option = st.radio("Escolha uma opção:", ["Opção 1", "Opção 2", "Opção 3"], horizontal=True)
    opt_idx = int(option.split(" ")[1]) - 1
    selected_menu = menus[opt_idx]
    
    diff_cal = selected_menu.total_calories - (targets.min_calories + targets.max_calories)/2
    
    col1, col2 = st.columns([1, 1])
    
    meal_icons = {
        "Café da Manhã": "🥣",
        "Almoço": "🍛",
        "Lanche": "🍎",
        "Jantar": "🍲"
    }

    for i, meal in enumerate(selected_menu.meals):
        if i % 2 == 0:
            target_col = col1
        else:
            target_col = col2
            
        with target_col:
            icon = meal_icons.get(meal.name, "🍽️") # Emoji fera
            
            items_html = ""
            for food in meal.foods:
                items_html += f"""
<div class="food-item">
    • <b>{food.name}</b> <br>
    <span style="font-size:0.8rem; color:#888;">{food.category}</span>
</div>
"""
            
            card_html = f"""
<div class="meal-card">
    <div class="meal-header">
        <span>{icon}</span>
        <span>{meal.name}</span>
    </div>
    <div style="margin-bottom:10px; font-size:0.9rem; color:#777;">
        {meal.total_calories:.0f} kcal | P: {meal.total_proteins:.1f}g | C: {meal.total_carbs:.1f}g | F: {meal.total_fats:.1f}g
    </div>
    {items_html}
</div>
"""
            st.markdown(card_html, unsafe_allow_html=True)
            
    #  Resumo Diário
    st.markdown("---")
    st.markdown("### 📊 Resumo Diário")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Calorias", f"{selected_menu.total_calories:.0f}") # Removed delta
    c2.metric("Proteínas", f"{selected_menu.total_proteins:.1f}g")
    c3.metric("Carboidratos", f"{selected_menu.total_carbs:.1f}g")
    c4.metric("Gorduras", f"{selected_menu.total_fats:.1f}g")

else:
    st.info("👈 Configure seus dados na barra lateral e clique em 'Gerar Cardápio' para começar.")
    
    st.markdown("### Exemplo de Layout")
    st.markdown("""
<div class="meal-card">
    <div class="meal-header">🥣 Café da Manhã (Exemplo)</div>
    <div class="food-item">• Pão Francês</div>
    <div class="food-item">• Queijo Minas</div>
    <div class="food-item">• Café com Leite</div>
</div>
""", unsafe_allow_html=True)
