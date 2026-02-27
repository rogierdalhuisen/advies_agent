"""Allow running as: python -m src.database.data_preprocessor"""

from .preprocessor import preprocess_user, preprocess_all_users

if __name__ == "__main__":
    user = preprocess_user(118)
    print(user)
