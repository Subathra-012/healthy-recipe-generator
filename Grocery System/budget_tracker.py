"""
Budget Tracking Module
======================
Manages weekly grocery budgets, compares against estimated costs,
and provides spending status/warnings.
"""


class BudgetTracker:
    """Tracks grocery budget and compares with estimated costs."""

    WARNING_THRESHOLD = 0.80
    OVER_THRESHOLD = 1.0

    def __init__(self, store=None):
        self.store = store if store is not None else {}

    def set_budget(self, amount, currency='INR'):
        self.store['grocery_budget'] = {
            'amount': float(amount),
            'currency': currency,
            'currency_symbol': '₹' if currency == 'INR' else '$'
        }
        return self.store['grocery_budget']

    def get_budget(self):
        return self.store.get('grocery_budget')

    def clear_budget(self):
        self.store.pop('grocery_budget', None)

    def check_budget(self, estimated_total):
        budget_data = self.get_budget()
        if not budget_data:
            return {
                'budget': 0, 'estimated': estimated_total,
                'remaining': 0, 'percentage_used': 0,
                'status': 'no_budget',
                'status_message': 'No budget set. Set a weekly budget to track spending.',
                'currency_symbol': '₹'
            }

        budget_amount = budget_data['amount']
        symbol = budget_data.get('currency_symbol', '₹')
        remaining = budget_amount - estimated_total
        pct = (estimated_total / budget_amount * 100) if budget_amount > 0 else 0

        if pct >= self.OVER_THRESHOLD * 100:
            status = 'over'
            msg = f'Over budget by {symbol}{abs(remaining):.0f}! Consider removing items.'
        elif pct >= self.WARNING_THRESHOLD * 100:
            status = 'warning'
            msg = f'Approaching budget limit. {symbol}{remaining:.0f} remaining.'
        else:
            status = 'under'
            msg = f'Within budget. {symbol}{remaining:.0f} remaining.'

        return {
            'budget': budget_amount,
            'estimated': round(estimated_total, 2),
            'remaining': round(remaining, 2),
            'percentage_used': round(pct, 1),
            'status': status,
            'status_message': msg,
            'currency_symbol': symbol
        }

    def get_savings_suggestions(self, optimized_list):
        suggestions = []
        all_items = []
        categories = optimized_list.get('categories', {})
        for cat_name, items in categories.items():
            for item in items:
                if item.get('estimated_cost', 0) > 0:
                    all_items.append({
                        'name': item['name'], 'cost': item['estimated_cost'],
                        'category': cat_name
                    })
        all_items.sort(key=lambda x: x['cost'], reverse=True)
        for item in all_items[:3]:
            suggestions.append({
                'item': item['name'], 'current_cost': item['cost'],
                'suggestion': f"Consider reducing {item['name']} or finding a cheaper alternative.",
                'potential_saving': round(item['cost'] * 0.3, 2)
            })
        return suggestions
