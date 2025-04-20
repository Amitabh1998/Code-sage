transactions=[]
def record_transaction(amount, category, is_expense):
    """Record a financial transaction with amount, category, and type."""
    if not isinstance(amount, (int, float)) or amount <= 0:
        return False, "Amount must be a positive number"
    transaction = {
        "id": len(transactions) + 1,
        "amount": amount,
        "category": category.lower(),
        "is_expense": is_expense
    }
    transactions.append(transaction)
    return True, f"Transaction {transaction['id']} recorded"

def calculate_balance():
    """Calculate the net balance from all transactions."""
    balance = 0
    for t in transactions:
        balance += t["amount"] if not t["is_expense"] else -t["amount"]
    return balance

def summarize_by_category():
    """Summarize total amounts by category."""
    summary = {}
    for t in transactions:
        category = t["category"]
        amount = t["amount"] if not t["is_expense"] else -t["amount"]
        summary[category] = summary.get(category, 0) + amount
    return summary