def company_schema(company) -> dict:
    return {"id": str(company["_id"]),
            "name": company["name"],
            "type": company["type"],
            "details": company["details"]}


def companies_schema(companies) -> list:
    return [company_schema(company) for company in companies]