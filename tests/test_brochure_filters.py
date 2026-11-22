"""get_brochure_offers filters (categories, exclude, compact, sort) on synthetic viewer data, offline.
Run: uv run python tests/test_brochure_filters.py"""
import asyncio, json, os, tempfile
from pathlib import Path

os.environ["KAUFDA_MCP_PREFS"] = str(Path(tempfile.mkdtemp()) / "prefs.json")
from kaufda_mcp import server as S  # noqa: E402

BID = "6a40c781-41fb-45eb-a279-398e8d00acd9"


def offer(i, name, brand, path, price, regular=None):
    deals = [{"type": "SALES_PRICE", "min": price}]
    if regular:
        deals.append({"type": "REGULAR_PRICE", "min": regular})
    return {"content": {"id": f"00000000-0000-0000-0000-00000000000{i}", "deals": deals,
                        "parentContent": {"id": BID, "page": {"number": 0}},
                        "publisher": {"name": "Lidl"},
                        "products": [{"name": name, "brandName": brand,
                                      "categoryPaths": [{"name": n} for n in path]}]}}


PAGES = [{"number": 0, "offers": [
    offer(1, "Feldsalat", None, ["Lebensmittel und Getränke", "Gemüse", "Feldsalat"], 1.19),
    offer(2, "Rum", "X", ["Lebensmittel und Getränke", "Alkoholische Getränke", "Rum"], 9.99),
    offer(3, "Toaster", "Y", ["Elektronik und Technik", "Toaster"], 19.99, 39.99),
    offer(4, "Roquefort", "Deluxe", ["Lebensmittel und Getränke", "Käse"], 2.29, 3.49),
    offer(5, "Prosciutto", "DELUXE", ["Lebensmittel und Getränke", "Schinken"], 4.99),
]}]


async def fake_load(brochure_id, location):
    return BID, {"publisher": {"name": "Lidl"}}, PAGES


async def main():
    S._load_brochure = fake_load
    r = json.loads(await S.get_brochure_offers(BID, categories=["Lebensmittel und Getränke"],
                                               exclude=["Alkoholische Getränke"], compact=True))
    names = [o["product"] for o in r["offers"]]
    assert names == ["Feldsalat", "Roquefort", "Prosciutto"], names
    assert r["brands"] == {"DELUXE": 2}, r["brands"]
    assert set(r["offers"][1]) <= {"product", "brand", "category", "description", "price_text", "app_price",
                                   "program", "discount_pct", "validity", "page", "app_only", "online_only",
                                   "multi_buy", "conditions"}, r["offers"][1]
    assert r["offers"][1]["category"] == "Lebensmittel und Getränke › Käse"
    r = json.loads(await S.get_brochure_offers(BID, sort="discount", max_results=2))
    assert [o["product"] for o in r["offers"]][0] in ("Toaster", "Roquefort"), r["offers"]
    assert all("_categor" not in k for o in r["offers"] for k in o)
    r = json.loads(await S.get_brochure_offers(BID, exclude=["Toaster"]))
    assert "Toaster" not in [o["product"] for o in r["offers"]]
    print("ok: categories, exclude, compact, brands, sort")


asyncio.run(main())
