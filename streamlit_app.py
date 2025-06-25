# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
from snowflake.snowpark import Session  # Added for external connection
import json

# Connect to Snowflake (required for SniS - Streamlit not in Snowflake)
# Reads credentials from a Streamlit secrets file (.streamlit/secrets.toml)
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("""Choose the fruits you want in your custom Smoothie!""")

# Input name for the smoothie order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Load fruit options from the database
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

fruit_rows = my_dataframe.collect()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_rows,
    format_func=lambda row: row['FRUIT_NAME'],
    max_selections=5
)
# Once ingredients are selected
if ingredients_list:
    st.write(ingredients_list)

    ingredients_string = ' '.join([fruit.FRUIT_NAME for fruit in ingredients_list])
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_submit = st.button("Submit Order")
    if time_to_submit:
        if ingredients_string and name_on_order:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
