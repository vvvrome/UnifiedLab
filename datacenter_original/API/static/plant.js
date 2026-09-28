let plantHistory = {
    labels:[],
    temperature:[],
    power:[],
    coolantFlow:[]
};

let temperatureChart;

let powerChart;

let flowChart;


// ========================================
// CREAR GRÁFICAS
// ========================================

function createPlantCharts() {

    const temperatureContext =
        document
            .getElementById("temperature-chart")
            .getContext("2d");


    const powerContext =
        document
            .getElementById("power-chart")
            .getContext("2d");


    const flowContext =
        document
            .getElementById("flow-chart")
            .getContext("2d");


    temperatureChart =
        new Chart(
            temperatureContext,
            {

                type: "line",

                data: {

                    labels:
                        plantHistory.labels,

                    datasets: [

                        {

                            label:
                                "Temperature",

                            data:
                                plantHistory.temperature,

                            tension: 0.3,

                            pointRadius: 0

                        }

                    ]

                },

                options: {

                    responsive: true,

                    animation: false,

                    scales: {

                        x: {
                            display: false
                        },

                        y: {
                            beginAtZero: false
                        }

                    },

                    plugins: {

                        legend: {
                            display: false
                        }

                    }

                }

            }
        );


    powerChart =
        new Chart(
            powerContext,
            {

                type: "line",

                data: {

                    labels:
                        plantHistory.labels,

                    datasets: [

                        {

                            label:
                                "Power",

                            data:
                                plantHistory.power,

                            tension: 0.3,

                            pointRadius: 0

                        }

                    ]

                },

                options: {

                    responsive: true,

                    animation: false,

                    scales: {

                        x: {
                            display: false
                        },

                        y: {
                            beginAtZero: false
                        }

                    },

                    plugins: {

                        legend: {
                            display: false
                        }

                    }

                }

            }
        );


    flowChart =
        new Chart(
            flowContext,
            {

                type: "line",

                data: {

                    labels:
                        plantHistory.labels,

                    datasets: [

                        {

                            label:
                                "Coolant Flow",

                            data:
                                plantHistory.coolantFlow,

                            tension: 0.3,

                            pointRadius: 0

                        }

                    ]

                },

                options: {

                    responsive: true,

                    animation: false,

                    scales: {

                        x: {
                            display: false
                        },

                        y: {
                            beginAtZero: false
                        }

                    },

                    plugins: {

                        legend: {
                            display: false
                        }

                    }

                }

            }
        );

}


// ========================================
// QKD
// ========================================

function renderQKD(qkd) {

    if (!qkd) return;


    const status =
        String(
            qkd.status || "UNKNOWN"
        ).toUpperCase();


    const statusElement =
        document.getElementById(
            "qkd-status"
        );


    statusElement.textContent =
        `● ${status}`;


    statusElement.className =
        `qkd-status ${status.toLowerCase()}`;


    const qberPercent =
        qkd.qber_percent !== undefined
            ? Number(qkd.qber_percent)
            : Number(qkd.qber || 0) * 100;


    const thresholdPercent =
        Number(
            qkd.qber_threshold || 0
        ) * 100;


    document.getElementById(
        "qkd-qber"
    ).textContent =
        `${qberPercent.toFixed(1)} %`;


    document.getElementById(
        "qkd-threshold"
    ).textContent =
        `${thresholdPercent.toFixed(1)} %`;


    document.getElementById(
        "qkd-key-length"
    ).textContent =
        `${Number(
            qkd.key_length || 0
        )} bits`;


    document.getElementById(
        "qkd-eve"
    ).textContent =
        qkd.eve_detected
            ? "YES"
            : "NO";


    const message =
        document.getElementById(
            "qkd-message"
        );


    if (status === "COMPROMISED") {

        message.textContent =
            `Interception detected. QBER ${qberPercent.toFixed(1)} % exceeds the ${thresholdPercent.toFixed(1)} % threshold. Key rejected.`;

    }

    else if (status === "SECURE") {

        message.textContent =
            `Secure session established. QBER ${qberPercent.toFixed(1)} % is below the ${thresholdPercent.toFixed(1)} % threshold.`;

    }

    else {

        message.textContent =
            "Waiting for QKD session...";

    }

}



// ========================================
// ALERTAS DE PLANTA
// ========================================

function escapeHtml(value) {

    return String(
        value ?? ""
    )

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );

}


async function updatePlantAlerts() {

    try {

        const response =
            await fetch(
                "/api/plant/alerts"
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );

        }


        const alerts =
            await response.json();


        const container =
            document.getElementById(
                "plant-alerts"
            );


        const count =
            document.getElementById(
                "plant-alert-count"
            );


        count.textContent =
            `${alerts.length} events`;


        if (!alerts.length) {

            container.innerHTML =
                '<div class="plant-alert-empty">No plant security alerts.</div>';

            return;

        }


        container.innerHTML =
            alerts
                .slice()
                .reverse()
                .map(
                    alert => {

                        const severity =
                            String(
                                alert.severity ||
                                "INFO"
                            ).toLowerCase();


                        const device =
                            alert.device ||
                            "PLANT";


                        const parameter =
                            alert.parameter
                                ? ` · ${escapeHtml(
                                    alert.parameter
                                )}`
                                : "";


                        const value =
                            alert.value !== null &&
                            alert.value !== undefined
                                ? ` · Value: ${escapeHtml(
                                    alert.value
                                )}`
                                : "";


                        return `

                            <div class="plant-alert ${severity}">

                                <span class="plant-alert-severity">

                                    ${escapeHtml(
                                        severity.toUpperCase()
                                    )}

                                </span>


                                <div class="plant-alert-info">

                                    <strong>
                                        ${escapeHtml(
                                            alert.message
                                        )}
                                    </strong>


                                    <span>

                                        ${escapeHtml(
                                            device
                                        )}

                                        ${parameter}

                                        ${value}

                                    </span>

                                </div>


                                <span class="plant-alert-time">

                                    ${escapeHtml(
                                        alert.timestamp || ""
                                    )}

                                </span>

                            </div>

                        `;

                    }
                )
                .join("");
        const security = data.security;

            if (security) {

                const securityStatus =
                    document.getElementById(
                        "security-controller-status"
                    );

                const channelStatus =
                    document.getElementById(
                        "security-channel-status"
                    );

                const lastAction =
                    document.getElementById(
                        "security-last-action"
                    );

                securityStatus.textContent =
                    security.status;

                channelStatus.textContent =
                    security.channel_status;

                lastAction.textContent =
                    `● ${security.last_action}`;

                lastAction.className =
                    `device-status ${
                        security.status.toLowerCase()
                    }`;
            }

            async function runQKDSession(eve = false) {

                const message =
                    document.getElementById(
                        "qkd-message"
                    );


                message.textContent =
                    "Running QKD session...";


                try {

                    const response =
                        await fetch(
                            "/api/plant/qkd/session",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body:
                                    JSON.stringify({
                                        eve: eve
                                    })
                            }
                        );


                    if (!response.ok) {

                        throw new Error(
                            `HTTP ${response.status}`
                        );

                    }


                    const result =
                        await response.json();


                    renderQKD(result);


                    await updatePlantAlerts();


                }

                catch (error) {

                    console.error(
                        "QKD error:",
                        error
                    );


                    message.textContent =
                        "QKD session error.";

                }

            }

    }

    catch (error) {

        console.error(
            "Plant alerts error:",
            error
        );

    }

}


// ========================================
// ACTUALIZAR PLANTA
// ========================================

async function updatePlant() {

    try {

        const response =
            await fetch(
                "/api/plant"
            );


        const data =
            await response.json();


        // ========================================
        // QKD
        // ========================================

        renderQKD(
            data.qkd
        );


        // ========================================
        // REACTOR
        // ========================================

        const reactor =
            data.reactor;


        const history =
            data.history;


        temperatureChart.data.labels =
            history.labels;


        temperatureChart.data.datasets[0].data =
            history.temperature;


        powerChart.data.labels =
            history.labels;


        powerChart.data.datasets[0].data =
            history.power;


        flowChart.data.labels =
            history.labels;


        flowChart.data.datasets[0].data =
            history.coolant_flow;


        temperatureChart.update();

        powerChart.update();

        flowChart.update();


        document.getElementById(
            "chart-temperature-value"
        ).textContent =
            `${Number(
                reactor.temperature
            ).toFixed(1)} °C`;


        document.getElementById(
            "chart-power-value"
        ).textContent =
            `${Number(
                reactor.power
            ).toFixed(1)} %`;


        document.getElementById(
            "chart-flow-value"
        ).textContent =
            Number(
                reactor.coolant_flow
            ).toFixed(1);


        // ========================================
        // DATOS DEL REACTOR
        // ========================================

        document.getElementById(
            "reactor-name"
        ).textContent =
            reactor.name;


        document.getElementById(
            "reactor-temperature"
        ).textContent =
            `${Number(
                reactor.temperature
            ).toFixed(1)} °C`;


        document.getElementById(
            "reactor-pressure"
        ).textContent =
            Number(
                reactor.pressure
            ).toFixed(1);


        document.getElementById(
            "reactor-flow"
        ).textContent =
            Number(
                reactor.coolant_flow
            ).toFixed(1);


        document.getElementById(
            "reactor-power"
        ).textContent =
            `${Number(
                reactor.power
            ).toFixed(1)} %`;


        document.getElementById(
            "reactor-level"
        ).textContent =
            `${Number(
                reactor.water_level
            ).toFixed(1)} %`;


        document.getElementById(
            "reactor-radiation"
        ).textContent =
            Number(
                reactor.radiation
            ).toFixed(2);


        // ========================================
        // CONTROLLER
        // ========================================

        const controller =
            data.controller;


        document.getElementById(
            "controller-mode"
        ).textContent =
            controller.mode;


        const controllerStatus =
            document.getElementById(
                "controller-status"
            );


        controllerStatus.textContent =
            `● ${controller.status}`;


        controllerStatus.className =
            `device-status ${
                controller.status.toLowerCase()
            }`;


        // ========================================
        // ESTADO DEL REACTOR
        // ========================================

        const reactorStatus =
            document.getElementById(
                "reactor-status"
            );


        reactorStatus.textContent =
            reactor.status;


        reactorStatus.className =
            `plant-status ${
                reactor.status.toLowerCase()
            }`;


        document.getElementById(
            "plant-status"
        ).textContent =
            reactor.status;


        // ========================================
        // SENSORES
        // ========================================

        const sensorsContainer =
            document.getElementById(
                "plant-sensors"
            );


        sensorsContainer.innerHTML =
            "";


        data.sensors.forEach(
            sensor => {

                const element =
                    document.createElement(
                        "div"
                    );


                element.className =
                    "plant-device";


                let sensorValue =
                    "---";


                if (
                    sensor.value !== null &&
                    sensor.value !== undefined
                ) {

                    sensorValue =
                        Number(
                            sensor.value
                        ).toFixed(2);

                }


                element.innerHTML = `

                    <div>

                        <strong>
                            ${sensor.name}
                        </strong>

                        <span>
                            ${sensor.parameter}
                        </span>

                    </div>


                    <strong class="sensor-value">

                        ${sensorValue}

                    </strong>


                    <span
                        class="device-status ${sensor.status.toLowerCase()}"
                    >

                        ● ${sensor.status}

                    </span>

                `;


                sensorsContainer.appendChild(
                    element
                );

            }
        );


        // ========================================
        // ACTUADORES
        // ========================================

        const actuatorsContainer =
            document.getElementById(
                "plant-actuators"
            );


        actuatorsContainer.innerHTML =
            "";


        data.actuators.forEach(
            actuator => {

                const element =
                    document.createElement(
                        "div"
                    );


                element.className =
                    "plant-device";


                element.innerHTML = `

                    <div>

                        <strong>
                            ${actuator.name}
                        </strong>

                        <span>
                            ${actuator.parameter}
                        </span>

                    </div>


                    <span
                        class="device-status ${actuator.status.toLowerCase()}"
                    >

                        ● ${actuator.status}

                    </span>

                `;


                actuatorsContainer.appendChild(
                    element
                );

            }
        );


        // ========================================
        // ACTUALIZAR GRÁFICAS
        // ========================================

        if (temperatureChart) {

            temperatureChart.update();

        }


        if (powerChart) {

            powerChart.update();

        }


        if (flowChart) {

            flowChart.update();

        }


    }

    catch (error) {

        console.error(
            "Plant error:",
            error
        );


        document.getElementById(
            "plant-status"
        ).textContent =
            "Connection error";

    }

}


// ========================================
// INICIALIZACIÓN
// ========================================

createPlantCharts();


updatePlant();


updatePlantAlerts();


setInterval(
    updatePlant,
    1000
);


setInterval(
    updatePlantAlerts,
    1000
);