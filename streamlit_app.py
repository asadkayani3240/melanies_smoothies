# Import Python packages
import streamlit as st
from snowflake.snowpark.functions import col
from snowflake.snowpark import Session
import pandas as pd
import requests

# Connect to Snowflake
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# UI Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input name
name_on_order = st.text_input('Name on Smoothie:')
if name_on_order:
    st.write('The name on your Smoothie will be:', name_on_order)

# Pull fruit data including search term
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Fruit picker
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Checkbox for marking as filled
order_filled = st.checkbox('Mark order as filled')

# Order submission block
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)  # Clean space handling

    for fruit_chosen in ingredients_list:
        # Get the API-safe search term
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Show nutrition info
        st.subheader(f"{fruit_chosen} Nutrition Information")
        api_url = f"https://my.smoothiefroot.com/api/fruit/{search_on.lower()}"
        api_response = requests.get(api_url)

        if api_response.status_code == 200:
            try:
                data = api_response.json()
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Failed to parse API response for {fruit_chosen}: {e}")
        else:
            st.error(f"Could not retrieve data for {fruit_chosen}. Check API availability or SEARCH_ON mapping.")

    # Submit order to Snowflake
    time_to_submit = st.button("Submit Order")
    if time_to_submit and name_on_order:
        # Escape any single quotes in inputs
        safe_name = name_on_order.replace("'", "''")
        safe_ingredients = ingredients_string.replace("'", "''")

        insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order, order_filled)
            VALUES ('{safe_ingredients}', '{safe_name}', {str(order_filled).upper()})
        """
        try:
            session.sql(insert_stmt).collect()
            st.success("Your Smoothie is ordered!", icon="✅")
        except Exception as err:
            st.error(f"Failed to submit order: {err}")
