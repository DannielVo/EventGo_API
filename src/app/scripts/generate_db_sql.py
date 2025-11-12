from app.db.session import engine, Base

# import các models để Base biết
from app.general import models as general_models
from app.attendee import models as attendee_models
from app.organizer import models as organizer_models

from sqlalchemy.schema import CreateTable

with open("db.sql", "w", encoding="utf-8") as f:
    for table in Base.metadata.sorted_tables:
        f.write(str(CreateTable(table).compile(engine)) + ";\n\n")

print("db.sql created successfully!")
