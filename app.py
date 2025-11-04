import requests
import streamlit as st

AIC_SEARCH_URL = "https://api.artic.edu/api/v1/artworks/search"
AIC_ARTWORK_URL = "https://api.artic.edu/api/v1/artworks/{id}"
AIC_WEB_UI = "https://www.artic.edu/artworks/{id}"
IIIF_IMAGE = "https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"

st.set_page_config(page_title="Open Museum Explorer", page_icon="🖼️", layout="wide")

# ---------- Sidebar Controls ----------
st.sidebar.header("🔎 Search the Collection")
query = st.sidebar.text_input("Keyword", value=st.session_state.get("query", "sunflower"))
per_page = st.sidebar.select_slider("Results per page", options=[9, 12, 15, 18, 21, 24], value=12)
page = st.sidebar.number_input("Page", min_value=1, value=st.session_state.get("page", 1), step=1)
show_only_with_images = st.sidebar.checkbox("Only show items with images", value=True)
st.sidebar.markdown("---")
st.sidebar.caption("Data source: Art Institute of Chicago Open API")

if st.sidebar.button("Search", use_container_width=True):
    st.session_state["query"] = query
    st.session_state["page"] = page

def search_artworks(q: str, page: int, limit: int):
    """Search artworks from AIC and return (items, pagination)."""
    params = {
        "q": q or "",
        "page": page,
        "limit": limit,
        "fields": "id,title,image_id,artist_title,date_display,medium_display",
    }
    try:
        r = requests.get(AIC_SEARCH_URL, params=params, timeout=20)
        r.raise_for_status()
        js = r.json()
        return js.get("data", []), js.get("pagination", {})
    except Exception as e:
        st.error(f"Search failed: {e}")
        return [], {}

def fetch_artwork_detail(art_id: int):
    try:
        r = requests.get(AIC_ARTWORK_URL.format(id=art_id), params={
            "fields": "id,title,artist_title,date_display,medium_display,dimensions,provenance_text,thumbnail,term_titles,image_id,credit_line,place_of_origin,classification_title"
        }, timeout=20)
        r.raise_for_status()
        return r.json().get("data", {})
    except Exception as e:
        st.error(f"Failed to load details: {e}")
        return {}

st.title("🖼️ Open Museum Explorer")
st.caption("Built with the **Art Institute of Chicago** open API.")

items, pagination = search_artworks(query, page, per_page)

total_pages = pagination.get("total_pages", 1)
total_items = pagination.get("total", 0)
st.write(f"**{total_items}** results for “{query}”. Page **{page} / {total_pages}**.")

# ---------- Results Grid ----------
def card(item):
    cols = st.columns([1, 1.2])
    with cols[0]:
        image_id = item.get("image_id")
        if image_id:
            st.image(IIIF_IMAGE.format(image_id=image_id), use_column_width=True)
        else:
            st.info("No image")
    with cols[1]:
        st.subheader(item.get("title") or "Untitled")
        st.write(item.get("artist_title") or "Unknown artist")
        dd = item.get("date_display")
        md = item.get("medium_display")
        meta = " · ".join([x for x in [dd, md] if x])
        if meta:
            st.caption(meta)
        c1, c2 = st.columns([1,1])
        with c1:
            if st.button("🔍 View details", key=f"detail_{item['id']}"):
                st.session_state["selected_id"] = item["id"]
                st.experimental_rerun()
        with c2:
            st.link_button("↗ Open on AIC", AIC_WEB_UI.format(id=item['id']))

# layout: 3 cards per row
row_cols = st.columns(3)

for i, it in enumerate(items):
    if show_only_with_images and not it.get("image_id"):
        continue
    with row_cols[i % 3]:
        with st.container(border=True):
            card(it)

# ---------- Pagination Controls ----------
pc1, pc2, pc3 = st.columns(3)
with pc1:
    if st.button("⏮ First", disabled=(page <= 1)):
        st.session_state["page"] = 1
        st.experimental_rerun()
with pc2:
    if st.button("◀ Prev", disabled=(page <= 1)):
        st.session_state["page"] = max(1, page-1)
        st.experimental_rerun()
with pc3:
    if st.button("Next ▶", disabled=(page >= total_pages)):
        st.session_state["page"] = min(total_pages, page+1)
        st.experimental_rerun()

# ---------- Detail Drawer ----------
if "selected_id" in st.session_state:
    art_id = st.session_state["selected_id"]
    with st.expander(f"Artwork details (ID {art_id})", expanded=True):
        data = fetch_artwork_detail(art_id)
        if data:
            img_id = data.get("image_id")
            if img_id:
                st.image(IIIF_IMAGE.format(image_id=img_id), use_column_width=True)
            st.markdown(f"### {data.get('title') or 'Untitled'}")
            if data.get("artist_title"):
                st.write(f"**Artist**: {data['artist_title']}")
            if data.get("date_display"):
                st.write(f"**Date**: {data['date_display']}")
            if data.get("medium_display"):
                st.write(f"**Medium**: {data['medium_display']}")
            if data.get("dimensions"):
                st.write(f"**Dimensions**: {data['dimensions']}")
            if data.get("classification_title"):
                st.write(f"**Classification**: {data['classification_title']}")
            if data.get("place_of_origin"):
                st.write(f"**Origin**: {data['place_of_origin']}")
            if data.get("credit_line"):
                st.write(f"**Credit**: {data['credit_line']}")
            if data.get("provenance_text"):
                with st.expander("Provenance"):
                    st.write(data["provenance_text"])
            st.link_button("↗ View on artic.edu", AIC_WEB_UI.format(id=art_id))
        if st.button("Close"):
            del st.session_state["selected_id"]
            st.experimental_rerun()