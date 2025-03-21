import secrets
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.database import engine, SessionLocal, Base
from models.user import User
from infrastructure.security.auth import get_password_hash, validate_password_strength

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_secure_password():
    """Generate a cryptographically secure random password."""
    while True:
        password = secrets.token_urlsafe(16)
        if validate_password_strength(password):
            return password

def init_db(max_retries: int = 3):
    """Initialize database with secure admin credentials and proper error handling."""
    Base.metadata.create_all(bind=engine)
    
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            try:
                # Check if admin user exists
                admin = db.query(User).filter(User.username == "admin").first()
                
                if admin:
                    # Generate new secure password
                    new_password = generate_secure_password()
                    admin.hashed_password = get_password_hash(new_password)
                    admin.role = "admin"  # Ensure admin role
                    db.commit()
                    logger.info("Admin password updated successfully")
                    logger.info(f"New admin password: {new_password}")
                    logger.info("IMPORTANT: Please change this password after first login!")
                else:
                    # Create admin user with secure password
                    admin_password = generate_secure_password()
                    admin_user = User(
                        username="admin",
                        hashed_password=get_password_hash(admin_password),
                        role="admin"
                    )
                    db.add(admin_user)
                    db.commit()
                    logger.info("Admin user created successfully")
                    logger.info(f"Admin credentials - Username: admin, Password: {admin_password}")
                    logger.info("IMPORTANT: Please change this password after first login!")
                return True
                
            except SQLAlchemyError as e:
                db.rollback()
                if attempt == max_retries - 1:
                    logger.error(f"Failed to initialize admin user: {str(e)}")
                    raise
                logger.warning(f"Attempt {attempt + 1} failed, retrying...")
            finally:
                db.close()
                
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Admin initialization failed after {max_retries} attempts: {str(e)}")
                raise

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialization completed")