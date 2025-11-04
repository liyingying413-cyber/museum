import requests
import streamlit as st

# --- MET Museum API endpoints ---
MET_SEARCH_URL = "https://collectionapi.metmuseum.org/public/collection/v1/search"
MET_OBJECT_URL = "https://collectionapi.metmuseum.org/public/collection/v1/objects/{}"
MET_WEB_UI = "https://www.metmuseum.org/art/collection/search/{}"

st.set_page_config(page_title="MET MUSEUM", page_icon="🖼️", layout="wide")

# ---------- Sidebar Controls ----------
st.sidebar.header("🔎 Search the MET Museum")
query = st.sidebar.text_input("Keyword", value=st.session_state.get("query", "bird"))
per_page = st.sidebar.select_slider("Results per page", options=[9, 12, 15, 18, 21, 24], value=12)
page = st.sidebar.number_input("Page", min_value=1, value=st.session_state.get("page", 1), step=1)
show_only_with_images = st.sidebar.checkbox("Only show items with images", value=True)
public_only = st.sidebar.checkbox("Only Public Domain items", value=True)
st.sidebar.markdown("---")
st.sidebar.caption("Data source: **The Metropolitan Museum of Art (Open Access API)**")

if st.sidebar.button("Search", use_container_width=True):
    st.session_state["query"] = query
    st.session_state["page"] = page


# ---------- API helper functions ----------
def search_artworks(q: str, page: int, limit: int, has_images=True):
    """Search artworks from MET Museum."""
    params = {"q": q or ""}
    if has_images:
        params["hasImages"] = "true"
    try:
        r = requests.get(MET_SEARCH_URL, params=params, timeout=20)
        r.raise_for_status()
        js = r.json()
        ids = js.get("objectIDs") or []
        total = len(ids)
        start = (page - 1) * limit
        end = start + limit
        return ids[start:end], total
    except Exception as e:
        st.error(f"Search failed: {e}")
        return [], 0


def fetch_artwork_detail(art_id: int):
    """Fetch a single artwork's metadata."""
    try:
        r = requests.get(MET_OBJECT_URL.format(art_id), timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Failed to load details: {e}")
        return {}


# ---------- Page title ----------
st.title("🖼️ MET MUSEUM")
st.caption("Explore public-domain artworks from The Metropolitan Museum of Art.")

# ---------- Search ----------
ids, total_items = search_artworks(query, page, per_page, has_images=show_only_with_images)
total_pages = max(1, (total_items + per_page - 1) // per_page)
st.write(f"**{total_items}** results for “{query}”. Page **{page} / {total_pages}**.")

# ---------- Result cards ----------
def card(data):
    img = data.get("primaryImageSmall") or data.get("primaryImage")
    title = data.get("title") or "Untitled"
    artist = data.get("artistDisplayName") or "Unknown artist"
    date = data.get("objectDate") or ""
    culture = data.get("culture") or ""
    meta = " · ".join(x for x in [artist, date, culture] if x)

    if img:
        st.image(img, use_container_width=True)
    else:
        st.info("No image available.")
    st.markdown(f"### {title}")
    if meta:
        st.caption(meta)
    st.link_button("↗ View on The Met", MET_WEB_UI.format(data.get("objectID")))


if not ids:
    st.warning("No artworks found.")
else:
    # Display artworks in a responsive grid
    cols = st.columns(3)
    for i, oid in enumerate(ids):
        obj = fetch_artwork_detail(oid)
        if public_only and not obj.get("isPublicDomain", False):
            continue
        with cols[i % 3]:
            with st.container(border=True):
                card(obj)

# ---------- Pagination Controls ----------
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("⏮ First", disabled=(page <= 1)):
        st.session_state["page"] = 1
        st.experimental_rerun()
with col2:
    if st.button("◀ Prev", disabled=(page <= 1)):
        st.session_state["page"] = max(1, page - 1)
        st.experimental_rerun()
with col3:
    if st.button("Next ▶", disabled=(page >= total_pages)):
        st.session_state["page"] = min(total_pages, page + 1)
        st.experimental_rerun()

# ---------- Sidebar cache clear ----------
with st.sidebar:
    if st.button("🔄 Clear cache"):
        st.cache_data.clear()
        st.experimental_rerun()
