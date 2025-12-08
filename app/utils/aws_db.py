import boto3
import logging
import os
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

def get_ssm_parameter(param_name: str, with_decryption: bool = True) -> str:
    """
    Fetches a parameter from AWS SSM Parameter Store.
    """
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
    """
    Constructs the SQLAlchemy connection string by fetching credentials from SSM.
    Expects parameters at: /project/postgres/company/admin/... and /project/postgres/company/host
    """
    # Standard paths based on Terraform output
    base_path = f"/{project_name}/postgres/bovicare"
    
    try:
        logger.info("Fetching database credentials from AWS SSM...")
        host = get_ssm_parameter(f"{base_path}/host")
        user = get_ssm_parameter(f"{base_path}/admin/username")
        password = get_ssm_parameter(f"{base_path}/admin/password")
        
        # DB Name is 'bovicare'
        dbname = "bovicare"
        port = "5432"
        
        return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        
    except Exception as e:
        logger.error(f"Error constructing DB connection string: {str(e)}")
        raise

