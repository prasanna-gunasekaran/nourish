import pytest
from app.nutrition.service import NutritionService
from app.models.schemas import ConfidenceLevel

def test_nutrition_lookup_and_calc():
    service = NutritionService()
    
    # 1. Idli lookup
    idli = service.calculate_food_item("idli", quantity=3.0, unit="piece")
    assert idli.food_name == "Idli"
    assert idli.calories == pytest.approx(174.0, 0.1)
    assert idli.protein_g == pytest.approx(6.0, 0.1)
    assert idli.confidence == ConfidenceLevel.HIGH

    # 2. Vada lookup
    vada = service.calculate_food_item("vada", quantity=1.0, unit="piece")
    assert vada.food_name == "Medu Vada"
    assert vada.calories == pytest.approx(150.0, 0.1)

    # 3. Eggs lookup
    eggs = service.calculate_food_item("eggs", quantity=2.0, unit="piece")
    assert eggs.calories == pytest.approx(140.0, 0.1)

    # 4. Meal total calculation
    tot_cals, tot_p, tot_c, tot_f, tot_fib, conf = service.calculate_meal_totals([idli, vada, eggs])
    assert tot_cals == pytest.approx(464.0, 0.1)
    assert tot_p == pytest.approx(20.0, 0.1)
