def user_schema(user) -> dict:
    return {"id": str(user["_id"]),
            "username": user["username"],
            "name": user["name"],
            "surname": user["surname"],
            "email": user["email"],
            "subscriptions": user["subscriptions"],
            "sources": user["sources"],
            "password": user["password"]}


def users_schema(users) -> list:
    return [user_schema(user) for user in users]