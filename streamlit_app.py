# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
from snowflake.snowpark import Session
import json

# Connect to Snowflake
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# UI Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Fetch fruit list
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_rows = [row.FRUIT_NAME for row in my_dataframe.collect()]

# Multi-select UI
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_rows,
    max_selections=5
)

# Submission logic
if ingredients_list:
    st.write(ingredients_list)
    ingredients_string = ' '.join(ingredients_list)

    time_to_submit = st.button("Submit Order")
    if time_to_submit:
        if ingredients_string and name_on_order:
            my_insert_stmt = f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
            import requests
            smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
            st.text(smoothiefroot_response)
