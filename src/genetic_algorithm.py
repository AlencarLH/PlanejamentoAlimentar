import random
import copy
from typing import List, Callable
from .models import Food, Meal, Menu, NutritionalTargets

class GeneticAlgorithm:
    def __init__(self, 
                 foods: List[Food], 
                 targets: NutritionalTargets,
                 population_size: int = 200, 
                 generations: int = 50,
                 mutation_rate: float = 0.1,
                 elite_size: int = 4):
        self.foods = foods
        self.targets = targets
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.population: List[Menu] = []

    def initialize_population(self):
        self.population = []
        for _ in range(self.population_size):
            self.population.append(self._generate_random_menu())

    def _generate_random_menu(self) -> Menu:
       
        menu = Menu(meals=[
            self._create_template_meal("Café da Manhã", [
                {"type": "cat", "val": "Frutas"},
                {"type": "tag", "val": "DAIRY"},
                {"type": "tag", "val": "BREAKFAST_CEREAL"}
            ]),
            self._create_template_meal("Almoço", [
                {"type": "tag", "val": "LUNCH_CARB"},
                {"type": "cat", "val": "Leguminosas"}, # Maioria dos feijões são cozidos se não filtrados por 'cru'
                {"type": "tag", "val": "MEAT"},
                {"type": "cat", "val": "Verduras"}
            ]),
            self._create_template_meal("Lanche", [
                {"type": "cat", "val": "Frutas"},
                {"type": "tag", "val": "DAIRY"}
            ]),
            self._create_template_meal("Jantar", [
                {"type": "tag", "val": "LUNCH_CARB"}, # Jantar leve
                {"type": "tag", "val": "MEAT"},
                {"type": "cat", "val": "Verduras"}
            ])
        ])
        return menu

    def _create_template_meal(self, name: str, requirements: List[dict]) -> Meal:
        items = []
        for req in requirements:
            candidates = []
            if req["type"] == "cat":
                candidates = [f for f in self.foods if req["val"].lower() in f.category.lower()]
            elif req["type"] == "tag":
                candidates = [f for f in self.foods if req["val"] in f.tags]
            
            if not candidates:
                #Fallback: correspondência simples de categoria ou aleatório
                candidates = self.foods
            
            items.append(random.choice(candidates))
            
        return Meal(name=name, foods=items)

    def calculate_fitness(self, menu: Menu) -> float:
        # Fitness = 1 / (1 + Erro)
        # Erro = Soma dos desvios quadrados das metas (normalizado)
        
        cals = menu.total_calories
        prots = menu.total_proteins
        carbs = menu.total_carbs
        fats = menu.total_fats
        
        error = 0.0
        # Penaliza se estiver fora do intervalo
        # Eleva ao quadrado para penalizar outliers mais fortemente
        
        if cals < self.targets.min_calories:
            error += ((self.targets.min_calories - cals) / 100) ** 2
        elif cals > self.targets.max_calories:
            error += ((cals - self.targets.max_calories) / 100) ** 2
            
        if prots < self.targets.min_proteins:
            error += ((self.targets.min_proteins - prots) / 10) ** 2
        elif prots > self.targets.max_proteins:
            error += ((prots - self.targets.max_proteins) / 10) ** 2

        if carbs < self.targets.min_carbs:
            error += ((self.targets.min_carbs - carbs) / 10) ** 2
        elif carbs > self.targets.max_carbs:
            error += ((carbs - self.targets.max_carbs) / 10) ** 2
            
        if fats < self.targets.min_fats:
            error += ((self.targets.min_fats - fats) / 10) ** 2
        elif fats > self.targets.max_fats:
            error += ((fats - self.targets.max_fats) / 10) ** 2
            
        return 1.0 / (1.0 + error)

    def select_parents(self) -> List[Menu]:
        tournament_size = 5
        parents = []
        for _ in range(self.population_size - self.elite_size):
            tournament = random.sample(self.population, tournament_size)
            winner = max(tournament, key=lambda m: m.fitness_score)
            parents.append(winner)
        return parents

    def crossover(self, parent1: Menu, parent2: Menu) -> Menu:
        #Crossover uniforme no nível da refeicao
        new_meals = []
        for i in range(len(parent1.meals)):
            if random.random() < 0.5:
                
                new_meals.append(copy.deepcopy(parent1.meals[i]))
            else:
                new_meals.append(copy.deepcopy(parent2.meals[i]))
        return Menu(meals=new_meals)

    def mutate(self, menu: Menu):
        for meal in menu.meals:
            if random.random() < self.mutation_rate:
              
                # Reduzimos probabilidade de add/remove para manter a estrutura "Template" estável
                mutation_type = random.choice(['replace', 'replace', 'replace', 'add', 'remove'])
                
                if mutation_type == 'replace' and len(meal.foods) > 0:
                    idx = random.randint(0, len(meal.foods) - 1)
                    old_food = meal.foods[idx]
                    
                    #Tenta encontrar um substituto com as MESMAS TAGS primeiro
                    candidates = []
                    #Heurística: Se alimento antigo tem tags específicas, tenta manter.
                    priority_tags = ["MEAT", "LUNCH_CARB", "BREAKFAST_CEREAL", "DAIRY"]
                    target_tag = next((t for t in priority_tags if t in old_food.tags), None)
                    
                    if target_tag:
                         candidates = [f for f in self.foods if target_tag in f.tags]
                    
                    if not candidates:
                        candidates = [f for f in self.foods if f.category == old_food.category]
                        
                    if not candidates:
                        candidates = self.foods
                        
                    meal.foods[idx] = random.choice(candidates)
                
                elif mutation_type == 'add':
                    #Adiciona alimento aleatório
                    meal.foods.append(random.choice(self.foods))
                    
                elif mutation_type == 'remove' and len(meal.foods) > 1:
                    idx = random.randint(0, len(meal.foods) - 1)
                    meal.foods.pop(idx)

    def run(self, progress_callback: Callable = None) -> List[Menu]:
        self.initialize_population()
        
        for generation in range(self.generations):
            #Avaliacao de fitness
            for individual in self.population:
                individual.fitness_score = self.calculate_fitness(individual)
            
            # Ordena por fitness (decrescente)
            self.population.sort(key=lambda x: x.fitness_score, reverse=True)
            
            best_fitness = self.population[0].fitness_score
            if progress_callback:
                progress_callback(generation, best_fitness)
            
            #Elitismo: mantém os melhores N
            next_population = self.population[:self.elite_size]
            
            #Seleção
            parents = self.select_parents() 
            
            #Loop de Generação
            while len(next_population) < self.population_size:
                p1 = random.choice(parents)
                p2 = random.choice(parents)
                child = self.crossover(p1, p2)
                self.mutate(child)
                next_population.append(child)
            
            self.population = next_population

        # >>> Retorna os top 3 menus únicos
        unique_menus = []
        seen_calories = set()
        
        for menu in self.population:
            cal_int = int(menu.total_calories)
            if cal_int not in seen_calories:
                unique_menus.append(menu)
                seen_calories.add(cal_int)
            if len(unique_menus) >= 3:
                break
                
        return unique_menus
