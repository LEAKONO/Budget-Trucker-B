from marshmallow import fields, ValidationError
from app import ma
from models import Income, Expense, User

class IncomeSchema(ma.SQLAlchemyAutoSchema):
    date = fields.Date(required=True, format='%Y-%m-%d')
    # user_id is not required from frontend

    class Meta:
        model = Income

class ExpenseSchema(ma.SQLAlchemyAutoSchema):
    date = fields.Date(required=True, format='%Y-%m-%d')
    # user_id is not required from frontend

    class Meta:
        model = Expense

class UserSchema(ma.SQLAlchemyAutoSchema):
    email = fields.Email(required=True)

    class Meta:
        model = User

def validate_user(data):
    try:
        UserSchema().load(data)
        return data, None
    except ValidationError as err:
        return None, err.messages

def validate_income(data):
    try:
        IncomeSchema().load(data)
        return data, None
    except ValidationError as err:
        return None, err.messages

def validate_expense(data):
    try:
        ExpenseSchema().load(data)
        return data, None
    except ValidationError as err:
        return None, err.messages
