"""
Grocery Optimization System — Core Module
==========================================
Handles ingredient normalization, smart grouping, quantity merging,
and category assignment for weekly meal plan grocery lists.
"""

import re
from collections import defaultdict


# ═══════════════════════════════════════════════════════════════
# 📏 UNIT CONVERSION TABLES
# ═══════════════════════════════════════════════════════════════

# Canonical unit families — convert everything to the base unit for merging
UNIT_FAMILIES = {
    # Mass: base = g
    'g':   {'family': 'mass', 'to_base': 1},
    'gm':  {'family': 'mass', 'to_base': 1},
    'gms': {'family': 'mass', 'to_base': 1},
    'gram': {'family': 'mass', 'to_base': 1},
    'grams': {'family': 'mass', 'to_base': 1},
    'kg':  {'family': 'mass', 'to_base': 1000},
    'kgs': {'family': 'mass', 'to_base': 1000},
    'kilogram': {'family': 'mass', 'to_base': 1000},
    'kilograms': {'family': 'mass', 'to_base': 1000},
    'oz':  {'family': 'mass', 'to_base': 28.3495},
    'ounce': {'family': 'mass', 'to_base': 28.3495},
    'ounces': {'family': 'mass', 'to_base': 28.3495},
    'lb':  {'family': 'mass', 'to_base': 453.592},
    'lbs': {'family': 'mass', 'to_base': 453.592},
    'pound': {'family': 'mass', 'to_base': 453.592},
    'pounds': {'family': 'mass', 'to_base': 453.592},

    # Volume: base = ml
    'ml':    {'family': 'volume', 'to_base': 1},
    'milliliter': {'family': 'volume', 'to_base': 1},
    'milliliters': {'family': 'volume', 'to_base': 1},
    'l':     {'family': 'volume', 'to_base': 1000},
    'liter': {'family': 'volume', 'to_base': 1000},
    'liters': {'family': 'volume', 'to_base': 1000},
    'litre': {'family': 'volume', 'to_base': 1000},
    'litres': {'family': 'volume', 'to_base': 1000},
    'cup':   {'family': 'volume', 'to_base': 236.588},
    'cups':  {'family': 'volume', 'to_base': 236.588},
    'tbsp':  {'family': 'volume', 'to_base': 14.787},
    'tablespoon': {'family': 'volume', 'to_base': 14.787},
    'tablespoons': {'family': 'volume', 'to_base': 14.787},
    'tsp':   {'family': 'volume', 'to_base': 4.929},
    'teaspoon': {'family': 'volume', 'to_base': 4.929},
    'teaspoons': {'family': 'volume', 'to_base': 4.929},

    # Count: base = piece
    'piece': {'family': 'count', 'to_base': 1},
    'pieces': {'family': 'count', 'to_base': 1},
    'pcs':   {'family': 'count', 'to_base': 1},
    'whole': {'family': 'count', 'to_base': 1},
    'nos':   {'family': 'count', 'to_base': 1},
    'no':    {'family': 'count', 'to_base': 1},
    'bunch': {'family': 'count', 'to_base': 1},
    'bunches': {'family': 'count', 'to_base': 1},
    'clove': {'family': 'count', 'to_base': 1},
    'cloves': {'family': 'count', 'to_base': 1},
    'slice': {'family': 'count', 'to_base': 1},
    'slices': {'family': 'count', 'to_base': 1},
    'medium': {'family': 'count', 'to_base': 1},
    'large':  {'family': 'count', 'to_base': 1},
    'small':  {'family': 'count', 'to_base': 1},
}

# Human-friendly display units per family
DISPLAY_UNITS = {
    'mass':   {'threshold': 1000, 'small': 'g',  'large': 'kg', 'factor': 1000},
    'volume': {'threshold': 1000, 'small': 'ml', 'large': 'L',  'factor': 1000},
    'count':  {'threshold': 9999, 'small': 'pcs', 'large': 'pcs', 'factor': 1},
}


# ═══════════════════════════════════════════════════════════════
# 🏷️ INGREDIENT ALIAS MAP (Smart Grouping)
# ═══════════════════════════════════════════════════════════════

# Maps various forms/preparations to a single canonical name
INGREDIENT_ALIASES = {
    # Onion variants
    'chopped onion': 'onion', 'diced onion': 'onion', 'sliced onion': 'onion',
    'red onion': 'onion', 'white onion': 'onion', 'yellow onion': 'onion',
    'onions': 'onion', 'spring onion': 'spring onion',
    # Tomato
    'chopped tomato': 'tomato', 'diced tomato': 'tomato', 'tomatoes': 'tomato',
    'cherry tomato': 'cherry tomato', 'cherry tomatoes': 'cherry tomato',
    'roma tomato': 'tomato', 'roma tomatoes': 'tomato',
    # Garlic
    'garlic clove': 'garlic', 'garlic cloves': 'garlic', 'minced garlic': 'garlic',
    'crushed garlic': 'garlic', 'chopped garlic': 'garlic',
    # Ginger
    'fresh ginger': 'ginger', 'grated ginger': 'ginger', 'minced ginger': 'ginger',
    'ginger root': 'ginger',
    # Chicken
    'chicken breast': 'chicken breast', 'chicken breasts': 'chicken breast',
    'boneless chicken': 'chicken breast', 'chicken thigh': 'chicken thigh',
    'chicken thighs': 'chicken thigh',
    # Rice
    'basmati rice': 'basmati rice', 'brown rice': 'brown rice',
    'white rice': 'rice', 'cooked rice': 'rice', 'steamed rice': 'rice',
    # Peppers
    'bell pepper': 'bell pepper', 'bell peppers': 'bell pepper',
    'green bell pepper': 'bell pepper', 'red bell pepper': 'bell pepper',
    'capsicum': 'bell pepper',
    # Potato
    'potatoes': 'potato', 'diced potato': 'potato', 'chopped potato': 'potato',
    'boiled potato': 'potato', 'mashed potato': 'potato',
    # Spinach
    'baby spinach': 'spinach', 'fresh spinach': 'spinach',
    # Lemon
    'lemon juice': 'lemon', 'lemons': 'lemon', 'fresh lemon juice': 'lemon',
    # Egg
    'eggs': 'egg', 'boiled egg': 'egg', 'whole egg': 'egg',
    # Milk
    'whole milk': 'milk', 'low-fat milk': 'milk', 'skimmed milk': 'milk',
    'skim milk': 'milk',
    # Olive oil
    'extra virgin olive oil': 'olive oil', 'virgin olive oil': 'olive oil',
    # Butter
    'unsalted butter': 'butter', 'salted butter': 'butter',
    # Yogurt
    'greek yogurt': 'yogurt', 'plain yogurt': 'yogurt', 'yoghurt': 'yogurt',
    'curd': 'yogurt',
    # Cucumber
    'cucumbers': 'cucumber', 'sliced cucumber': 'cucumber',
    # Carrot
    'carrots': 'carrot', 'diced carrot': 'carrot', 'chopped carrot': 'carrot',
    'grated carrot': 'carrot',
    # Cheese
    'cheddar cheese': 'cheddar cheese', 'mozzarella cheese': 'mozzarella cheese',
    'parmesan cheese': 'parmesan cheese', 'cottage cheese': 'cottage cheese',
    'paneer': 'paneer',
}

# Preparation words to strip from ingredient names for matching
PREP_WORDS = {
    'chopped', 'diced', 'sliced', 'minced', 'crushed', 'grated',
    'fresh', 'dried', 'ground', 'whole', 'raw', 'cooked', 'boiled',
    'steamed', 'roasted', 'baked', 'fried', 'blanched', 'peeled',
    'trimmed', 'washed', 'rinsed', 'soaked', 'finely', 'roughly',
    'thinly', 'thickly', 'cubed', 'julienned', 'shredded',
}


# ═══════════════════════════════════════════════════════════════
# 🗂️ GROCERY CATEGORIES
# ═══════════════════════════════════════════════════════════════

CATEGORY_MAP = {
    # Produce
    'onion': 'Produce', 'tomato': 'Produce', 'potato': 'Produce',
    'garlic': 'Produce', 'ginger': 'Produce', 'carrot': 'Produce',
    'cucumber': 'Produce', 'spinach': 'Produce', 'lettuce': 'Produce',
    'bell pepper': 'Produce', 'broccoli': 'Produce', 'cauliflower': 'Produce',
    'zucchini': 'Produce', 'mushroom': 'Produce', 'cabbage': 'Produce',
    'eggplant': 'Produce', 'celery': 'Produce', 'kale': 'Produce',
    'avocado': 'Produce', 'corn': 'Produce', 'peas': 'Produce',
    'green beans': 'Produce', 'cherry tomato': 'Produce', 'spring onion': 'Produce',
    'sweet potato': 'Produce', 'beetroot': 'Produce', 'radish': 'Produce',
    # Fruits
    'lemon': 'Fruits', 'banana': 'Fruits', 'apple': 'Fruits',
    'orange': 'Fruits', 'mango': 'Fruits', 'strawberry': 'Fruits',
    'blueberry': 'Fruits', 'grape': 'Fruits', 'pineapple': 'Fruits',
    'watermelon': 'Fruits', 'kiwi': 'Fruits', 'papaya': 'Fruits',
    # Protein
    'chicken breast': 'Protein', 'chicken thigh': 'Protein',
    'chicken': 'Protein', 'salmon': 'Protein', 'tuna': 'Protein',
    'shrimp': 'Protein', 'egg': 'Protein', 'tofu': 'Protein',
    'lentils': 'Protein', 'chickpeas': 'Protein', 'kidney beans': 'Protein',
    'black beans': 'Protein', 'paneer': 'Protein', 'fish': 'Protein',
    'turkey': 'Protein', 'beef': 'Protein', 'lamb': 'Protein',
    'prawns': 'Protein', 'mutton': 'Protein',
    # Dairy
    'milk': 'Dairy', 'yogurt': 'Dairy', 'butter': 'Dairy',
    'cheese': 'Dairy', 'cream': 'Dairy', 'cheddar cheese': 'Dairy',
    'mozzarella cheese': 'Dairy', 'parmesan cheese': 'Dairy',
    'cottage cheese': 'Dairy', 'sour cream': 'Dairy',
    # Grains & Staples
    'rice': 'Grains & Staples', 'basmati rice': 'Grains & Staples',
    'brown rice': 'Grains & Staples', 'oats': 'Grains & Staples',
    'quinoa': 'Grains & Staples', 'pasta': 'Grains & Staples',
    'bread': 'Grains & Staples', 'flour': 'Grains & Staples',
    'wheat flour': 'Grains & Staples', 'noodles': 'Grains & Staples',
    'tortilla': 'Grains & Staples', 'couscous': 'Grains & Staples',
    # Oils & Condiments
    'olive oil': 'Oils & Condiments', 'vegetable oil': 'Oils & Condiments',
    'coconut oil': 'Oils & Condiments', 'sesame oil': 'Oils & Condiments',
    'soy sauce': 'Oils & Condiments', 'vinegar': 'Oils & Condiments',
    'mustard': 'Oils & Condiments', 'ketchup': 'Oils & Condiments',
    'mayonnaise': 'Oils & Condiments', 'hot sauce': 'Oils & Condiments',
    'honey': 'Oils & Condiments',
    # Spices & Herbs
    'salt': 'Spices & Herbs', 'pepper': 'Spices & Herbs',
    'black pepper': 'Spices & Herbs', 'cumin': 'Spices & Herbs',
    'turmeric': 'Spices & Herbs', 'paprika': 'Spices & Herbs',
    'coriander': 'Spices & Herbs', 'cinnamon': 'Spices & Herbs',
    'oregano': 'Spices & Herbs', 'basil': 'Spices & Herbs',
    'thyme': 'Spices & Herbs', 'rosemary': 'Spices & Herbs',
    'parsley': 'Spices & Herbs', 'mint': 'Spices & Herbs',
    'bay leaf': 'Spices & Herbs', 'chili powder': 'Spices & Herbs',
    'red chili': 'Spices & Herbs', 'garam masala': 'Spices & Herbs',
    'cilantro': 'Spices & Herbs', 'dill': 'Spices & Herbs',
    # Nuts & Seeds
    'almond': 'Nuts & Seeds', 'almonds': 'Nuts & Seeds',
    'walnut': 'Nuts & Seeds', 'walnuts': 'Nuts & Seeds',
    'cashew': 'Nuts & Seeds', 'cashews': 'Nuts & Seeds',
    'peanut': 'Nuts & Seeds', 'peanuts': 'Nuts & Seeds',
    'chia seeds': 'Nuts & Seeds', 'flax seeds': 'Nuts & Seeds',
    'sunflower seeds': 'Nuts & Seeds', 'pumpkin seeds': 'Nuts & Seeds',
    'sesame seeds': 'Nuts & Seeds',
}


# ═══════════════════════════════════════════════════════════════
# 🔧 INGREDIENT PARSER
# ═══════════════════════════════════════════════════════════════

class IngredientParser:
    """Parses quantity strings like '500g', '2 cups', '1/2 kg' into (amount, unit)."""

    # Regex: captures amount (int, float, fraction) and optional unit
    QTY_PATTERN = re.compile(
        r'^\s*'
        r'(\d+\s*/\s*\d+|\d+\.?\d*)\s*'  # amount: fraction or decimal
        r'([a-zA-Z]*)\s*'                  # unit (optional)
        r'$'
    )

    @staticmethod
    def parse(qty_string):
        """
        Parse a quantity string into (amount, unit).
        Examples:
            '500g' -> (500.0, 'g')
            '2 cups' -> (2.0, 'cup')
            '1/2 kg' -> (0.5, 'kg')
            '3' -> (3.0, 'piece')
        """
        if not qty_string:
            return (1.0, 'piece')

        qty_string = str(qty_string).strip().lower()

        # Handle compound quantities like "1 1/2 cups"
        compound_match = re.match(
            r'(\d+)\s+(\d+\s*/\s*\d+)\s*([a-zA-Z]*)', qty_string
        )
        if compound_match:
            whole = float(compound_match.group(1))
            frac_parts = compound_match.group(2).split('/')
            frac = float(frac_parts[0]) / float(frac_parts[1])
            unit = compound_match.group(3).strip() or 'piece'
            return (whole + frac, IngredientParser._normalize_unit(unit))

        match = IngredientParser.QTY_PATTERN.match(qty_string)
        if match:
            amount_str = match.group(1)
            unit = match.group(2).strip() or 'piece'

            # Handle fractions
            if '/' in amount_str:
                parts = amount_str.split('/')
                amount = float(parts[0]) / float(parts[1])
            else:
                amount = float(amount_str)

            return (amount, IngredientParser._normalize_unit(unit))

        # Fallback: try to extract any number
        nums = re.findall(r'\d+\.?\d*', qty_string)
        if nums:
            return (float(nums[0]), 'piece')

        return (1.0, 'piece')

    @staticmethod
    def _normalize_unit(unit):
        """Normalize unit string to a canonical short form."""
        unit = unit.lower().strip().rstrip('s') if len(unit) > 3 else unit.lower().strip()
        unit_map = {
            'gram': 'g', 'gm': 'g', 'kilogram': 'kg',
            'milliliter': 'ml', 'liter': 'l', 'litre': 'l',
            'tablespoon': 'tbsp', 'teaspoon': 'tsp',
            'ounce': 'oz', 'pound': 'lb',
        }
        return unit_map.get(unit, unit) if unit else 'piece'


# ═══════════════════════════════════════════════════════════════
# 🧹 INGREDIENT NORMALIZER
# ═══════════════════════════════════════════════════════════════

class IngredientNormalizer:
    """Normalizes ingredient names by stripping prep words and resolving aliases."""

    @staticmethod
    def normalize(name):
        """
        Normalize an ingredient name to its canonical form.
        Examples:
            'chopped onion' -> 'Onion'
            'fresh baby spinach' -> 'Spinach'
            'chicken breasts' -> 'Chicken Breast'
        """
        if not name:
            return 'Unknown'

        clean = name.lower().strip()

        # 1. Direct alias lookup
        if clean in INGREDIENT_ALIASES:
            return INGREDIENT_ALIASES[clean].title()

        # 2. Strip preparation words and try again
        words = clean.split()
        core_words = [w for w in words if w not in PREP_WORDS]
        stripped = ' '.join(core_words) if core_words else clean

        if stripped in INGREDIENT_ALIASES:
            return INGREDIENT_ALIASES[stripped].title()

        # 3. Try singular form (remove trailing 's')
        singular = stripped.rstrip('s') if len(stripped) > 3 and stripped.endswith('s') else stripped
        if singular in INGREDIENT_ALIASES:
            return INGREDIENT_ALIASES[singular].title()

        # 4. Check if singular itself is a known canonical name in the category map
        if singular in CATEGORY_MAP:
            return singular.title()
        if stripped in CATEGORY_MAP:
            return stripped.title()

        # 5. Return cleaned-up, title-cased version
        return stripped.title() if stripped else clean.title()

    @staticmethod
    def get_category(canonical_name):
        """Get the grocery aisle category for a canonical ingredient name."""
        key = canonical_name.lower()
        if key in CATEGORY_MAP:
            return CATEGORY_MAP[key]

        # Partial match fallback
        for known, cat in CATEGORY_MAP.items():
            if known in key or key in known:
                return cat

        return 'Other'


# ═══════════════════════════════════════════════════════════════
# 🛒 GROCERY OPTIMIZER (Main Engine)
# ═══════════════════════════════════════════════════════════════

class GroceryOptimizer:
    """
    Main optimization engine.
    Takes raw grocery data from AI meal plans and produces
    a consolidated, normalized, categorized grocery list.
    """

    def __init__(self):
        self.parser = IngredientParser()
        self.normalizer = IngredientNormalizer()

    def optimize(self, raw_grocery_data):
        """
        Optimize a raw grocery list from the AI.

        Args:
            raw_grocery_data: Can be:
                - dict: {"Produce": ["Item1", "Item2"], "Protein": ["Item3"]}
                - list: ["500g chicken breast", "2 onions", ...]
                - str:  "500g chicken breast\n2 onions\n..."

        Returns:
            dict: {
                "categories": {
                    "Produce": [
                        {"name": "Onion", "quantity": 1.5, "unit": "kg",
                         "display_qty": "1.5 kg", "original_items": [...]}
                    ], ...
                },
                "total_items": int,
                "total_unique": int,
                "merged_count": int
            }
        """
        # Step 1: Flatten all items into a raw list
        raw_items = self._flatten(raw_grocery_data)

        # Step 2: Parse, normalize, and group
        grouped = defaultdict(list)  # canonical_name -> [(amount, unit, original)]
        for item in raw_items:
            name, amount, unit = self._parse_item(item)
            canonical = self.normalizer.normalize(name)
            grouped[canonical].append({
                'amount': amount,
                'unit': unit,
                'original': item
            })

        # Step 3: Merge quantities and categorize
        categories = defaultdict(list)
        total_items = len(raw_items)
        merged_count = 0

        for canonical, entries in grouped.items():
            merged = self._merge_quantities(entries)
            category = self.normalizer.get_category(canonical)

            if len(entries) > 1:
                merged_count += len(entries) - 1

            categories[category].append({
                'name': canonical,
                'quantity': merged['amount'],
                'unit': merged['unit'],
                'display_qty': merged['display'],
                'original_items': [e['original'] for e in entries],
                'merge_count': len(entries)
            })

        # Sort items within each category
        for cat in categories:
            categories[cat].sort(key=lambda x: x['name'])

        # Category display order
        order = [
            'Produce', 'Fruits', 'Protein', 'Dairy',
            'Grains & Staples', 'Oils & Condiments',
            'Spices & Herbs', 'Nuts & Seeds', 'Other'
        ]
        ordered = {}
        for cat in order:
            if cat in categories:
                ordered[cat] = categories[cat]
        # Any remaining categories
        for cat in categories:
            if cat not in ordered:
                ordered[cat] = categories[cat]

        return {
            'categories': ordered,
            'total_items': total_items,
            'total_unique': len(grouped),
            'merged_count': merged_count
        }

    def _flatten(self, data):
        """Flatten various input formats into a list of item strings."""
        items = []
        if isinstance(data, dict):
            for category, item_list in data.items():
                if isinstance(item_list, list):
                    items.extend(item_list)
                elif isinstance(item_list, str):
                    items.append(item_list)
        elif isinstance(data, list):
            items = data
        elif isinstance(data, str):
            items = [line.strip() for line in data.split('\n') if line.strip()]
        return [str(item).strip() for item in items if item]

    def _parse_item(self, item_str):
        """
        Parse a grocery item string into (name, amount, unit).
        Handles formats like:
            '500g chicken breast'
            'Chicken Breast : 500g'
            '2 cups rice'
            'Onion (2 medium)'
        """
        item_str = str(item_str).strip()

        # Format: "Name : Quantity"
        if ':' in item_str:
            parts = item_str.split(':', 1)
            name = parts[0].strip()
            amount, unit = self.parser.parse(parts[1].strip())
            return (name, amount, unit)

        # Format: "Name (quantity)"
        paren_match = re.match(r'^(.+?)\s*\((.+?)\)\s*$', item_str)
        if paren_match:
            name = paren_match.group(1).strip()
            amount, unit = self.parser.parse(paren_match.group(2).strip())
            return (name, amount, unit)

        # Format: "Quantity Name" (e.g., "500g chicken breast", "2 cups rice")
        qty_name_match = re.match(
            r'^(\d+\.?\d*\s*(?:/\s*\d+)?\s*[a-zA-Z]*)\s+(.+)$', item_str
        )
        if qty_name_match:
            qty_part = qty_name_match.group(1).strip()
            name_part = qty_name_match.group(2).strip()
            amount, unit = self.parser.parse(qty_part)
            # Check if unit got eaten into name
            if unit == 'piece' and name_part:
                return (name_part, amount, unit)
            return (name_part, amount, unit)

        # Fallback: entire string is the name
        return (item_str, 1.0, 'piece')

    def _merge_quantities(self, entries):
        """
        Merge multiple quantity entries for the same ingredient.
        Converts to a common base unit if possible, then formats for display.
        """
        if len(entries) == 1:
            e = entries[0]
            display = self._format_display(e['amount'], e['unit'])
            return {'amount': e['amount'], 'unit': e['unit'], 'display': display}

        # Group by unit family
        family_totals = defaultdict(float)  # family -> total in base units
        family_units = {}  # family -> original unit (for pieces)
        uncategorized = []

        for e in entries:
            unit = e['unit'].lower()
            if unit in UNIT_FAMILIES:
                family = UNIT_FAMILIES[unit]['family']
                base_amount = e['amount'] * UNIT_FAMILIES[unit]['to_base']
                family_totals[family] += base_amount
                family_units[family] = unit
            else:
                uncategorized.append(e)

        # Pick the dominant family
        if family_totals:
            dominant = max(family_totals, key=family_totals.get)
            total_base = family_totals[dominant]
            display = self._format_from_base(total_base, dominant)
            return {
                'amount': total_base,
                'unit': DISPLAY_UNITS[dominant]['small'],
                'display': display
            }

        # If no unit families matched, just sum amounts
        total = sum(e['amount'] for e in entries)
        unit = entries[0]['unit']
        return {
            'amount': total,
            'unit': unit,
            'display': self._format_display(total, unit)
        }

    def _format_from_base(self, base_amount, family):
        """Format a base-unit amount to a human-friendly string."""
        info = DISPLAY_UNITS.get(family)
        if not info:
            return f"{base_amount:.0f}"

        if base_amount >= info['threshold']:
            converted = base_amount / info['factor']
            if converted == int(converted):
                return f"{int(converted)} {info['large']}"
            return f"{converted:.1f} {info['large']}"
        else:
            if base_amount == int(base_amount):
                return f"{int(base_amount)} {info['small']}"
            return f"{base_amount:.1f} {info['small']}"

    def _format_display(self, amount, unit):
        """Format amount + unit for display."""
        if amount == int(amount):
            amount_str = str(int(amount))
        else:
            amount_str = f"{amount:.1f}"

        if unit in ('piece', 'pcs'):
            return f"{amount_str} pcs" if float(amount) > 1 else amount_str
        return f"{amount_str} {unit}"


# ═══════════════════════════════════════════════════════════════
# 🔗 CONVENIENCE FUNCTION
# ═══════════════════════════════════════════════════════════════

def optimize_grocery_list(raw_data):
    """One-call convenience function to optimize a grocery list."""
    optimizer = GroceryOptimizer()
    return optimizer.optimize(raw_data)
