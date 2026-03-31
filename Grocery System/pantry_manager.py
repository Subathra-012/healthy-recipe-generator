"""
Pantry Manager Module
=====================
Manages user pantry inventory and deducts from grocery lists.
Uses Flask session for per-user in-memory storage.
"""


class PantryManager:
    """Manages pantry inventory and deducts from grocery lists."""

    def __init__(self, store=None):
        self.store = store if store is not None else {}

    def _get_pantry(self):
        if 'pantry_items' not in self.store:
            self.store['pantry_items'] = []
        return self.store['pantry_items']

    def add_item(self, name, quantity=1.0, unit='piece'):
        pantry = self._get_pantry()
        # Check if item already exists
        for item in pantry:
            if item['name'].lower() == name.lower():
                item['quantity'] += float(quantity)
                return {'status': 'updated', 'item': item}
        new_item = {
            'name': name.strip().title(),
            'quantity': float(quantity),
            'unit': unit.lower().strip()
        }
        pantry.append(new_item)
        return {'status': 'added', 'item': new_item}

    def remove_item(self, name):
        pantry = self._get_pantry()
        self.store['pantry_items'] = [
            i for i in pantry if i['name'].lower() != name.lower()
        ]
        return {'status': 'removed', 'name': name}

    def update_item(self, name, quantity=None, unit=None):
        pantry = self._get_pantry()
        for item in pantry:
            if item['name'].lower() == name.lower():
                if quantity is not None:
                    item['quantity'] = float(quantity)
                if unit is not None:
                    item['unit'] = unit
                return {'status': 'updated', 'item': item}
        return {'status': 'not_found', 'name': name}

    def get_inventory(self):
        return self._get_pantry()

    def clear_inventory(self):
        self.store['pantry_items'] = []
        return {'status': 'cleared'}

    def deduct_from_list(self, optimized_list):
        """
        Subtract pantry items from an optimized grocery list.
        Returns a new list with adjusted quantities and a deduction log.
        """
        from grocery_optimizer import UNIT_FAMILIES, IngredientNormalizer

        pantry = self._get_pantry()
        if not pantry:
            return {
                'adjusted_list': optimized_list,
                'deductions': [],
                'pantry_used': False
            }

        normalizer = IngredientNormalizer()
        # Build pantry lookup: canonical_name -> {amount in base units}
        pantry_lookup = {}
        for p_item in pantry:
            canonical = normalizer.normalize(p_item['name'])
            unit = p_item['unit'].lower()
            qty = p_item['quantity']
            if unit in UNIT_FAMILIES:
                base_qty = qty * UNIT_FAMILIES[unit]['to_base']
            else:
                base_qty = qty
            if canonical in pantry_lookup:
                pantry_lookup[canonical] += base_qty
            else:
                pantry_lookup[canonical] = base_qty

        deductions = []
        categories = optimized_list.get('categories', {})

        for cat_name, items in categories.items():
            adjusted_items = []
            for item in items:
                canon = item['name']
                if canon in pantry_lookup and pantry_lookup[canon] > 0:
                    # Get item quantity in base units
                    item_unit = item.get('unit', 'piece').lower()
                    if item_unit in UNIT_FAMILIES:
                        item_base = item['quantity'] * UNIT_FAMILIES[item_unit]['to_base']
                    else:
                        item_base = item['quantity']

                    available = pantry_lookup[canon]
                    if available >= item_base:
                        # Fully covered by pantry
                        deductions.append({
                            'item': canon,
                            'needed': item['display_qty'],
                            'from_pantry': item['display_qty'],
                            'status': 'fully_covered'
                        })
                        pantry_lookup[canon] -= item_base
                        continue  # Don't add to adjusted list
                    else:
                        # Partially covered
                        remaining_base = item_base - available
                        pantry_lookup[canon] = 0
                        item_copy = dict(item)
                        # Recalculate display
                        if item_unit in UNIT_FAMILIES:
                            item_copy['quantity'] = remaining_base / UNIT_FAMILIES[item_unit]['to_base']
                        else:
                            item_copy['quantity'] = remaining_base
                        item_copy['display_qty'] = f"{item_copy['quantity']:.1f} {item_unit}"
                        item_copy['pantry_deducted'] = True
                        deductions.append({
                            'item': canon,
                            'needed': item['display_qty'],
                            'from_pantry': f"partial ({available:.0f} base units)",
                            'status': 'partially_covered'
                        })
                        adjusted_items.append(item_copy)
                else:
                    adjusted_items.append(item)

            categories[cat_name] = adjusted_items

        # Remove empty categories
        optimized_list['categories'] = {
            k: v for k, v in categories.items() if v
        }

        return {
            'adjusted_list': optimized_list,
            'deductions': deductions,
            'pantry_used': True
        }
