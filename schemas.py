from marshmallow import Schema, fields, validate, ValidationError

class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

def validate_user(data):
    schema = UserSchema()
    try:
        validated_data = schema.load(data)
        return validated_data, None
    except ValidationError as err:
        return None, err.messages
class IncomeSchema(Schema):
    amount = fields.Float(required=True)
    source = fields.Str(required=True)
    date = fields.Date(required=True)
    description = fields.Str()
def validate_income(data):
    schema = IncomeSchema()
    try:
        validated_data = schema.load(data)
        return validated_data, None
    except ValidationError as err:
        return None, err.messages
class ExpenseSchema(Schema):
    amount = fields.Float(required=True, validate=validate.Range(min=0))
    category = fields.Str(required=True, validate=validate.Length(min=1))
    date = fields.Date(required=True)  
    description = fields.Str()  

def validate_expense(data):
    schema = ExpenseSchema()
    try:
        validated_data = schema.load(data)
        return validated_data, None
    except ValidationError as err:
        return None, err.messages
class BudgetSchema(Schema):
    category = fields.String(required=True)
    limit = fields.Float(required=True)
    year = fields.Integer(required=True)
    month = fields.Integer(required=True)

def validate_budget(data):
    schema = BudgetSchema()
    try:
        validated_data = schema.load(data)
        return validated_data, None
    except ValidationError as err:
        return None, err.messages
class FinancialGoalSchema(Schema):
    goal_name = fields.String(required=True)
    target_amount = fields.Float(required=True)
    current_amount = fields.Float(missing=0)  
    target_date = fields.Date(required=True, format='%Y-%m-%d')
def validate_financial_goal(data):
    schema = FinancialGoalSchema()
    try:
        validated_data = schema.load(data)
        return validated_data, None
    except ValidationError as err:
        return None, err.messages
