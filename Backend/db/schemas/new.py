def new_schema(new) -> dict:
    return {"id": str(new["_id"]),
            "company": new["company"],
            "title": new["title"],
            "topic": new["topic"],
            "details": new["details"],}


def news_schema(news) -> list:
    return [new_schema(new) for new in news]