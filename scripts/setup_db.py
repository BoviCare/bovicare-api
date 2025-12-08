import sys
import os
import logging
import boto3
from botocore.exceptions import ClientError
from werkzeug.security import generate_password_hash

# Add the parent directory to sys.path to allow importing 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_ssm_parameter(param_name: str, with_decryption: bool = True) -> str:
    """Fetches a parameter from AWS SSM Parameter Store."""
    session = boto3.Session()
    ssm = session.client('ssm', region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'))
    
    try:
        response = ssm.get_parameter(
            Name=param_name,
            WithDecryption=with_decryption
        )
        return response['Parameter']['Value']
    except ClientError as e:
        logger.error(f"Failed to fetch SSM parameter {param_name}: {str(e)}")
        raise

def get_db_connection_string(project_name: str = 'bovicare', env: str = 'production') -> str:
    """Constructs the SQLAlchemy connection string by fetching credentials from SSM."""
    base_path = f"/{project_name}/postgres/bovicare"
    
    try:
        logger.info("Fetching database credentials from AWS SSM...")
        host = get_ssm_parameter(f"{base_path}/host")
        user = get_ssm_parameter(f"{base_path}/admin/username")
        password = get_ssm_parameter(f"{base_path}/admin/password")
        
        dbname = "bovicare"
        port = "5432"
        
        return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        
    except Exception as e:
        logger.error(f"Error constructing DB connection string: {str(e)}")
        raise

# 1. Get Connection String from AWS BEFORE importing app
logger.info("Retrieving database configuration...")
db_uri = get_db_connection_string()

# 2. Set environment variable so app can use it during initialization
os.environ['SQLALCHEMY_DATABASE_URI'] = db_uri

# Now import app (it will read SQLALCHEMY_DATABASE_URI from env)
from app import app, db
from app.models import User

def init_db():
    """
    Initialize the database schema and seed default admin user.
    """
    try:
        
        with app.app_context():
            # 3. Create Tables
            logger.info("Creating database tables...")
            db.create_all()
            logger.info("Tables created successfully.")
            
            # 4. Create Admin User
            admin_email = "admin@bovicare.com"
            admin_username = "admin"
            
            existing_admin = User.query.filter_by(email=admin_email).first()
            
            if not existing_admin:
                logger.info("Creating default admin user...")
                # You can change this default password later
                default_password = "adminpassword123" 
                
                admin = User(
                    username=admin_username,
                    email=admin_email,
                    password=generate_password_hash(default_password),
                    role='admin',
                    is_active=True
                )
                db.session.add(admin)
                db.session.commit()
                logger.info(f"Admin user created! Email: {admin_email}, Password: {default_password}")
            else:
                logger.info("Admin user already exists.")
                
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()

