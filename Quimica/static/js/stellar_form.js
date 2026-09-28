(() => {
    "use strict";

    const COMPOSITION_FIELDS = [
        "composicion",
        "abundancia",
        "Atmosfera",
        "ComposicionInterior"
    ];

    /*
     * Formato esperado:
     * H:70, He:28, O:1, Fe:1
     */

    function parseComposition(raw) {
        const entries = raw
            .split(",")
            .map(part => part.trim())
            .filter(Boolean);

        if (!entries.length) {
            return {
                ok: false,
                message: "Introduce al menos un elemento químico."
            };
        }

        let total = 0;
        const seen = new Set();

        for (const entry of entries) {
            const match = entry.match(
                /^([A-Za-z]{1,3}):\s*(\d+(?:[.,]\d+)?)\s*$/
            );

            if (!match) {
                return {
                    ok: false,
                    message:
                        `Formato incorrecto en "${entry}". ` +
                        "Usa H:70, He:28, O:1, Fe:1"
                };
            }

            const symbol = match[1];
            const amount = Number(
                match[2].replace(",", ".")
            );

            if (seen.has(symbol)) {
                return {
                    ok: false,
                    message: `El elemento ${symbol} está repetido.`
                };
            }

            seen.add(symbol);

            if (!Number.isFinite(amount) || amount < 0) {
                return {
                    ok: false,
                    message:
                        `El porcentaje de ${symbol} debe ser positivo o cero.`
                };
            }

            total += amount;
        }

        if (Math.abs(total - 100) > 0.01) {
            return {
                ok: false,
                message:
                    `Los porcentajes suman ${total.toFixed(2)} %. ` +
                    "Deben sumar 100 %."
            };
        }

        return {
            ok: true,
            message: "Composición química válida: 100 %."
        };
    }

    function showError(input, message) {
        input.setCustomValidity(message);
        input.reportValidity();
    }

    function clearError(input) {
        input.setCustomValidity("");
    }

    document.addEventListener("DOMContentLoaded", () => {
        const forms = document.querySelectorAll(
            'form[action="/stellar/estrella"], ' +
            'form[action="/stellar/planeta"]'
        );

        forms.forEach(form => {
            const compositionInputs = COMPOSITION_FIELDS
                .map(name => form.querySelector(`[name="${name}"]`))
                .filter(Boolean);

            compositionInputs.forEach(input => {
                input.addEventListener("input", () => {
                    clearError(input);
                });
            });

            form.addEventListener("submit", event => {

                // Validar composición química

                for (const input of compositionInputs) {
                    const value = input.value.trim();

                    if (!value) {
                        continue;
                    }

                    const result = parseComposition(value);

                    if (!result.ok) {
                        event.preventDefault();
                        showError(input, result.message);
                        return;
                    }

                    clearError(input);
                }

                // Validar excentricidad orbital

                const eccentricity = form.querySelector(
                    '[name="excentricidad"], [name="Excentricidad"]'
                );

                if (eccentricity && eccentricity.value !== "") {
                    const e = Number(eccentricity.value);

                    if (!Number.isFinite(e) || e < 0 || e >= 1) {
                        event.preventDefault();

                        showError(
                            eccentricity,
                            "La excentricidad debe estar entre 0 y menos de 1."
                        );

                        return;
                    }
                }

                // Validar albedo

                const albedo = form.querySelector(
                    '[name="albedo"], [name="Albedo"]'
                );

                if (albedo && albedo.value !== "") {
                    const a = Number(albedo.value);

                    if (!Number.isFinite(a) || a < 0 || a > 1) {
                        event.preventDefault();

                        showError(
                            albedo,
                            "El albedo debe estar entre 0 y 1."
                        );

                        return;
                    }
                }
            });
        });
    });

    // Permite reutilizar el validador desde otros scripts.

    window.StellarLab = Object.freeze({
        parseComposition
    });

})();