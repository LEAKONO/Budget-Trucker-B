# Personal Finance Management API

This project provides a Flask API for managing personal finances, including tracking income, expenses, budgets, and financial goals. The API allows users to add, update, and delete transactions, view summaries, and monitor their financial health over time. Authentication is managed through JWT tokens, and all routes are secured to ensure that users can only manage their own data.

## Features

- **Income Management**: Add, update, delete, and retrieve income records.
- **Expense Management**: Add, update, delete, and retrieve expense records.
- **Budget Management**: Create, update, delete, and retrieve monthly budgets for different categories.
- **Financial Goal Management**: Set and track progress toward financial goals.
- **Monthly and Recent Summaries**: View detailed summaries of transactions and financial balances.
- **User Authentication**: Secure user data with JWT-based authentication.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/LEAKONO/Budget-Trucker-B
    cd trucker
    ```

2. Install the required packages:

    ```bash
    pipenv install
    ```

3. Set up environment variables and create the database.

4. Run the application:

    ```bash
    flask run
    ```
### Blueprints

- **Authentication Routes:** `auth/api`
- **Other Routes:** `routes/api`

## Routes

### Income

- **POST /income**  
  Add a new income entry.

  ```json
  {
    "amount": 1000,
    "source": "Salary",
    "date": "2023-10-01",
    "description": "October Salary"
  }
### Expense

- **POST /expense**  
  Add a new expense entry.

  ```json
  {
    "amount": 200,
    "category": "Groceries",
    "date": "2023-10-05",
    "description": "Supermarket shopping"
  }
### Transactions

- **GET /transactions**  
  Retrieve all transactions (income and expenses) for the authenticated user.

- **GET /recent-transactions**  
  Retrieve the most recent 5 income and expense transactions.

### Financial Summaries

- **GET /balance**  
  Get the user's current financial balance (total income minus total expenses).

- **GET /monthly_summary**  
  Get a summary of income and expenses for a specific month.

### Budget

- **POST /budget**  
  Add a new monthly budget.

  ```json
  {
    "category": "Food",
    "limit": 500,
    "year": 2023,
    "month": 10
  }
### Financial Goals

- **POST /financial_goals**  
  Add a new financial goal.

  ```json
  {
    "goal_name": "Buy a car",
    "target_amount": 20000,
    "current_amount": 5000,
    "target_date": "2025-12-31"
  }
## Contributing

Contributions are welcome! If you would like to contribute to this project, please follow these steps:
