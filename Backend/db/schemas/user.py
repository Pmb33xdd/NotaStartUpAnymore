def user_schema(user) -> dict:
    return {"id": str(user["_id"]),
            "username": user["username"],
            "name": user["name"],
            "surname": user["surname"],
            "email": user["email"],
            "subscriptions": user["subscriptions"],
            "filters": user["filters"],
            "password": user["password"]}


def users_schema(users) -> list:
    return [user_schema(user) for user in users]