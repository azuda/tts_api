# app.py
# https://huggingface.co/spaces/NihalGazi/Text-To-Speech-Unlimited/blob/main/app.py

from gradio_client import Client
import gradio as gr
import requests
import random
import tempfile
import os

CLIENT = Client("NihalGazi/Text-To-Speech-Unlimited")

# VOICES
VOICES = [
  "alloy", "echo", "fable", "onyx", "nova", "shimmer",  # Standard OpenAI Voices
  "coral", "verse", "ballad", "ash", "sage", "amuch", "dan" # Some additional pre-trained
]



# generates audio via api and return audio bytes
def generate_audio(prompt: str, voice: str, emotion: str, seed: int) -> bytes:
  try:
    # call specific endpoint
    # do NOT pass seed as a kwarg to predict
    # always uses a random seed
    result = CLIENT.predict(
      prompt=prompt,
      voice=voice,
      emotion=emotion,
      use_random_seed=True,
      api_name="/text_to_speech_app"
    )

    # if model returns tuple / list (audio_path, status_str) extract the first element (audio)
    if isinstance(result, (list, tuple)) and len(result) >= 1:
      result = result[0]

    print(f"DEBUG: Received result type: {type(result)}")

    # if model returns raw bytes
    if isinstance(result, (bytes, bytearray)):
      return result

    # if model returns a url string -> fetch
    if isinstance(result, str):
      # data url (base64) support
      if result.startswith("data:"):
        import base64
        try:
          _, b64 = result.split(",", 1)
          return base64.b64decode(b64)
        except Exception as e:
          print(f"Error decoding data URL: {e}")
          raise gr.Error("Failed to decode audio data URL returned by API.")

      # http -> download
      if result.startswith("http"):
        print(f"DEBUG: Downloading audio from URL: {result.split('?')[0]}...")
        # allow trusting custom ca bundle via
        ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE")
        verify = ca_bundle if ca_bundle else True
        try:
          response = requests.get(result, timeout=60, verify=verify)
          response.raise_for_status()
        except requests.exceptions.SSLError as e:
          # retry without verify on exception
          print(f"SSL error when downloading audio: {e}")
          print("Retrying without SSL verification. To avoid this, set REQUESTS_CA_BUNDLE to a PEM that trusts the intercepting proxy (ex. Cloudflare CA)")
          response = requests.get(result, timeout=60, verify=False)
          response.raise_for_status()
        content_type = response.headers.get("content-type", "").lower()
        if "audio" not in content_type:
          print(f"Warning: Unexpected content type received: {content_type}")
          print(f"Response Text: {response.text[:500]}")
          raise gr.Error("No audio returned")
        return response.content

      # local file path -> read it
      if os.path.exists(result):
        with open(result, "rb") as f:
          return f.read()

      # unknown string type
      print(f"Warning: API returned an unexpected string: {result[:200]}")
      raise gr.Error("API returned an unexpected string result. Expected audio URL, local path, or bytes.")

    # unexpected response type
    print(f"Warning: Unsupported response type from API: {type(result)}")
    raise gr.Error("Unsupported response from the TTS API.")

  except requests.exceptions.RequestException as e:
    print(f"Error during audio generation: {e}")
    error_details = ""
    if hasattr(e, 'response') and e.response is not None:
      error_details = e.response.text[:200]
    raise gr.Error("Failed to generate audio. Please wait for a second and try again.")
  except gr.Error:
    # re-raise gr.Error unchanged so upstream can surface it
    raise
  except Exception as e:
    print(f"Unexpected error during audio generation: {e}")
    raise gr.Error("An unexpected error occurred during audio generation. Please wait for a second and try again.")



def text_to_speech_app(prompt: str, voice: str, emotion: str):
  print(f"\n\n\n{prompt}\n\n\n")
  if not prompt:
    raise gr.Error("Prompt cannot be empty.")
  if not emotion:
    emotion = "neutral instructional test reader"
    print("No emotion provided, using default.")
  if not voice:
     raise gr.Error("Please select a voice.")

  # always use a random seed (no user input)
  seed = random.randint(0, 2**32 - 1)
  print(f"Using Seed: {seed}")

  # check nsfw
  print("Checking prompt safety...")
  try:
    # is_nsfw = check_nsfw(prompt)
    is_nsfw = False
  except gr.Error as e:
    return None, f"There was an error. Please wait for a second and try again."

  if is_nsfw:
    print("Prompt flagged as inappropriate.")
    return None, "Error: The prompt was flagged as inappropriate and cannot be processed."

  # if not nsfw
  print("Prompt is safe. Generating audio...")
  try:
    audio_bytes = generate_audio(prompt, voice, emotion, seed)

    # save audio to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
      temp_audio_file.write(audio_bytes)
      temp_file_path = temp_audio_file.name
      print(f"Audio saved temporarily to: {temp_file_path}")

    return temp_file_path, f"Audio generated successfully with voice '{voice}', emotion '{emotion}', and seed {seed}."

  except gr.Error as e:
     return None, str(e)
  except Exception as e:
    print(f"Unexpected error in main function: {e}")
    return None, f"An unexpected error occurred: {e}"



def toggle_seed_input(use_random_seed):
  return gr.update(visible=not use_random_seed, value=12345)



# render web app ui
with gr.Blocks() as app:
  gr.Markdown("# Rundle AI Text-To-Speech Unlimited")
  gr.Markdown("Enter text, choose a voice and emotion, and generate audio.")

  with gr.Row():
    with gr.Column(scale=3):
      prompt_input = gr.Textbox(label="Prompt", placeholder="Enter the text you want to convert to speech")
      emotion_input = gr.Textbox(label="Emotion Style", placeholder="Leave blank for default neutral tone")
      voice_dropdown = gr.Dropdown(label="Voice", choices=VOICES, value="alloy")
    with gr.Column(scale=2):
      # random_seed_checkbox = gr.Checkbox(label="Use Random Seed", value=True)
      # seed_input = gr.Number(label="Specific Seed", value=12345, visible=False, precision=0)
      audio_output = gr.Audio(label="Generated Audio", type="filepath")
      status_output = gr.Textbox(label="Status")

  submit_button = gr.Button("Generate Audio", elem_id="button_colour")

  # random_seed_checkbox.change(
  #   fn=toggle_seed_input,
  #   inputs=[random_seed_checkbox],
  #   outputs=[seed_input]
  # )

  submit_button.click(
    fn=text_to_speech_app,
    inputs=[
      prompt_input,
      voice_dropdown,
      emotion_input,
      # random_seed_checkbox,
      # seed_input
    ],
    outputs=[audio_output, status_output],
    concurrency_limit=30
  )

  # gr.Examples(
  #   examples=[
  #     ["Hello there! This is a test of the text-to-speech system.", "alloy", "neutral", False, 12345],
  #     ["Surely *you* wouldn't want *that*. [laughs]", "shimmer", "sarcastic and mocking", True, 12345],
  #     ["[sobbing] I am feeling... [sighs] a bit down today [cry]", "ballad", "sad and depressed, with stammering", True, 662437],
  #     ["This technology is absolutely amazing!", "nova", "excited and joyful", True, 12345],
  #   ],
  #   inputs=[prompt_input, voice_dropdown, emotion_input, random_seed_checkbox, seed_input],
  #   outputs=[audio_output, status_output],
  #   fn=text_to_speech_app,
  #   cache_examples=False, 
  # )

# css
style = """
#button_colour {
  background-color: #58212E;
  color: white;
  border-color: #58212E;
}
#button_colour:hover {
  background-color: #7A2E42;
}
"""



if __name__ == "__main__":
  try:
    app.launch(css=style)
  except Exception as e:
    print(f"Error launching the app: {e}")
  # if NSFW_URL_TEMPLATE and TTS_URL_TEMPLATE:
  #   app.launch()
  # else:
  #   print("ERROR: Cannot launch app. Required API URL secrets are missing.")
