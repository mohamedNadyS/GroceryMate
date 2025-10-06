# GroceryMate

A collaborative web application for managing shared grocery lists with family and friends. Built with Streamlit and MySQL.

## Features

- User authentication with secure password hashing
- Create and join shopping groups with unique codes
- Add items with detailed information (quantity, unit, importance, category)
- Filter items by category
- Mark items as purchased or remove them
- Share grocery lists in real-time with group members
- Personal lists for users not in groups

## Prerequisites

- Python 3.7 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)

## Setup Development Environment

### 1. Clone the Repository

```bash
git clone https://github.com/mohamedNadyS/GroceryMate.git
cd GroceryMate
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MySQL Database

Create a MySQL database for the application:

```sql
CREATE DATABASE grocerymate;
```

### 5. Configure Streamlit Secrets

Create a `.streamlit` directory in the project root and add a `secrets.toml` file:

```bash
mkdir .streamlit
```

Create `.streamlit/secrets.toml` with your MySQL credentials:

```toml
[mysql]
host = "localhost"
port = 3306
database = "grocerymate"
user = "your_mysql_username"
password = "your_mysql_password"
```

**Important**: Never commit the `secrets.toml` file to version control. It's already included in `.gitignore`.

## Running the Application

### Local Development

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

## Usage Guide

### First Time Setup

1. **Sign Up**: Create a new account with username, email, and password
   - Username must be 5-20 characters
   - Password must be at least 8 characters with uppercase, lowercase, digit, and special character

2. **Login**: Use your credentials to access the application

### Managing Groups

**Create a Group**:
- Click "Create group" from the home page
- Enter a group name
- Share the generated join code with family/friends

**Join a Group**:
- Click "Join group" from the home page
- Enter the join code provided by the group creator

**Leave a Group**:
- Click "Leave group" to exit your current group

### Managing Items

**Add Items**:
- Click "Add item"
- Fill in item details:
  - Item name (required)
  - Quantity and unit (kg, g, lb, oz, pcs, ml, l, etc.)
  - Importance level (Urgent, Important, Normal, Not-important)
  - Category (Produce, Meat & Seafood, Dairy, etc.)
  - Optional notes

**View Items**:
- Items are displayed on the home page
- Filter by category using the dropdown
- Items are color-coded by importance (red, yellow, green, white)

**Complete Items**:
- Click "Done" to mark an item as purchased
- Click "Remove" to delete an item from the list

## Database Schema

The application automatically creates the following tables:

- `users`: User accounts and authentication
- `user_groups`: Group information and join codes
- `group_members`: Group membership relationships
- `items`: Grocery list items with metadata

## Project Structure

```
GroceryMate/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── LICENSE               # MIT License
├── README.md             # This file
├── .gitignore           # Git ignore rules
└── .streamlit/          # Configuration (not in repo)
    └── secrets.toml     # Database credentials
```

## Security Features

- Passwords are hashed using bcrypt
- SQL injection prevention through parameterized queries
- Input validation for usernames and passwords
- Secure session management

## Demo

To quickly demo the application:

1. Set up the database and configuration as described above
2. Run `streamlit run app.py`
3. Create two user accounts in separate browser sessions
4. Create a group with the first user
5. Join the group with the second user using the join code
6. Add items from both accounts and see real-time synchronization

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
