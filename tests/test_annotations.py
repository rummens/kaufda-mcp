"""Every tool says whether it only reads. Run: uv run python tests/test_annotations.py"""
import asyncio, os, tempfile
from pathlib import Path

os.environ["KAUFDA_MCP_PREFS"] = str(Path(tempfile.mkdtemp()) / "prefs.json")
from kaufda_mcp import server as S  # noqa: E402
from kaufda_mcp.prefs import PreferenceStore  # noqa: E402

READ_ONLY = {"get_preferences", "search_offers", "shopping_list", "list_brochures", "get_brochure_offers",
             "view_brochure_page", "view_offer", "suggest_search_terms", "bring_status", "bring_get_list"}
WRITES = {"set_preferences", "bring_connect", "bring_select_list", "bring_add_items", "bring_remove_items",
          "bring_disconnect"}


async def main():
    tools = {t.name: t for t in await S.mcp.list_tools()}
    assert set(tools) == READ_ONLY | WRITES, f"unexpected tool set: {sorted(set(tools) ^ (READ_ONLY | WRITES))}"
    for name, tool in tools.items():
        hint = tool.annotations and tool.annotations.readOnlyHint
        assert hint is (name in READ_ONLY), f"{name}: readOnlyHint={hint}"
    print(f"ok: {len(READ_ONLY)} read-only, {len(WRITES)} write tools")

    os.environ["KAUFDA_STORES"] = "Lidl, Kaufland"
    os.environ["KAUFDA_APPS"] = "Lidl Plus"
    store = PreferenceStore(Path(tempfile.mkdtemp()) / "p.json")
    assert store.stores() == ["Lidl", "Kaufland"] and store.apps() == ["Lidl Plus"]
    store.save({"stores": ["Aldi"]})
    assert store.stores() == ["Aldi"], "saved preferences win over the environment"
    print("ok: KAUFDA_STORES / KAUFDA_APPS defaults")


asyncio.run(main())
