import pandas as pd
import numpy as np
from typing import List
from .models import Food
import csv

def clean_number(value):
   
    if isinstance(value, (int, float)):
        return float(value)
    
    if pd.isna(value) or value == 'NA' or value == '*':
        return 0.0
    
    if isinstance(value, str):
        value = value.strip()
        if value == 'Tr' or value == 'tr':
            return 0.0
        if value == '':
            return 0.0
        value = value.replace(',', '.')
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0

def load_taco_data(csv_path: str) -> pd.DataFrame:    
    # Precisamos analisar manualmente para capturar os cabeçalhos de categoria "stateful"
    foods_data = []
    current_category = "Geral"
    
    with open(csv_path, 'r', encoding='latin1') as f:
        reader = csv.reader(f, delimiter=';')
        
        # Se Col 0 é número -> É um alimento.
        # Se Col 0 é Texto e Col 1 vazio -> Provável cabeçalho de categoria.
        # Se Col 1 é "Descrição dos alimentos" -> É cabeçalho de coluna para pular.
        
        for i, row in enumerate(reader):
            if not row: continue
            
            col0 = row[0].strip() if len(row) > 0 else ""
            col1 = row[1].strip() if len(row) > 1 else ""
          
            if "Descrição dos alimentos" in col1 or "Número do" in col0:
                continue
          
            if col0 and not col0.replace('.', '').isdigit():
                if "Número" in col0 or "Umidade" in col0 or "Carbo" in col0:
                    continue
                
                current_category = col0
                continue
                
           
            if col0.isdigit():
                if len(row) < 9: continue # linha inválida
            
                # 1: Descrição (Nome)
                # 3: Calorias (kcal)
                # 5: Proteínas
                # 6: Lipídeos (Gordura)
                # 8: Carboidratos
                
                try:
                    name = row[1]
                    cals = clean_number(row[3])
                    prot = clean_number(row[5])
                    fat = clean_number(row[6])
                    carb = clean_number(row[8])
                    
                    foods_data.append({
                        'name': name,
                        'calories': cals,
                        'proteins': prot,
                        'carbs': carb,
                        'fats': fat,
                        'category': current_category
                    })
                except (ValueError, IndexError):
                    continue

    df = pd.DataFrame(foods_data)
    return df

def get_tags(name: str, category: str) -> List[str]:
    tags = []
    name_lower = name.lower()
    cat_lower = category.lower()

    # 1. Filtragem para alimentos "desagradáveis" para dieta no dia a dia (Carnes/Leguminosas cruas)
    is_raw = 'cru' in name_lower
    
    # Categorias que são UNSAFE se cruas
    unsafe_raw_cats = ['carnes', 'pescados', 'leguminosas', 'ovos', 'miúdos', 'vísceras']
    
    if is_raw and any(c in cat_lower for c in unsafe_raw_cats):
        #Exceção: algumas coisas podem ser seguras (Sushi) mas no contexto do projeto 'Peixe cru' assume necessidade de preparo
        tags.append("UNSAFE")
    elif is_raw and 'mandioca' in name_lower: # Mandioca crua é tóxica
        tags.append("UNSAFE")
    
    
    # Carbo Café da Manhã: Pães, Bolos, Biscoitos, Cereais
    if 'pão' in name_lower or 'bolo' in name_lower or 'biscoito' in name_lower or 'torrada' in name_lower:
        tags.append("BREAKFAST_CEREAL")
    elif 'cereal' in name_lower and 'matinal' in name_lower:
        tags.append("BREAKFAST_CEREAL")
    elif 'mingau' in name_lower:
        tags.append("BREAKFAST_CEREAL")
        
    # Carbo Almoço: Arroz, Macarrão, Polenta, Batata, Mandioca, Farinhas
    if 'arroz' in name_lower or 'macarrão' in name_lower or 'polenta' in name_lower or 'milho' in name_lower:
        # Exclui Curau dependendo do contexto, mas milho grão é almoço
        if 'curau' not in name_lower and 'mingau' not in name_lower:
             tags.append("LUNCH_CARB")
    elif 'farinha' in name_lower and 'láctea' not in name_lower: # Farinha de mandioca/milho
        tags.append("LUNCH_CARB")
    elif 'batata' in name_lower or 'mandioca' in name_lower or 'inhame' in name_lower or 'cará' in name_lower:
        tags.append("LUNCH_CARB")
    elif 'lasanha' in name_lower or 'pizza' in name_lower or 'pastel' in name_lower:
        tags.append("LUNCH_CARB") # Pratos principais

    # Carnes
    if any(c in cat_lower for c in ['carnes', 'pescados', 'ovos', 'vísceras']):
        if "UNSAFE" not in tags:
            tags.append("MEAT")

    # Laticínios
    if 'leite' in cat_lower or 'queijo' in name_lower or 'iogurte' in name_lower:
        tags.append("DAIRY")
        
    return tags

def get_foods_from_df(df: pd.DataFrame) -> List[Food]:
    foods = []
    for _, row in df.iterrows():
        tags = get_tags(row['name'], row['category'])

        if "UNSAFE" in tags:
            continue
            
        foods.append(Food(
            name=row['name'],
            calories=row['calories'],
            proteins=row['proteins'],
            carbs=row['carbs'],
            fats=row['fats'],
            category=row['category'],
            tags=tags
        ))
    return foods
