 Of course. Here are the commands to run the system locally for testing:

  1. Set Up Environment Variables

  Before running the applications, you need to set the following environment
  variable. Make sure to replace "your_google_maps_api_key" with your actual
  Google Maps API key.

   1 export GOOGLE_MAPS_API_KEY="your_google_maps_api_key"

  2. Install Dependencies

  You'll need to install the Python dependencies for both the dora and pilot
  projects.

  For the `dora` agent:

   1 cd /home/user/vigilant-journey/dora
   2 uv pip install -r requirements.txt

  For the `pilot` agent:

   1 cd /home/user/vigilant-journey/pilot
   2 uv pip install -r requirements.txt

  3. Run the Services

  You will need two separate terminal sessions to run both the dora and pilot
  applications.

  Terminal 1: Start the `dora` A2A Server

   1 cd /home/user/vigilant-journey/dora
   2 source .venv/bin/activate
   3 uvicorn dora.dora.agent:a2a_app --host 0.0.0.0 --port 8001

  Terminal 2: Start the `pilot` Backend Server

   1 cd /home/user/vigilant-journey/pilot
   2 uvicorn main:app --host 0.0.0.0 --port 8000

  4. Test the Application

   1. Open your web browser and navigate to the mooncake frontend (I'm assuming
      it's running on http://localhost:3000 based on the project structure).
   2. Click the voice input button and say a map-related command, such as:
       * "Show me the Eiffel Tower"
       * "Where is the Golden Gate Bridge?"
       * "Find Central Park in New York"

  The system should now process your voice command, delegate the request to
  the dora agent, get the location from the Google Maps service, and update
  the 3D map in the mooncake application.