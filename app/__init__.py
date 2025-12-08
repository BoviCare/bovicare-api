import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)

# Import RAG client for HTTP communication with RAG service
from app import rag_client

# Configuração CORS: permitir frontend deployado e localhost dev
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://18.207.95.49:3000, http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-User-Id, X-User-Name')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

from app import routes
from app import api_v1

with app.app_context():
    try:
        db.create_all()
        print("✅ Banco de dados inicializado com sucesso!")
    except Exception as db_init_error:
        # Gracefully handle DB connection errors (e.g., during setup script or if DB is not available)
        print(f"⚠️  Database initialization skipped: {str(db_init_error)}")
        print("   This is normal if running setup scripts or if the database is not yet available.")

    # Tentativa segura de migrar a coluna profile_photo_url se não existir
    try:
        from sqlalchemy import text
        db.session.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='profile_photo_url'
                ) THEN
                    BEGIN
                        ALTER TABLE users ADD COLUMN profile_photo_url VARCHAR(500);
                    EXCEPTION WHEN OTHERS THEN
                        -- Ignorar erro caso a coluna já exista em alguns bancos
                        NULL;
                    END;
                END IF;
            END$$;
        """))
        db.session.commit()
    except Exception as mig_err:
        # Em SQLite, a sintaxe acima não vale; seguimos sem travar
        db.session.rollback()
        try:
            # Tentativa best-effort para SQLite: criar tabela temporária está fora de escopo; ignorar
            pass
        except Exception:
            pass

    print("✅ Flask API inicializada. RAG service acessível via HTTP client.")
