from urllib.parse import urlparse

from pymilvus import Role, connections, utility, db

from app.config import settings


def test_create_user():
    if not settings.MILVUS_URI:
        print("MILVUS_URI is not set")
        return

    parsed = urlparse(settings.MILVUS_URI)
    connections.connect(
        alias="default",
        host=parsed.hostname,
        port=parsed.port,
        user="root",
        password="Milvus"
    )
    db_name = settings.MILVUS_DB_NAME

    ensure_database(db_name)
    db.using_database(db_name)

    ensure_rw_role(db_name)

    ensure_user(user="tinyrag", password="tinyrag",
                role_name="rw_role")

    user_info = utility.list_user(
        "tinyrag", include_role_info=True)
    print(f"\nuser_info={user_info}")


def ensure_user(user: str, password: str, role_name: str | None = None) -> bool:
    if utility.list_user(user, include_role_info=True).groups:
        return False

    utility.create_user(
        user=user,
        password=password,
    )
    if role_name:
        role = Role(role_name)
        role.add_user(user)
    return True


def ensure_rw_role(db_name: str) -> bool:
    role = Role("rw_role")
    if role.is_exist():
        return False

    role.create()

    privileges = ["Search", "Insert", "Delete", "Load", "CollectionAdmin"]
    for privilege in privileges:
        role.grant_v2(privilege, "*", db_name=db_name)

    return True

def ensure_database(db_name: str) -> bool:
    if db_name in db.list_database():
        return False

    db.create_database(db_name)
    return True
