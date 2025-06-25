# Import python packages
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
st.write('The name on your Smoothie will be:', name_on_order)

# Pull fruit data including search term
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Show raw fruit table if needed
# st.dataframe(pd_df)

# Fruit picker
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Checkbox for marking as filled
order_filled = st.checkbox('Mark order as filled')

# Order submission
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Use SEARCH_ON column
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Show search mapping
        st.caption(f"The search value for {fruit_chosen} is {search_on}.")

        # Show nutrition info
        st.subheader(f"{fruit_chosen} Nutrition Information")
        api_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on.lower()}")
        if api_response.status_code == 200:
            try:
                data = api_response.json()
                if isinstance(data, list):
                    st.dataframe(data, use_container_width=True)
                else:
                    st.write(data)
            except Exception as e:
                st.error(f"Failed to parse API response: {e}")
        else:
            st.error("Sorry, that fruit is not in our database.")

    # Submit to Snowflake
    time_to_submit = st.button("Submit Order")
    if time_to_submit and name_on_order:
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order, order_filled)
            VALUES ('{ingredients_string.strip()}', '{name_on_order}', {str(order_filled).upper()})
        """
        session.sql(insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
