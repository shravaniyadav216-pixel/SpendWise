def generate_spending_insights(category_summary: list, total_amount: float) -> list:
    insights = []

    if total_amount == 0:
        return ["No expenses added yet. Start tracking your spending to get insights."]

    if category_summary:
        highest_category = max(category_summary, key=lambda x: x["total_amount"])
        insights.append(
            f"Your highest spending is in '{highest_category['category']}' with amount ₹{highest_category['total_amount']:.2f}."
        )

    if total_amount > 10000:
        insights.append("Your overall spending is high. Consider setting a monthly budget.")
    else:
        insights.append("Your spending looks moderate. Keep tracking regularly.")

    if len(category_summary) >= 3:
        insights.append("You are spending across multiple categories. Review which category can be reduced.")

    return insights