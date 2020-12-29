from models import (
    session, Base
)

# create tables
Base.metadata.create_all()
