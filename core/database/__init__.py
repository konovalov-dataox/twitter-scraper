from setup_requirements import setup

requirements = ['sqlalchemy', 'PyMySQL']
setup(requirements)

from .database import AcceleratorDatabase
