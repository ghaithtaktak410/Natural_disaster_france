"""Introduction of the project."""
import streamlit as st

FRANCE_COMMUNES = 35000  # approximate number of communes in France (outside the dataset)


def render(df, q):
    n_communes = f"{q['n_communes']:,}"
    st.title("Natural disasters in France")
    st.write("*This page is for anyone who has heard about \"natural disaster decrees\" in the news and wonders "
             "what the numbers really mean. No technical background needed.*")
    st.write(
        f"""
The register of natural disaster decrees ("CatNat") contains {n_communes} communes since {q['first_year']}.
France has about {FRANCE_COMMUNES:,} communes, so this is {q['n_communes'] / FRANCE_COMMUNES:.0%} of them.
When I saw this number, my first thought was that the whole country is exposed.

After looking at the file more closely, I understood that each row is
**one decree for one commune**, not one disaster. So we have to be careful about what we count.
In this project I try to answer three questions:

1. Which types of disasters are recognised, and how does this change over time?
2. Where do they happen most often?
3. Can we really trust this data?
"""
    )
    with st.expander("How to read this page"):
        st.write(
            """
- The filters on the left change all the numbers and charts.
- A natural disaster decree is a decision of the State that recognises an event for a list of
  communes. It does not measure how strong the event was, or how much damage it caused.
- Source: "Arrêtés de catastrophe naturelle par commune" (GASPAR database, French Ministry of
  Ecological Transition), on data.gouv.fr. Licence: see the README.
"""
        )
