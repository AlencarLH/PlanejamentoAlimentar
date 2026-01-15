from .models import NutritionalTargets

class NutritionalStrategy:
    @staticmethod
    def get_targets(age: int, gender: str = 'M', weight_kg: float = 70.0, height_cm: float = 170.0, activity_level: float = 1.2) -> NutritionalTargets:
        # Fallback padrão
        return NutritionalStrategy.for_general_adult()

    @staticmethod
    def for_age_group(age: int) -> NutritionalTargets:
        # Lógica original do projeto para grupos etários escolares. (alterado para grupos gerais)
        # os valores são aproximações baseadas no script original
        
        if 4 <= age <= 5:
           
            return NutritionalTargets(
                min_calories=1300, max_calories=1400,
                min_carbs=170, max_carbs=180,
                min_proteins=25, max_proteins=35,
                min_fats=40, max_fats=60 #Estimado
            )
        elif 6 <= age <= 10:
            return NutritionalTargets(
                min_calories=1600, max_calories=1700,
                min_carbs=230, max_carbs=240,
                min_proteins=40, max_proteins=50,
                min_fats=50, max_fats=70
            )
        elif 11 <= age <= 15:
            return NutritionalTargets(
                min_calories=2300, max_calories=2450,
                min_carbs=340, max_carbs=350,
                min_proteins=60, max_proteins=70,
                min_fats=60, max_fats=80
            )
        else:
            return NutritionalStrategy.for_general_adult()

    @staticmethod
    def for_general_adult() -> NutritionalTargets:
        return NutritionalTargets(
            min_calories=1800, max_calories=2200,
            min_carbs=250, max_carbs=300,
            min_proteins=70, max_proteins=100,
            min_fats=60, max_fats=90
        )

    @staticmethod
    def from_bmi(weight: float, height: float, age: int, gender: str, activity_factor: float = 1.375) -> NutritionalTargets:
        
        # Calculo das metas baseadas na TMB de Harris-Benedict + fator de atividade
        
        #Equação de Harris-Benedict
        if gender.lower() == 'm':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        
        tdee = bmr * activity_factor
        
        # > Macros (divisão aproximada: 50% carb, 20% prot, 30% gord)
        # > 1g Carb = 4kcal, 1g Prot = 4kcal, 1g Gord = 9kcal
        
        target_calories = tdee
        
        carbs_g = (target_calories * 0.50) / 4
        prot_g = (target_calories * 0.20) / 4
        fats_g = (target_calories * 0.30) / 9
        
        margin = 0.10 # margem de 10%
        
        return NutritionalTargets(
            min_calories=target_calories * (1 - margin),
            max_calories=target_calories * (1 + margin),
            min_carbs=carbs_g * (1 - margin),
            max_carbs=carbs_g * (1 + margin),
            min_proteins=prot_g * (1 - margin),
            max_proteins=prot_g * (1 + margin),
            min_fats=fats_g * (1 - margin),
            max_fats=fats_g * (1 + margin)
        )
