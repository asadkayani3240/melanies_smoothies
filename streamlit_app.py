# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
from snowflake.snowpark import Session
import json
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
ingredients_string = ''
if ingredients_list:
    for fruit in ingredients_list:
        ingredients_string += fruit + ' '

        # Display Nutrition Header
        st.subheader(f"{fruit} Nutrition Information")

        # API call for each fruit
        response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit.lower()}")
        if response.status_code == 200:
            try:
                nutrition_info = response.json()
                if isinstance(nutrition_info, dict):
                    st.dataframe(nutrition_info, use_container_width=True)
                else:
                    st.warning("Unexpected data format from API.")
            except Exception as e:
                st.error(f"Error parsing JSON: {e}")
        else:
            st.error("Sorry, that fruit is not in our database.")

# Submit Button
time_to_submit = st.button("Submit Order")
if time_to_submit:
    if ingredients_string and name_on_order:
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string.strip()}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
