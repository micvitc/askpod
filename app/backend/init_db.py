from backend.database import engine, Base
from backend.models import User

Base.metadata.create_all(bind=engine)
