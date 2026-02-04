from src.common.database import Base, engine
from src.models import user, user_champion

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
