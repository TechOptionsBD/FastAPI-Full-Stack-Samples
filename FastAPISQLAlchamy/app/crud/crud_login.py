from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Any

import sys

sys.path.append("..")
from db import models, pagination
from util import passutil, schemas
from logs import fastapi_logger
from crud import get_user


class CRUDLogin:

    def check_username_password(self, email: str, password: str,
                                db: Session) -> Any:
        """ Verify Password"""
        db_user_info = get_user(email=email, db=db)

        return passutil.verify_password(str(password),
                                        str(db_user_info.password))

    def check_active_session(self, session_id: str,
                             db: Session):
        """ check for active session """
        try:
            db_session = db.query(models.UsersLoginAttempt).filter(
                models.UsersLoginAttempt.session_id == session_id).first()

            return db_session
        except SQLAlchemyError as e:
            fastapi_logger.exception("logoff_user")
            return None

    def login_user(self, user: schemas.UserLogIn, session_id: str,
                   db: Session) -> Any:
        """ Login Attempt Record """
        try:
            db_session = models.UsersLoginAttempt(
                email=user.email,
                session_id=session_id,
                ip_address=user.ip_address,
                browser=user.browser,
                status="logged_in")
            db.add(db_session)
            db.commit()
            db.refresh(db_session)
            return db_session
        except SQLAlchemyError as e:
            fastapi_logger.exception("login_user")
            return None

    def active_user(self, session_id: str,
                    db: Session) -> Any:
        """ check for active user"""
        try:
            db_session = db.query(models.UsersLoginAttempt).filter(
                models.UsersLoginAttempt.session_id == session_id).first()

            db_session.status = "active"
            db.commit()
            db.refresh(db_session)
            return db_session
        except SQLAlchemyError as e:
            fastapi_logger.exception("active_user")
            return None

    def logoff_user(self, session_id: str,
                    db: Session) -> Any:
        """ Logging off Record"""
        try:
            db_session = db.query(models.UsersLoginAttempt).filter(
                models.UsersLoginAttempt.session_id == session_id).first()

            db_session.status = "logged_off"
            db.commit()
            db.refresh(db_session)
            return db_session
        except SQLAlchemyError as e:
            fastapi_logger.exception("logoff_user")
            return None


crud_login = CRUDLogin()
