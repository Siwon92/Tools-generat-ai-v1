# Creator Flow AI — Production Workflow

## Current workflow

1. Enter product/subject and visual settings.
2. Generate exactly 3 image prompts with Gemini 3.6 Flash.
3. Edit and save one image prompt.
4. Create the image in Google Flow.
5. Upload the Google Flow result and select it as the main image.
6. Generate video prompts from the saved image prompt and main-image context.
7. Choose 8-second or 10-second scenes and copy/download the video prompts for Google Flow.

## Important

This Streamlit app generates prompts and manages the selected reference image. Actual image/video rendering is performed in Google Flow; the current app does not call a Google Flow rendering API.

The Gemini API key is entered at runtime and is not stored in the repository.
