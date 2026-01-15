from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Food:
    name: str
    calories: float
    proteins: float
    carbs: float
    fats: float
    category: str = "Geral"
    tags: List[str] = field(default_factory=list)
    
    def __repr__(self):
        return f"{self.name} ({self.category} - {self.calories} kcal)"

@dataclass
class Meal:
    name: str
    foods: List[Food] = field(default_factory=list)

    @property
    def total_calories(self) -> float:
        return sum(f.calories for f in self.foods)

    @property
    def total_proteins(self) -> float:
        return sum(f.proteins for f in self.foods)

    @property
    def total_carbs(self) -> float:
        return sum(f.carbs for f in self.foods)

    @property
    def total_fats(self) -> float:
        return sum(f.fats for f in self.foods)

@dataclass
class NutritionalTargets:
    min_calories: float
    max_calories: float
    min_proteins: float
    max_proteins: float
    min_carbs: float
    max_carbs: float
    min_fats: float
    max_fats: float

@dataclass
class Menu:
    meals: List[Meal] = field(default_factory=list)
    fitness_score: float = 0.0
    targets: Optional[NutritionalTargets] = None

    @property
    def total_calories(self) -> float:
        return sum(m.total_calories for m in self.meals)

    @property
    def total_proteins(self) -> float:
        return sum(m.total_proteins for m in self.meals)
    
    @property
    def total_carbs(self) -> float:
        return sum(m.total_carbs for m in self.meals)

    @property
    def total_fats(self) -> float:
        return sum(m.total_fats for m in self.meals)
