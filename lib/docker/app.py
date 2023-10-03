# To run the Streamlit app, use the following command:
# streamlit run app.py

# Import necessary libraries
import streamlit as st
import boto3
import json
import base64
import time
import os
import sys
import io
from PIL import Image

# Function to generate a recipe using Bedrock API
def generate_recipe(bedrock, ingredients, dietary_prefs, cuisine_prefs, status_element):
    prompt = f"\n\nHuman:Generate a step by step recipe using the MAIN ingredients ( {', '.join(ingredients)} ) and is {dietary_prefs.lower()} and has a {cuisine_prefs.lower()} flavor.\n\nAssistant:"

    body = json.dumps({
        "prompt": prompt,
        "max_tokens_to_sample": 300
    })

    modelId = "anthropic.claude-instant-v1"
    accept = 'application/json'
    contentType = 'application/json'

    response = bedrock.invoke_model_with_response_stream(
        modelId=modelId,
        body=body
    )

    generated_recipe = ""
    if response and 'body' in response:
        stream = response.get('body')
        if stream:
            for event in stream:
                chunk = event.get('chunk')
                if chunk:
                    chunk_text = json.loads(chunk.get('bytes').decode())
                    completion = chunk_text.get('completion', '')
                    if completion:
                        generated_recipe += completion
                        status_element.code(generated_recipe, language='text')  
                        time.sleep(0.2)  # Add a small delay for blinking effect

    return generated_recipe

# Function to generate an image using Bedrock StableDiffusion API
def generate_image(bedrock, recipe_text, location):
    stable_diffusion_prompt = f"A photograph of a dish based on the following recipe: {recipe_text}"

    body = json.dumps({
        "text_prompts": [
            {
                "text": stable_diffusion_prompt
            }
        ],
        "cfg_scale": 10,
        "seed": 20,
        "steps": 50
    })

    modelId = "stability.stable-diffusion-xl-v0"
    accept = "application/json"
    contentType = "application/json"

    response = bedrock.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    
    response_body = json.loads(response.get("body").read())
    generated_image_base64 = response_body.get("artifacts")[0].get("base64")
    os.makedirs("data", exist_ok=True)
    image_1 = Image.open(io.BytesIO(base64.decodebytes(bytes(generated_image_base64, "utf-8"))))
    image_1.save(location)

    return location

# Initialize the AWS Bedrock client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

# Step 1: Create a Streamlit app
st.title("Recipe Generator App")

# Step 2: Create drop-down menus for ingredients, dietary preferences, and cuisine preferences
ingredients = st.multiselect("Select Ingredients", ["Chicken", "Beef", "Shrimp", "Pasta", "Tomatoes", "Onions", "Bell Peppers", "Garlic", "Chillies", "Eggplant", "Spinach", "Chickpeas"])
dietary_prefs = st.selectbox("Select Dietary Preferences", ["Non-Vegetarian", "Vegetarian", "Vegan", "Gluten-Free", "Nut-Free"])
cuisine_prefs = st.selectbox("Select Cuisine Preference", ["Italian", "Indian", "Mexican", "Thai", "Chinese","Caribbean","Korean"])


# Step 3: Add a button to initiate the recipe generation process
if st.button("Generate Recipe"):
    # Clear the old recipe 
    image_placeholder = st.empty()
    recipe_status = st.empty()
    generated_recipe = ""
    recipe_status.empty()
    image_placeholder.empty()

    # Step 4: Integrate the Bedrock API for recipe generation
    generated_recipe = generate_recipe(bedrock, ingredients, dietary_prefs, cuisine_prefs, recipe_status)

    # Step 5: Integrate the Bedrock StableDiffusion API for image generation
    img_url = "data/image_1.png"
    generated_image_base64 =  generate_image(bedrock, generated_recipe,img_url)

    # Update the image placeholder with the actual image
    image_placeholder.image(img_url, caption="Recipe Image")


    


