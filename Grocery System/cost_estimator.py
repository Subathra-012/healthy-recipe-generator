"""
Cost Estimation Module
======================
Estimates grocery costs based on a built-in price database.
Extensible with user-defined prices and multiple currencies.
"""


# ═══════════════════════════════════════════════════════════════
# 💰 PRICE DATABASE (per base unit: g for mass, ml for volume, piece for count)
# ═══════════════════════════════════════════════════════════════

# Prices in INR (₹) per standard unit
# Mass items: price per kg (will be converted from g)
# Volume items: price per liter (will be converted from ml)
# Count items: price per piece
PRICE_DB = {
    # Produce (per kg)
    'onion':        {'price': 40,  'per': 'kg', 'currency': 'INR'},
    'tomato':       {'price': 50,  'per': 'kg', 'currency': 'INR'},
    'potato':       {'price': 35,  'per': 'kg', 'currency': 'INR'},
    'carrot':       {'price': 60,  'per': 'kg', 'currency': 'INR'},
    'cucumber':     {'price': 40,  'per': 'kg', 'currency': 'INR'},
    'spinach':      {'price': 30,  'per': 'bunch', 'currency': 'INR'},
    'bell pepper':  {'price': 120, 'per': 'kg', 'currency': 'INR'},
    'broccoli':     {'price': 100, 'per': 'kg', 'currency': 'INR'},
    'cauliflower':  {'price': 50,  'per': 'kg', 'currency': 'INR'},
    'mushroom':     {'price': 150, 'per': 'kg', 'currency': 'INR'},
    'garlic':       {'price': 200, 'per': 'kg', 'currency': 'INR'},
    'ginger':       {'price': 180, 'per': 'kg', 'currency': 'INR'},
    'cabbage':      {'price': 30,  'per': 'kg', 'currency': 'INR'},
    'sweet potato': {'price': 60,  'per': 'kg', 'currency': 'INR'},
    'spring onion': {'price': 20,  'per': 'bunch', 'currency': 'INR'},
    'lettuce':      {'price': 50,  'per': 'piece', 'currency': 'INR'},
    'avocado':      {'price': 150, 'per': 'piece', 'currency': 'INR'},
    'kale':         {'price': 80,  'per': 'bunch', 'currency': 'INR'},
    'celery':       {'price': 60,  'per': 'bunch', 'currency': 'INR'},
    'peas':         {'price': 80,  'per': 'kg', 'currency': 'INR'},
    'corn':         {'price': 50,  'per': 'piece', 'currency': 'INR'},

    # Fruits (per kg or piece)
    'lemon':       {'price': 10,  'per': 'piece', 'currency': 'INR'},
    'banana':      {'price': 6,   'per': 'piece', 'currency': 'INR'},
    'apple':       {'price': 150, 'per': 'kg', 'currency': 'INR'},
    'orange':      {'price': 80,  'per': 'kg', 'currency': 'INR'},
    'mango':       {'price': 120, 'per': 'kg', 'currency': 'INR'},
    'strawberry':  {'price': 200, 'per': 'kg', 'currency': 'INR'},
    'blueberry':   {'price': 500, 'per': 'kg', 'currency': 'INR'},

    # Protein (per kg or piece)
    'chicken breast': {'price': 350, 'per': 'kg', 'currency': 'INR'},
    'chicken thigh':  {'price': 300, 'per': 'kg', 'currency': 'INR'},
    'chicken':        {'price': 280, 'per': 'kg', 'currency': 'INR'},
    'salmon':         {'price': 1200,'per': 'kg', 'currency': 'INR'},
    'tuna':           {'price': 600, 'per': 'kg', 'currency': 'INR'},
    'shrimp':         {'price': 500, 'per': 'kg', 'currency': 'INR'},
    'prawns':         {'price': 500, 'per': 'kg', 'currency': 'INR'},
    'egg':            {'price': 7,   'per': 'piece', 'currency': 'INR'},
    'tofu':           {'price': 120, 'per': 'kg', 'currency': 'INR'},
    'paneer':         {'price': 380, 'per': 'kg', 'currency': 'INR'},
    'lentils':        {'price': 120, 'per': 'kg', 'currency': 'INR'},
    'chickpeas':      {'price': 130, 'per': 'kg', 'currency': 'INR'},
    'kidney beans':   {'price': 140, 'per': 'kg', 'currency': 'INR'},
    'black beans':    {'price': 150, 'per': 'kg', 'currency': 'INR'},
    'fish':           {'price': 400, 'per': 'kg', 'currency': 'INR'},
    'beef':           {'price': 500, 'per': 'kg', 'currency': 'INR'},
    'lamb':           {'price': 700, 'per': 'kg', 'currency': 'INR'},
    'mutton':         {'price': 750, 'per': 'kg', 'currency': 'INR'},
    'turkey':         {'price': 450, 'per': 'kg', 'currency': 'INR'},

    # Dairy (per liter or kg)
    'milk':            {'price': 60,  'per': 'liter', 'currency': 'INR'},
    'yogurt':          {'price': 80,  'per': 'kg', 'currency': 'INR'},
    'butter':          {'price': 500, 'per': 'kg', 'currency': 'INR'},
    'cheese':          {'price': 600, 'per': 'kg', 'currency': 'INR'},
    'cheddar cheese':  {'price': 700, 'per': 'kg', 'currency': 'INR'},
    'mozzarella cheese': {'price': 650, 'per': 'kg', 'currency': 'INR'},
    'parmesan cheese': {'price': 1200, 'per': 'kg', 'currency': 'INR'},
    'cottage cheese':  {'price': 350, 'per': 'kg', 'currency': 'INR'},
    'cream':           {'price': 250, 'per': 'liter', 'currency': 'INR'},

    # Grains & Staples (per kg)
    'rice':          {'price': 60,  'per': 'kg', 'currency': 'INR'},
    'basmati rice':  {'price': 120, 'per': 'kg', 'currency': 'INR'},
    'brown rice':    {'price': 140, 'per': 'kg', 'currency': 'INR'},
    'oats':          {'price': 180, 'per': 'kg', 'currency': 'INR'},
    'quinoa':        {'price': 600, 'per': 'kg', 'currency': 'INR'},
    'pasta':         {'price': 150, 'per': 'kg', 'currency': 'INR'},
    'bread':         {'price': 45,  'per': 'piece', 'currency': 'INR'},
    'flour':         {'price': 45,  'per': 'kg', 'currency': 'INR'},
    'wheat flour':   {'price': 50,  'per': 'kg', 'currency': 'INR'},
    'noodles':       {'price': 30,  'per': 'piece', 'currency': 'INR'},
    'tortilla':      {'price': 80,  'per': 'piece', 'currency': 'INR'},

    # Oils & Condiments (per liter)
    'olive oil':      {'price': 700,  'per': 'liter', 'currency': 'INR'},
    'vegetable oil':  {'price': 150,  'per': 'liter', 'currency': 'INR'},
    'coconut oil':    {'price': 300,  'per': 'liter', 'currency': 'INR'},
    'sesame oil':     {'price': 400,  'per': 'liter', 'currency': 'INR'},
    'soy sauce':      {'price': 120,  'per': 'liter', 'currency': 'INR'},
    'vinegar':        {'price': 80,   'per': 'liter', 'currency': 'INR'},
    'honey':          {'price': 400,  'per': 'kg', 'currency': 'INR'},

    # Spices (per kg — used in small amounts)
    'salt':           {'price': 20,  'per': 'kg', 'currency': 'INR'},
    'pepper':         {'price': 600, 'per': 'kg', 'currency': 'INR'},
    'black pepper':   {'price': 600, 'per': 'kg', 'currency': 'INR'},
    'cumin':          {'price': 300, 'per': 'kg', 'currency': 'INR'},
    'turmeric':       {'price': 200, 'per': 'kg', 'currency': 'INR'},
    'paprika':        {'price': 400, 'per': 'kg', 'currency': 'INR'},
    'coriander':      {'price': 250, 'per': 'kg', 'currency': 'INR'},
    'cinnamon':       {'price': 500, 'per': 'kg', 'currency': 'INR'},
    'garam masala':   {'price': 400, 'per': 'kg', 'currency': 'INR'},

    # Nuts & Seeds (per kg)
    'almond':         {'price': 800, 'per': 'kg', 'currency': 'INR'},
    'walnut':         {'price': 1200, 'per': 'kg', 'currency': 'INR'},
    'cashew':         {'price': 900,  'per': 'kg', 'currency': 'INR'},
    'peanut':         {'price': 150,  'per': 'kg', 'currency': 'INR'},
    'chia seeds':     {'price': 500,  'per': 'kg', 'currency': 'INR'},
    'flax seeds':     {'price': 300,  'per': 'kg', 'currency': 'INR'},
}

# Conversion factors to normalize price units to base units
PRICE_UNIT_TO_BASE = {
    'kg':    1000,    # 1 kg = 1000 g
    'liter': 1000,    # 1 L = 1000 ml
    'piece': 1,
    'bunch': 1,
}


# ═══════════════════════════════════════════════════════════════
# 💵 COST ESTIMATOR
# ═══════════════════════════════════════════════════════════════

class CostEstimator:
    """Estimates cost for an optimized grocery list."""

    def __init__(self, price_db=None):
        self.prices = price_db or PRICE_DB

    def estimate(self, optimized_list):
        """
        Add cost estimates to each item in an optimized grocery list.

        Args:
            optimized_list: Output of GroceryOptimizer.optimize()

        Returns:
            dict: Enhanced list with cost info + summary
        """
        grand_total = 0.0
        category_totals = {}
        currency = 'INR'

        categories = optimized_list.get('categories', {})

        for cat_name, items in categories.items():
            cat_total = 0.0

            for item in items:
                cost = self._estimate_item(item)
                item['estimated_cost'] = round(cost, 2)
                item['currency'] = currency
                cat_total += cost

            category_totals[cat_name] = round(cat_total, 2)
            grand_total += cat_total

        optimized_list['cost_summary'] = {
            'total': round(grand_total, 2),
            'currency': currency,
            'currency_symbol': '₹',
            'by_category': category_totals
        }

        return optimized_list

    def _estimate_item(self, item):
        """Estimate cost for a single item."""
        name = item['name'].lower()
        quantity = item.get('quantity', 1)
        unit = item.get('unit', 'piece').lower()

        price_info = self.prices.get(name)
        if not price_info:
            # Try partial match
            for key, val in self.prices.items():
                if key in name or name in key:
                    price_info = val
                    break

        if not price_info:
            # Unknown item — estimate ₹50 per piece/unit
            return 50.0

        price_per = price_info['price']
        price_unit = price_info['per']

        # Convert item quantity to the price unit's base
        from grocery_optimizer import UNIT_FAMILIES

        # Get item quantity in base units (g or ml)
        if unit in UNIT_FAMILIES:
            base_qty = quantity * UNIT_FAMILIES[unit]['to_base']
        else:
            base_qty = quantity

        # Get how many base units are in the price unit
        price_base = PRICE_UNIT_TO_BASE.get(price_unit, 1)

        # Cost = (base_qty / price_base) * price_per
        if price_base > 0:
            cost = (base_qty / price_base) * price_per
        else:
            cost = price_per

        return max(cost, 0)


# ═══════════════════════════════════════════════════════════════
# 🔗 CONVENIENCE
# ═══════════════════════════════════════════════════════════════

def estimate_grocery_cost(optimized_list):
    """One-call convenience function."""
    estimator = CostEstimator()
    return estimator.estimate(optimized_list)
