# AI Soil Monitoring — trained SVM

The SVM is already trained. Use the offline Wokwi version first; no Python, Wi-Fi, Flask, tunnel, or retraining is needed for that demonstration.

## Wokwi: easiest setup
1. Open your project https://wokwi.com/projects/476603997228650497 (or make a copy).
2. Replace sketch.ino with the contents of wokwi/sketch.ino.
3. Add a new file named soil_svm.h and paste the entire contents of wokwi/soil_svm.h. This generated header contains the trained model, not fixed moisture thresholds.
4. Keep your existing wiring, or copy wokwi/diagram.json. Keep the libraries listed in wokwi/libraries.txt installed.
5. Start the simulation. Turn the potentiometer to change simulated soil moisture. Click DHT22 and change temperature and humidity.
6. OLED and Serial Monitor display NO_WATER, WATER_SOON, or WATER_NOW from the SVM every two seconds.

Pins: potentiometer SIG GPIO34; DHT22 SDA GPIO4; OLED SDA GPIO21, SCL GPIO22; OLED address 0x3C. The potentiometer mapping follows your original code: 0 ADC -> 0% moisture; 4095 -> 100%. Soil moisture is simulated and not physically calibrated.

Files sketch.ino and soil_svm.h must be in the same Wokwi project. Uploading the ZIP alone or copying only sketch.ino does not install the model. The offline version does not send data to the Flask dashboard.

## Optional Flask dashboard
Python 3.11 or newer is required. Double-click run_windows.bat after extracting the ZIP. It creates a virtual environment, installs the pinned dependencies, and launches the dashboard. Visit http://127.0.0.1:5000 and use manual testing.

Equivalent PowerShell commands, from this extracted project folder:
```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe apppp.py
```

The app loads the same scaled SVM from model/soil_model.joblib. Keep the pinned scikit-learn version to avoid model loading incompatibilities.

## Optional live Wokwi-to-dashboard mode
Use esp32/soil_monitor.ino instead of the offline sketch, with esp32/diagram.json and esp32/libraries.txt. Change serverEndpoint to your publicly reachable HTTPS Flask URL ending in /api/sensor. The supplied placeholder cannot connect until you configure it. Wokwi-GUEST uses an empty password. Localhost on your computer is not a public endpoint. Start your Flask server and tunnel/hosting service before starting the simulation. This mode needs Wi-Fi and a working public endpoint. No LEDs are required.

## Retraining (optional)
The dataset is already provided; do not regenerate it unless changing the synthetic design intentionally.
```powershell
.\.venv\Scripts\python.exe model	rain_model.py
```
This updates the trained model, metrics, held-out predictions, CV results, and offline soil_svm.h. Copy the regenerated header to Wokwi after retraining, and restart Flask.

## Included evaluation and verification
Read TRAINING_RESULTS.md, model/metrics.json, and model/verification.json. tests/verify.py verifies Flask endpoints and compiles the exported header with a host C++ compiler to compare against Python predictions. It requires g++ in addition to Python dependencies.

Host C++ checks do not verify Arduino libraries or the live Wokwi circuit. The ESP32 Arduino sketch and Wokwi browser simulation have not been compiled/run here because the Arduino toolchain was unavailable.

## Dataset limitation
This is a classroom simulation using synthetic labeled data. The formula in dataset/generate_dataset.py defines the assumed demand and adds noise. Evaluation is not evidence of real-world watering correctness. See TRAINING_RESULTS.md for supported training ranges and results.
