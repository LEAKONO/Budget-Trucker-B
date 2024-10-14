from flask import Blueprint, request, jsonify
from app import db
from models import User, Income, Expense, Budget, FinancialGoal
from datetime import datetime, timedelta
from schemas import IncomeSchema, ExpenseSchema, BudgetSchema, FinancialGoalSchema, validate_income, validate_expense
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

bp_routes = Blueprint('routes', __name__)
expense_schema = ExpenseSchema()
budget_schema = BudgetSchema()

@bp_routes.route('/income', methods=['POST'])
@jwt_required()
def add_income():
    data = request.json
    validated_data, errors = validate_income(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    user_id = get_jwt_identity() 
    new_income = Income(
        amount=validated_data['amount'],
        source=validated_data['source'],
        date=validated_data['date'],
        description=validated_data.get('description', ''),
        user_id=user_id
    )
    db.session.add(new_income)
    db.session.commit()
    return jsonify({'message': 'Income added successfully'}), 201



@bp_routes.route('/income/<int:id>', methods=['PUT'])
@jwt_required()
def update_income(id):
    data = request.json
    user_id = get_jwt_identity()
    income = Income.query.filter_by(id=id, user_id=user_id).first()

    if not income:
        return jsonify({'message': 'Income record not found'}), 404

    validated_data, validation_errors = validate_income(data)
    if validation_errors:
        return jsonify(validation_errors), 400

    income.amount = validated_data['amount']
    income.source = validated_data['source']

    if isinstance(validated_data['date'], str):
        income.date = datetime.strptime(validated_data['date'], '%Y-%m-%d').date()
    else:
        income.date = validated_data['date']

    income.description = validated_data.get('description', income.description)

    db.session.commit()
    return jsonify({'message': 'Income updated successfully'}), 200
@bp_routes.route('/income/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_income(id):
    user_id = get_jwt_identity()
    income = Income.query.filter_by(id=id, user_id=user_id).first()

    if not income:
        return jsonify({'message': 'Income record not found'}), 404

    db.session.delete(income)
    db.session.commit()
    return jsonify({'message': 'Income deleted successfully'}), 200

@bp_routes.route('/expense', methods=['POST'])
@jwt_required()
def add_expense():
    data = request.json
    user_id = get_jwt_identity()

    if isinstance(data, list):
        expenses = []
        for exp in data:
            try:
                expense_date = datetime.strptime(exp['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

            new_expense = Expense(
                amount=exp['amount'],
                category=exp['category'],
                date=expense_date,
                description=exp['description'],
                user_id=user_id
            )
            db.session.add(new_expense)
            expenses.append(new_expense)

        db.session.commit()
        return jsonify({"message": "Expenses added successfully"}), 201

    elif isinstance(data, dict):
        try:
            expense_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

        new_expense = Expense(
            amount=data['amount'],
            category=data['category'],
            date=expense_date,
            description=data['description'],
            user_id=user_id
        )
        db.session.add(new_expense)
        db.session.commit()

        return jsonify({"message": "Expense added successfully"}), 201

    else:
        return jsonify({"error": "Invalid data format"}), 400

@bp_routes.route('/expense/<int:id>', methods=['PUT'])
@jwt_required()
def update_expense(id):
    data = request.json
    user_id = get_jwt_identity()
    expense = Expense.query.filter_by(id=id, user_id=user_id).first()

    if not expense:
        return jsonify({'message': 'Expense record not found'}), 404

    try:
        validated_data = expense_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    expense.amount = validated_data['amount']
    expense.category = validated_data['category']
    expense.date = validated_data['date']  # No need for strptime, it's already a date object
    expense.description = validated_data.get('description', expense.description)

    db.session.commit()
    return jsonify({'message': 'Expense updated successfully'}), 200

@bp_routes.route('/expense/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_expense(id):
    user_id = get_jwt_identity()
    expense = Expense.query.filter_by(id=id, user_id=user_id).first()

    if not expense:
        return jsonify({'message': 'Expense record not found'}), 404

    db.session.delete(expense)
    db.session.commit()
    return jsonify({'message': 'Expense deleted successfully'}), 200

@bp_routes.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')

    incomes = Income.query.filter_by(user_id=user_id)
    expenses = Expense.query.filter_by(user_id=user_id)
    
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            incomes = incomes.filter(Income.date >= start_date, Income.date <= end_date)
            expenses = expenses.filter(Expense.date >= start_date, Expense.date <= end_date)
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

    if category:
        expenses = expenses.filter(Expense.category == category)

    income_schema = IncomeSchema(many=True)
    expense_schema = ExpenseSchema(many=True)
    
    transactions = {
        'incomes': income_schema.dump(incomes.all()),
        'expenses': expense_schema.dump(expenses.all())
    }

    return jsonify(transactions), 200

@bp_routes.route('/recent_transactions', methods=['GET'])
@jwt_required()
def get_recent_transactions():
    user_id = get_jwt_identity()
    recent_incomes = Income.query.filter_by(user_id=user_id).order_by(Income.date.desc()).limit(5).all()
    recent_expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc()).limit(5).all()

    income_schema = IncomeSchema(many=True)
    expense_schema = ExpenseSchema(many=True)

    transactions = {
        'recent_incomes': income_schema.dump(recent_incomes),
        'recent_expenses': expense_schema.dump(recent_expenses)
    }

    return jsonify(transactions), 200

@bp_routes.route('/balance', methods=['GET'])
@jwt_required()
def get_balance():
    user_id = get_jwt_identity()
    total_income = sum(i.amount for i in Income.query.filter_by(user_id=user_id).all())
    total_expenses = sum(e.amount for e in Expense.query.filter_by(user_id=user_id).all())
    balance = total_income - total_expenses

    return jsonify({'balance': balance}), 200

@bp_routes.route('/monthly_summary', methods=['GET'])
@jwt_required()
def get_monthly_summary():
    user_id = get_jwt_identity()
    
    year = request.args.get('year', default=datetime.utcnow().year, type=int)
    month = request.args.get('month', default=datetime.utcnow().month, type=int)

    if month < 1 or month > 12:
        return jsonify({'message': 'Invalid month. Must be between 1 and 12.'}), 400
    if year < 1900 or year > datetime.utcnow().year:
        return jsonify({'message': 'Invalid year.'}), 400

    start_of_month = datetime(year, month, 1)
    end_of_month = datetime(year, month + 1, 1) - timedelta(days=1)

    total_income = sum(i.amount for i in Income.query.filter_by(user_id=user_id).filter(Income.date >= start_of_month, Income.date <= end_of_month).all())
    total_expenses = sum(e.amount for e in Expense.query.filter_by(user_id=user_id).filter(Expense.date >= start_of_month, Expense.date <= end_of_month).all())

    summary = {
        'total_income': total_income,
        'total_expenses': total_expenses
    }

    return jsonify(summary), 200

@bp_routes.route('/budget', methods=['POST'])
@jwt_required()
def add_budget():
    data = request.json
    user_id = get_jwt_identity()

    try:
        validated_data = BudgetSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_budget = Budget(
        category=validated_data['category'],
        limit=validated_data['limit'],
        year=validated_data['year'],
        month=validated_data['month'],
        user_id=user_id
    )
    db.session.add(new_budget)
    db.session.commit()

    return jsonify({'message': 'Budget added successfully'}), 201


@bp_routes.route('/budget/<int:id>', methods=['PUT'])
@jwt_required()
def update_budget(id):
    data = request.json
    user_id = get_jwt_identity()
    budget = Budget.query.filter_by(id=id, user_id=user_id).first()

    if not budget:
        return jsonify({'message': 'Budget record not found'}), 404

    try:
        validated_data = budget_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Update the budget fields with validated data
    budget.category = validated_data.get('category', budget.category)
    budget.limit = validated_data.get('limit', budget.limit)
    budget.year = validated_data.get('year', budget.year)
    budget.month = validated_data.get('month', budget.month)

    db.session.commit()
    return jsonify({'message': 'Budget updated successfully'}), 200

@bp_routes.route('/budget/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_budget(id):
    user_id = get_jwt_identity()
    budget = Budget.query.filter_by(id=id, user_id=user_id).first()

    if not budget:
        return jsonify({'message': 'Budget record not found'}), 404

    db.session.delete(budget)
    db.session.commit()
    return jsonify({'message': 'Budget deleted successfully'}), 200
@bp_routes.route('/budget/<int:id>', methods=['GET'])
@jwt_required()
def get_budget(id):
    user_id = get_jwt_identity()
    budget = Budget.query.filter_by(id=id, user_id=user_id).first()

    if not budget:
        return jsonify({'message': 'Budget record not found'}), 404

    budget_data = {
        'id': budget.id,
        'category': budget.category,
        'limit': budget.limit,
        'year': budget.year,
        'month': budget.month
    }

    return jsonify(budget_data), 200


@bp_routes.route('/budget', methods=['GET'])
@jwt_required()
def get_all_budgets():
    user_id = get_jwt_identity()
    budgets = Budget.query.filter_by(user_id=user_id).all()

    if not budgets:
        return jsonify([]), 200  

    budget_data = [
        {
            'id': budget.id,
            'category': budget.category,
            'limit': budget.limit,
            'year': budget.year,
            'month': budget.month
        } for budget in budgets
    ]
    return jsonify(budget_data), 200

@bp_routes.route('/financial_goals', methods=['POST'])
@jwt_required()
def add_financial_goal():
    data = request.json
    user_id = get_jwt_identity()

    try:
        validated_data = FinancialGoalSchema().load(data)  # Correct way to call load
    except ValidationError as err:
        return jsonify(err.messages), 400  # Return validation errors

    new_goal = FinancialGoal(
        goal_name=validated_data['goal_name'],
        target_amount=validated_data['target_amount'],
        current_amount=validated_data.get('current_amount', 0),
        target_date=validated_data['target_date'],
        user_id=user_id
    )
    db.session.add(new_goal)
    db.session.commit()

    return jsonify({'message': 'Financial goal added successfully'}), 201

@bp_routes.route('/financial_goals/<int:id>', methods=['PUT'])
@jwt_required()
def update_financial_goal(id):
    data = request.json
    user_id = get_jwt_identity()
    goal = FinancialGoal.query.filter_by(id=id, user_id=user_id).first()

    if not goal:
        return jsonify({'message': 'Financial goal not found'}), 404

    validated_data, validation_errors = FinancialGoalSchema().load(data)
    if validation_errors:
        return jsonify(validation_errors), 400

    goal.goal_name = validated_data['goal_name']
    goal.target_amount = validated_data['target_amount']
    goal.current_amount = validated_data.get('current_amount', goal.current_amount)
    goal.target_date = datetime.strptime(validated_data['target_date'], '%Y-%m-%d').date()

    db.session.commit()
    return jsonify({'message': 'Financial goal updated successfully'}), 200

@bp_routes.route('/financial_goals/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_financial_goal(id):
    user_id = get_jwt_identity()
    goal = FinancialGoal.query.filter_by(id=id, user_id=user_id).first()

    if not goal:
        return jsonify({'message': 'Financial goal not found'}), 404

    db.session.delete(goal)
    db.session.commit()
    return jsonify({'message': 'Financial goal deleted successfully'}), 200

@bp_routes.route('/financial_goals', methods=['GET'])
@jwt_required()
def get_financial_goals():
    user_id = get_jwt_identity()
    goals = FinancialGoal.query.filter_by(user_id=user_id).all()
    goal_schema = FinancialGoalSchema(many=True)
    return jsonify(goal_schema.dump(goals)), 200
