from flask import Blueprint, request, jsonify
from app import db
from models import User, Income, Expense
from datetime import datetime, timedelta
from schemas import IncomeSchema, ExpenseSchema, validate_income, validate_expense
from flask_jwt_extended import jwt_required, get_jwt_identity

bp_routes = Blueprint('routes', __name__)

@bp_routes.route('/income', methods=['POST'])
@jwt_required()
def add_income():
    data = request.json
    if not isinstance(data, list):
        return jsonify({'message': 'Invalid input format, expected a list of records'}), 400

    errors = []
    user_id = get_jwt_identity()  # Get the user ID from the JWT token

    for record in data:
        validated_data, validation_errors = validate_income(record)
        if validation_errors:
            errors.append(validation_errors)
            continue

        # Convert date string to datetime object
        try:
            record['date'] = datetime.strptime(record['date'], '%Y-%m-%d')
        except ValueError:
            errors.append({'date': ['Not a valid date.']})
            continue

        # Create new Income record
        new_income = Income(
            amount=record['amount'],
            source=record['source'],
            date=record['date'],
            description=record['description'],
            user_id=user_id  # Use the user_id from JWT
        )
        db.session.add(new_income)

    if errors:
        db.session.rollback()
        return jsonify(errors), 400

    db.session.commit()
    return jsonify({'message': 'Income added successfully'}), 201

@bp_routes.route('/expense', methods=['POST'])
@jwt_required()
def add_expense():
    data = request.json
    user_id = get_jwt_identity()  # Get the user ID from the JWT token

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
                user_id=user_id  # Use the user_id from JWT
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
            user_id=user_id  # Use the user_id from JWT
        )
        db.session.add(new_expense)
        db.session.commit()

        return jsonify({"message": "Expense added successfully"}), 201

    else:
        return jsonify({"error": "Invalid data format"}), 400

@bp_routes.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()  # Get the user ID from the JWT token
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
    user_id = get_jwt_identity()  # Get the user ID from the JWT token
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
    user_id = get_jwt_identity()  # Get the user ID from the JWT token
    total_income = sum(i.amount for i in Income.query.filter_by(user_id=user_id).all())
    total_expenses = sum(e.amount for e in Expense.query.filter_by(user_id=user_id).all())
    balance = total_income - total_expenses

    return jsonify({'balance': balance}), 200

@bp_routes.route('/monthly_summary', methods=['GET'])
@jwt_required()
def get_monthly_summary():
    user_id = get_jwt_identity()  # Get the user ID from the JWT token
    
    # Get the year and month from query parameters
    year = request.args.get('year', default=datetime.utcnow().year, type=int)
    month = request.args.get('month', default=datetime.utcnow().month, type=int)

    # Validate month and year
    if month < 1 or month > 12:
        return jsonify({'message': 'Invalid month. Must be between 1 and 12.'}), 400
    if year < 1900 or year > datetime.utcnow().year:
        return jsonify({'message': 'Invalid year.'}), 400

    # Calculate start and end dates of the month
    start_of_month = datetime(year, month, 1)
    end_of_month = datetime(year, month + 1, 1) - timedelta(days=1)

    total_income = sum(i.amount for i in Income.query.filter_by(user_id=user_id).filter(Income.date >= start_of_month, Income.date <= end_of_month).all())
    total_expenses = sum(e.amount for e in Expense.query.filter_by(user_id=user_id).filter(Expense.date >= start_of_month, Expense.date <= end_of_month).all())

    summary = {
        'total_income': total_income,
        'total_expenses': total_expenses
    }

    return jsonify(summary), 200
