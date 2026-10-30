from sqlalchemy import select
from .database import Base, engine, SessionLocal
from .models import User
from .security import hash_password


def seed():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        accounts = [
            ("quanly", "123456", "quanly", "Quản lý KTX"),
            ("ketoan", "123456", "ketoan", "Kế toán KTX"),
        ]
        for username, password, role, full_name in accounts:
            if not db.scalar(select(User).where(User.username == username)):
                db.add(User(
                    username=username,
                    password_hash=hash_password(password),
                    role=role,
                    full_name=full_name,
                ))
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
