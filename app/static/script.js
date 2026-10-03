const form = document.getElementById("predictionForm");

function pct(value) {
  if (value === undefined || value === null) {
    return "—";
  }

  return `${(Number(value) * 100).toFixed(1)}%`;
}


function friendlyPrediction(value) {
  const names = {
    NO_WATER: "No Water",
    WATER_SOON: "Water Soon",
    WATER_NOW: "Water Now",
  };

  return names[value] || value || "Waiting for Data";
}


function predictionDescription(value) {
  const descriptions = {
    NO_WATER:
      "Current environmental conditions indicate that watering is not required at this time.",

    WATER_SOON:
      "Current environmental conditions indicate that watering may be required soon.",

    WATER_NOW:
      "Current environmental conditions indicate a greater need for watering.",
  };

  return (
    descriptions[value] ||
    "Start the Wokwi simulation to begin monitoring soil conditions."
  );
}


function predictionIcon(value) {
  const icons = {
    NO_WATER: "🌿",
    WATER_SOON: "💧",
    WATER_NOW: "🪴",
  };

  return icons[value] || "🌱";
}


function setBar(id, probability) {
  const element = document.getElementById(id);

  if (!element) return;

  const value =
    probability === undefined || probability === null
      ? 0
      : Number(probability) * 100;

  element.style.width = `${value}%`;
}


/* ==========================
   MANUAL TESTING
========================== */

function showPrediction(data) {
  document.getElementById("prediction").textContent =
    friendlyPrediction(data.prediction);

  document.getElementById("confidence").textContent =
    `Confidence: ${pct(data.confidence)}`;

  const probs = data.probabilities || {};

  document.getElementById("pNoWater").textContent =
    pct(probs.NO_WATER);

  document.getElementById("pWaterSoon").textContent =
    pct(probs.WATER_SOON);

  document.getElementById("pWaterNow").textContent =
    pct(probs.WATER_NOW);
}


if (form) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
      soil_moisture: Number(
        document.getElementById("soil_moisture").value
      ),

      temperature: Number(
        document.getElementById("temperature").value
      ),

      humidity: Number(
        document.getElementById("humidity").value
      ),
    };

    try {
      const response = await fetch("/api/predict", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.error || "Prediction failed.");
        return;
      }

      showPrediction(data);

    } catch (error) {
      alert("Unable to communicate with the Flask server.");
    }
  });
}


/* ==========================
   LIVE SENSOR DASHBOARD
========================== */

function updateSensorDescriptions(data) {

  const moisture = Number(data.soil_moisture);
  const temperature = Number(data.temperature);
  const humidity = Number(data.humidity);


  let moistureText = "Moderate";

  if (moisture < 30) {
    moistureText = "Low moisture";
  } else if (moisture >= 70) {
    moistureText = "High moisture";
  }

  document.getElementById("moistureStatus").textContent =
    moistureText;


  let temperatureText = "Moderate";

  if (temperature < 20) {
    temperatureText = "Cool";
  } else if (temperature > 30) {
    temperatureText = "Warm";
  }

  document.getElementById("temperatureStatus").textContent =
    temperatureText;


  let humidityText = "Moderate";

  if (humidity < 40) {
    humidityText = "Low humidity";
  } else if (humidity > 70) {
    humidityText = "High humidity";
  }

  document.getElementById("humidityStatus").textContent =
    humidityText;
}


function activateSystemFlow() {
  const stages = [
    "flowSensors",
    "flowESP",
    "flowAPI",
    "flowAI",
    "flowOutput",
  ];

  stages.forEach((id, index) => {
    setTimeout(() => {
      const stage = document.getElementById(id);

      if (stage) {
        stage.classList.add("active");
      }

    }, index * 130);
  });

  setTimeout(() => {
    stages.forEach((id) => {
      const stage = document.getElementById(id);

      if (stage) {
        stage.classList.remove("active");
      }
    });

  }, 1500);
}


function updateLiveDashboard(data) {

  document.getElementById("latestMoisture").textContent =
    `${Number(data.soil_moisture).toFixed(1)}%`;

  document.getElementById("latestTemperature").textContent =
    `${Number(data.temperature).toFixed(1)} °C`;

  document.getElementById("latestHumidity").textContent =
    `${Number(data.humidity).toFixed(1)}%`;


  document.getElementById("liveAssessment").textContent =
    friendlyPrediction(data.prediction);

  document.getElementById("assessmentDescription").textContent =
    predictionDescription(data.prediction);

  document.getElementById("assessmentIcon").textContent =
    predictionIcon(data.prediction);


  document.getElementById("liveConfidence").textContent =
    pct(data.confidence);

  setBar("confidenceBar", data.confidence);


  const probs = data.probabilities || {};

  document.getElementById("liveNoWater").textContent =
    pct(probs.NO_WATER);

  document.getElementById("liveWaterSoon").textContent =
    pct(probs.WATER_SOON);

  document.getElementById("liveWaterNow").textContent =
    pct(probs.WATER_NOW);


  setBar("barNoWater", probs.NO_WATER);
  setBar("barWaterSoon", probs.WATER_SOON);
  setBar("barWaterNow", probs.WATER_NOW);


  updateSensorDescriptions(data);


  const badge =
    document.getElementById("connectionBadge");

  badge.classList.remove("waiting");
  badge.classList.add("connected");

  document.getElementById("connectionText").textContent =
    "Sensor data connected";


  if (data.timestamp) {
    const date = new Date(data.timestamp);

    document.getElementById("latestTimestamp").textContent =
      `Last sensor update: ${date.toLocaleTimeString()}`;
  }


  activateSystemFlow();
}


async function refreshLatest() {

  try {

    const response = await fetch("/api/latest", {
      cache: "no-store",
    });

    const data = await response.json();


    if (
      data.soil_moisture === null ||
      data.soil_moisture === undefined
    ) {
      return;
    }


    updateLiveDashboard(data);

  } catch (error) {

    const badge =
      document.getElementById("connectionBadge");

    badge.classList.remove("connected");

    document.getElementById("connectionText").textContent =
      "Connection unavailable";
  }
}


refreshLatest();

setInterval(refreshLatest, 3000);


/* ==========================
   TESTING MODE TOGGLE
========================== */

const testingToggle =
  document.getElementById("testingToggle");

const testingContent =
  document.getElementById("testingContent");

const toggleSymbol =
  document.getElementById("toggleSymbol");


testingToggle.addEventListener("click", () => {

  testingContent.classList.toggle("open");

  if (testingContent.classList.contains("open")) {
    toggleSymbol.textContent = "−";
  } else {
    toggleSymbol.textContent = "+";
  }

});
/* ==========================
   SYSTEM FLOW INFORMATION
========================== */

const flowInformation = {

  sensors: {
    icon: "🌱",

    title: "Sensor Input",

    description:
      "The system collects three environmental inputs: soil moisture, temperature, and humidity.",

    role:
      "The potentiometer in Wokwi simulates the soil moisture sensor, while the DHT22 provides temperature and humidity readings."
  },


  esp32: {
    icon: "⚙️",

    title: "ESP32",

    description:
      "The ESP32 acts as the main embedded controller of the soil monitoring system.",

    role:
      "It reads the simulated sensor values and sends the soil moisture, temperature, and humidity data to the Flask web application."
  },


  flask: {
    icon: "↔️",

    title: "Flask API",

    description:
      "The Flask API provides communication between the ESP32 simulation, the machine-learning model, and the web dashboard.",

    role:
      "It receives sensor readings from the ESP32, sends them to the ML model for prediction, and provides the resulting data to the dashboard."
  },


  ai: {
    icon: "🧠",

    title: "AI / ML Model",

    description:
      "Machine-learning algorithms analyze the soil moisture, temperature, and humidity values to determine the watering condition.",

    role:
      "KNN, SVM, and Random Forest are evaluated as classification models. The system classifies the readings as No Water, Water Soon, or Water Now."
  },


  assessment: {
    icon: "💧",

    title: "Watering Assessment",

    description:
      "The result of the machine-learning analysis is presented as a simple watering assessment for the user.",

    role:
      "The dashboard displays No Water, Water Soon, or Water Now together with the model's confidence and the latest environmental readings."
  }

};


const flowModal =
  document.getElementById("flowModal");

const closeFlowModal =
  document.getElementById("closeFlowModal");


document
  .querySelectorAll(".flow-step.clickable")
  .forEach((step) => {

    step.addEventListener("click", () => {

      const key = step.dataset.step;
      const information = flowInformation[key];

      if (!information) return;


      document.getElementById("modalIcon").textContent =
        information.icon;

      document.getElementById("modalTitle").textContent =
        information.title;

      document.getElementById("modalDescription").textContent =
        information.description;

      document.getElementById("modalRole").textContent =
        information.role;


      flowModal.classList.add("open");

      document.body.style.overflow = "hidden";

    });

  });


function closeModal() {

  flowModal.classList.remove("open");

  document.body.style.overflow = "";

}


closeFlowModal.addEventListener(
  "click",
  closeModal
);


flowModal.addEventListener(
  "click",
  (event) => {

    if (event.target === flowModal) {
      closeModal();
    }

  }
);


document.addEventListener(
  "keydown",
  (event) => {

    if (
      event.key === "Escape" &&
      flowModal.classList.contains("open")
    ) {
      closeModal();
    }

  }
);