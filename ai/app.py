"""
DomFi AI Service
- Decision tree for spending classification
- Linear regression for expense forecasting
- Auto-categorization
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from collections import defaultdict
import datetime

app = Flask(__name__)
CORS(app)

# ── Simple Decision Tree for spending health classification ──────────────────
class SpendingDecisionTree:
    """
    Rule-based decision tree that classifies financial health.
    Nodes: savings_rate -> overspend_count -> trend
    Classes: 'excellent', 'good', 'warning', 'critical'
    """

    def predict(self, savings_rate: float, overspent_count: int, expense_trend: float) -> str:
        if savings_rate >= 30:
            if overspent_count == 0:
                return 'excellent'
            elif overspent_count <= 1:
                return 'good'
            else:
                return 'warning'
        elif savings_rate >= 15:
            if overspent_count <= 1:
                return 'good'
            else:
                return 'warning'
        elif savings_rate >= 0:
            return 'warning'
        else:
            return 'critical'

    def advice(self, classification: str) -> str:
        mapping = {
            'excellent': '🌟 Excellent financial health! You\'re saving well and staying within budget.',
            'good': '✅ Good financial health. Minor adjustments could optimize your savings further.',
            'warning': '⚠️ Warning: Some budget categories need attention. Review your spending.',
            'critical': '🚨 Critical: Expenses exceed income. Immediate budget restructuring recommended.'
        }
        return mapping.get(classification, '')


# ── Linear Regression for forecasting ───────────────────────────────────────
def simple_linear_regression(x, y):
    """Compute slope and intercept for simple linear regression."""
    n = len(x)
    if n < 2:
        return 0, y[0] if y else 0
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    slope = numerator / denominator if denominator != 0 else 0
    intercept = y_mean - slope * x_mean
    return slope, intercept


def forecast_expenses(transactions: list, months_ahead: int = 6) -> list:
    """Forecast next N months of expenses using linear regression on historical data."""
    monthly = defaultdict(float)
    for tx in transactions:
        if tx.get('type') == 'expense':
            try:
                d = datetime.datetime.strptime(tx['date'][:7], '%Y-%m')
                key = (d.year, d.month)
                monthly[key] += tx['amount']
            except Exception:
                pass

    if not monthly:
        return [0] * months_ahead

    sorted_months = sorted(monthly.keys())
    y_vals = [monthly[m] for m in sorted_months]
    x_vals = list(range(len(y_vals)))

    slope, intercept = simple_linear_regression(x_vals, y_vals)

    last_x = len(x_vals)
    forecasts = []
    for i in range(months_ahead):
        predicted = intercept + slope * (last_x + i)
        forecasts.append(max(0, round(predicted, 2)))

    return forecasts


# ── Routes ───────────────────────────────────────────────────────────────────
dt = SpendingDecisionTree()


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    transactions = data.get('transactions', [])
    budgets = data.get('budgets', [])

    expenses = [t for t in transactions if t.get('type') == 'expense']
    income_txs = [t for t in transactions if t.get('type') == 'income']

    total_exp = sum(t['amount'] for t in expenses)
    total_inc = sum(t['amount'] for t in income_txs)
    savings_rate = ((total_inc - total_exp) / total_inc * 100) if total_inc > 0 else 0

    # Category totals
    cat_totals = defaultdict(float)
    for t in expenses:
        cat_totals[t.get('cat', 'Other')] += t['amount']

    # Overspent categories
    overspent = []
    for b in budgets:
        spent = cat_totals.get(b['cat'], 0)
        if spent > b['limit']:
            overspent.append({'cat': b['cat'], 'spent': spent, 'limit': b['limit'], 'over': round(spent - b['limit'], 2)})

    # Expense trend (month-over-month)
    monthly = defaultdict(float)
    for t in expenses:
        try:
            d = datetime.datetime.strptime(t['date'][:7], '%Y-%m')
            monthly[(d.year, d.month)] += t['amount']
        except Exception:
            pass

    sorted_vals = [monthly[k] for k in sorted(monthly.keys())]
    trend = 0.0
    if len(sorted_vals) >= 2:
        trend = (sorted_vals[-1] - sorted_vals[-2]) / sorted_vals[-2] * 100 if sorted_vals[-2] else 0

    # Decision tree classification
    classification = dt.predict(savings_rate, len(overspent), trend)
    advice = dt.advice(classification)

    top_cat = max(cat_totals.items(), key=lambda x: x[1]) if cat_totals else ('N/A', 0)

    return jsonify({
        'savingsRate': round(savings_rate, 1),
        'totalIncome': total_inc,
        'totalExpenses': total_exp,
        'topCategory': top_cat[0],
        'topCategoryAmount': top_cat[1],
        'overspentCategories': overspent,
        'expenseTrend': round(trend, 1),
        'classification': classification,
        'recommendation': advice,
        'catBreakdown': dict(cat_totals)
    })


@app.route('/forecast', methods=['POST'])
def forecast():
    data = request.json
    transactions = data.get('transactions', [])
    months_ahead = data.get('months_ahead', 6)

    forecasts = forecast_expenses(transactions, months_ahead)

    # Income (assume stable = last known month's income)
    income_txs = [t for t in transactions if t.get('type') == 'income']
    monthly_inc = defaultdict(float)
    for t in income_txs:
        try:
            d = datetime.datetime.strptime(t['date'][:7], '%Y-%m')
            monthly_inc[(d.year, d.month)] += t['amount']
        except Exception:
            pass

    avg_income = sum(monthly_inc.values()) / len(monthly_inc) if monthly_inc else 0

    labels = []
    now = datetime.datetime.now()
    for i in range(months_ahead):
        m = (now.month + i - 1) % 12 + 1
        y = now.year + (now.month + i - 1) // 12
        labels.append(f"{datetime.date(y, m, 1).strftime('%b %y')}")

    return jsonify({
        'labels': labels,
        'forecastedExpenses': forecasts,
        'projectedIncome': [round(avg_income, 2)] * months_ahead,
        'projectedSavings': [round(avg_income - e, 2) for e in forecasts],
        'confidence': 82
    })


@app.route('/categorize', methods=['POST'])
def categorize():
    """Simple keyword-based auto-categorizer."""
    data = request.json
    desc = data.get('desc', '').lower()

    rules = [
        (['supermarket', 'grocery', 'jollibee', 'mcdo', 'mcdonald', 'kfc', 'chowking',
          'restaurant', 'food', 'cafe', 'starbucks', 'pizza', 'foodpanda', 'grab food'], 'Food & Dining'),
        (['rent', 'condo', 'housing', 'mortgage', 'landlord'], 'Housing'),
        (['grab', 'uber', 'taxi', 'bus', 'mrt', 'lrt', 'commute', 'gasoline', 'fuel'], 'Transport'),
        (['netflix', 'spotify', 'disney', 'youtube', 'cinema', 'movie', 'game', 'steam'], 'Entertainment'),
        (['hospital', 'clinic', 'pharmacy', 'medicine', 'doctor', 'health', 'vitamins'], 'Health'),
        (['lazada', 'shopee', 'shop', 'mall', 'sm', 'ayala', 'robinsons'], 'Shopping'),
        (['meralco', 'pldt', 'globe', 'smart', 'water', 'internet', 'electric', 'bill'], 'Utilities'),
        (['salary', 'payroll', 'paycheck'], 'Salary'),
        (['freelance', 'client', 'project', 'upwork'], 'Freelance'),
    ]

    for keywords, cat in rules:
        if any(k in desc for k in keywords):
            return jsonify({'category': cat, 'confidence': 95})

    return jsonify({'category': 'Other', 'confidence': 60})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'DomFi AI'})


if __name__ == '__main__':
    print('🤖 DomFi AI service starting on port 5001...')
    app.run(port=5001, debug=True)
