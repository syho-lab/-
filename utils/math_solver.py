from sympy import *
from sympy.parsing.sympy_parser import parse_expr
import re

class AdvancedMathSolver:
    def __init__(self):
        self.x, self.y, self.z = symbols('x y z')
    
    def solve_with_steps(self, expression: str) -> dict:
        """Решает выражение с пошаговым объяснением"""
        try:
            # Очистка выражения
            clean_expr = self.clean_expression(expression)
            
            # Определение типа задачи
            task_type = self.identify_task_type(clean_expr)
            
            # Решение в зависимости от типа
            if task_type == "equation":
                return self.solve_equation(clean_expr)
            elif task_type == "derivative":
                return self.solve_derivative(clean_expr)
            elif task_type == "integral":
                return self.solve_integral(clean_expr)
            else:
                return self.solve_expression(clean_expr)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "steps": []
            }
    
    def clean_expression(self, expr: str) -> str:
        """Очищает и нормализует выражение"""
        # Заменяем общепринятые обозначения
        expr = expr.replace('^', '**')
        expr = expr.replace('÷', '/')
        return expr.strip()
    
    def identify_task_type(self, expr: str) -> str:
        """Определяет тип математической задачи"""
        if 'solve(' in expr:
            return "equation"
        elif 'diff(' in expr or 'derivative' in expr:
            return "derivative" 
        elif 'integrate(' in expr or 'integral' in expr:
            return "integral"
        elif '=' in expr:
            return "equation"
        else:
            return "expression"
    
    def solve_expression(self, expr: str) -> dict:
        """Решает обычное математическое выражение"""
        parsed = parse_expr(expr, transformations='all')
        steps = [
            f"**Исходное выражение:** `{expr}`",
            "**Шаг 1:** Парсинг и анализ выражения",
            "**Шаг 2:** Вычисление значения",
            f"**Шаг 3:** Упрощение результата"
        ]
        
        result = simplify(parsed)
        
        return {
            "success": True,
            "result": f"`{result}`",
            "steps": steps
        }
    
    def solve_equation(self, expr: str) -> dict:
        """Решает уравнения"""
        # Извлекаем уравнение из solve()
        if expr.startswith('solve('):
            equation = expr[6:-1].split(',')[0]
        else:
            equation = expr
        
        parsed = parse_expr(equation, transformations='all')
        steps = [
            f"**Уравнение:** `{equation}`",
            "**Шаг 1:** Приведение к стандартному виду",
            "**Шаг 2:** Нахождение корней уравнения"
        ]
        
        solutions = solve(parsed, self.x)
        
        return {
            "success": True,
            "result": f"Корни уравнения: `{solutions}`",
            "steps": steps
        }

# Глобальный экземпляр решателя
math_solver = AdvancedMathSolver()
