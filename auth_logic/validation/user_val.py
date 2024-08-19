import re
import sys
from typing import Optional

from passlib.context import CryptContext

from auth_logic.data_access.user_data import UserDB
from auth_logic.entity.user import User
from auth_logic.exception import AppException
from auth_logic.logger import logging

bcrypt_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginVal:
    """Handles login validation and authentication."""

    def __init__(self, email: str, pwd: str):
        """Initialize with email and password."""
        self.email = email
        self.pwd = pwd
        self.email_regex = re.compile(
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        )

    def validate(self) -> bool:
        """Validate email and password input."""
        try:
            errors = []
            if not self.email:
                errors.append("Email is required")
            if not self.pwd:
                errors.append("Password is required")
            if not self.is_email_valid():
                errors.append("Invalid Email")
            return errors
        except Exception as e:
            raise e

    def is_email_valid(self) -> bool:
        """Check if the email matches the regex."""
        return bool(re.fullmatch(self.email_regex, self.email))

    def verify_pwd(self, plain_pwd: str, hashed_pwd: str) -> bool:
        """Verify if the plain password matches the hashed password."""
        return bcrypt_ctx.verify(plain_pwd, hashed_pwd)

    def validate_login(self) -> dict:
        """Validate login details and return status."""
        errors = self.validate()
        if errors:
            return {"status": False, "msg": errors}
        return {"status": True}

    def auth_user(self) -> Optional[str]:
        """Authenticate user and return user data if successful."""
        try:
            login_status = self.validate_login()
            logging.info("Authenticating user...")
            if login_status["status"]:
                user_data = UserDB()
                logging.info("Fetching user data...")
                user = user_data.fetch_user({"email": self.email})
                if not user:
                    logging.info("User not found")
                    return False
                if not self.verify_pwd(self.pwd, user["password"]):
                    logging.info("Incorrect password")
                    return False
                logging.info("User authenticated")
                return user
            return False
        except Exception as e:
            raise AppException(e, sys) from e


class RegisterVal:
    """Handles user registration validation and saving."""

    def __init__(self, user: User) -> None:
        """Initialize with a User object."""
        try:
            self.user = user
            self.email_regex = re.compile(
                r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
            )
            self.uuid = self.user.uid
            self.user_data = UserDB()
            self.bcrypt_ctx = bcrypt_ctx
        except Exception as e:
            raise e

    def validate(self) -> bool:
        """Validate user registration details."""
        try:
            errors = []
            if not self.user.name:
                errors.append("Name is required")
            if not self.user.username:
                errors.append("Username is required")
            if not self.user.email:
                errors.append("Email is required")
            if not self.user.phone:
                errors.append("Phone Number is required")
            if not self.user.pass1:
                errors.append("Password is required")
            if not self.user.pass2:
                errors.append("Confirm Password is required")
            if not self.is_email_valid():
                errors.append("Invalid Email")
            if not self.is_pwd_valid():
                errors.append("Password must be 8-16 characters long")
            if not self.is_pwd_match():
                errors.append("Passwords do not match")
            if not self.is_user_exists():
                errors.append("User already exists")
            return errors
        except Exception as e:
            raise e

    def is_email_valid(self) -> bool:
        """Check if the email is valid."""
        return bool(re.fullmatch(self.email_regex, self.user.email))

    def is_pwd_valid(self) -> bool:
        """Check if the password length is valid."""
        return 8 <= len(self.user.pass1) <= 16

    def is_pwd_match(self) -> bool:
        """Check if passwords match."""
        return self.user.pass1 == self.user.pass2

    def is_user_exists(self) -> bool:
        """Check if user details already exist in the database."""
        user_exists = any([
            self.user_data.fetch_user({"username": self.user.username}),
            self.user_data.fetch_user({"email": self.user.email}),
            self.user_data.fetch_user({"UUID": self.uuid}),
        ])
        return not user_exists

    @staticmethod
    def hash_pwd(pwd: str) -> str:
        """Hash the password."""
        return bcrypt_ctx.hash(pwd)

    def validate_reg(self) -> bool:
        """Validate registration details and return status."""
        errors = self.validate()
        if errors:
            return {"status": False, "msg": errors}
        return {"status": True}

    def save_user(self) -> bool:
        """Save user details to the database after validation."""
        try:
            logging.info("Validating registration details...")
            if self.validate_reg()["status"]:
                logging.info("Hashing password...")
                hashed_pwd = self.hash_pwd(self.user.pass1)
                user_data = {
                    "Name": self.user.name,
                    "username": self.user.username,
                    "password": hashed_pwd,
                    "email": self.user.email,
                    "ph_no": self.user.phone,
                    "UUID": self.uuid,
                }
                logging.info("Saving user data...")
                self.user_data.add_user(user_data)
                logging.info("User registration successful")
                return {"status": True, "msg": "User registered successfully"}
            logging.info("Registration validation failed")
            return {"status": False, "msg": self.validate()}
        except Exception as e:
            raise e
