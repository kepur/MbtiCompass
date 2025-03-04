from alembic import command
from alembic.config import Config

def upgrade():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

def downgrade():
    alembic_cfg = Config("alembic.ini")
    command.downgrade(alembic_cfg, "-1")

if __name__ == "__main__":
    upgrade()  # 运行 `python migrate.py` 自动升级数据库
