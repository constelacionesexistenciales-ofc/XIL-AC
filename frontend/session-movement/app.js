(() => {
  "use strict";
  const token = document.querySelector("#token");
  const objective = document.querySelector("#objective");
  const startButton = document.querySelector("#start");
  const sessionIdRow = document.querySelector("#sessionIdRow");
  const sessionIdView = document.querySelector("#sessionId");
  const setupStatus = document.querySelector("#setupStatus");
  const measureStatus = document.querySelector("#measureStatus");
  const saveButton = document.querySelector("#saveSnapshot");
  const phaseButtons = [...document.querySelectorAll("[data-phase]")];
  const source = document.querySelector("#source");
  const emptyReport = document.querySelector("#emptyReport");
  const reportContent = document.querySelector("#reportContent");
  const reportSummary = document.querySelector("#reportSummary");
  const chart = document.querySelector("#chart");
  const reportNotice = document.querySelector("#reportNotice");
  const toast = document.querySelector("#toast");
  const labels = {
    availability: "Disponibilidad interna",
    action_capacity: "Capacidad de acción",
    integration_capacity: "Capacidad integradora",
    phenomenological_movement: "Movimiento fenomenológico",
    vitality_energy: "Vitalidad percibida",
    coping_availability: "Disponibilidad para afrontar"
  };
  const objectiveLabels = {
    stabilization: "Estabilización y cuidado del momento",
    availability: "Construir disponibilidad interna",
    exploration: "Explorar y diferenciar la experiencia",
    integration: "Integrar lo reconocido",
    action: "Ampliar posibilidades de acción",
    other: "Objetivo contextual"
  };
  let activeSessionId = "";
  let activePhase = "arrival";
  let latestReport = null;
  let toastTimer = null;

  document.querySelectorAll("[data-metric]").forEach((select) => {
    select.add(new Option("NE", ""));
    for (let score = 0; score <= 4; score += 1) select.add(new Option(String(score), String(score)));
    select.value = "";
  });

  function notify(message) {
    toast.textContent = message;
    toast.classList.add("visible");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove("visible"), 3200);
  }

  function authHeaders() {
    const value = token.value.trim();
    if (!value) throw new Error("Ingresá un token autorizado. No se guarda en el navegador.");
    return { "Content-Type": "application/json", "Authorization": "Bearer " + value };
  }

  async function apiRequest(path, options = {}) {
    const response = await fetch(path, { ...options, headers: { ...authHeaders(), ...(options.headers || {}) } });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = typeof body.detail === "string" ? body.detail : body.detail?.code || body.detail?.notice;
      const messages = {
        SESSION_MOVEMENT_DISABLED: "El indicador está desactivado en el servidor. No se ha guardado nada.",
        401: "El token no es válido o venció.",
        403: "Tu rol no tiene permiso para esta operación.",
        404: "No se encontró el registro para este usuario.",
        409: "El momento no corresponde al estado del registro o ya se guardó."
      };
      throw new Error(messages[detail] || messages[response.status] || detail || "La operación no se completó.");
    }
    return body;
  }

  function setPhase(phase) {
    activePhase = phase;
    phaseButtons.forEach((button) => button.classList.toggle("active", button.dataset.phase === phase));
    const phaseLabels = { arrival: "Guardar llegada", during: "Guardar observación durante", closing: "Guardar cierre" };
    saveButton.textContent = phaseLabels[phase];
    measureStatus.textContent = phase === "arrival"
      ? "Registrá el punto de partida. Si todavía no hay base para valorar una dimensión, dejala en NE."
      : phase === "during"
        ? "Podés registrar cambios intermedios cuando aporten información; no es obligatorio hacerlo."
        : "Registrá cómo termina el encuentro. El cierre no exige decisión ni acción externa.";
  }

  function getScores() {
    const scores = {};
    document.querySelectorAll("[data-metric]").forEach((select) => {
      scores[select.dataset.metric] = select.value === "" ? null : Number(select.value);
    });
    return scores;
  }

  function renderReport(data) {
    latestReport = data;
    emptyReport.hidden = true;
    reportContent.hidden = false;
    reportSummary.replaceChildren();
    const vitalityDelta = data.delta ? data.delta.vitality_energy : null;
    const copingDelta = data.delta ? data.delta.coping_availability : null;
    const formatDelta = (value) => value === null || value === undefined
      ? "NE · no evaluable"
      : (value > 0 ? "+" : "") + value + " puntos";
    const chips = [
      ["Objetivo", objectiveLabels[data.objective] || data.objective],
      ["Estado", data.status === "closed" ? "Cerrado" : "En curso"],
      ["Registros", String(data.snapshots.length)],
      ["Variación de vitalidad", formatDelta(vitalityDelta)],
      ["Disponibilidad para afrontar", formatDelta(copingDelta)]
    ];
    chips.forEach(([label, value]) => {
      const chip = document.createElement("div");
      chip.className = "summary-chip";
      const name = document.createElement("span");
      name.textContent = label;
      const strong = document.createElement("strong");
      strong.textContent = value;
      chip.append(name, strong);
      reportSummary.append(chip);
    });

    chart.replaceChildren();
    const arrival = data.snapshots.find((item) => item.phase === "arrival");
    const closing = data.snapshots.find((item) => item.phase === "closing");
    if (!arrival) {
      const message = document.createElement("p");
      message.className = "empty-report";
      message.textContent = "Todavía falta registrar la llegada. No se calcula variación sin punto de partida.";
      chart.append(message);
    } else {
      Object.entries(labels).forEach(([key, label]) => {
        const before = arrival.scores[key];
        const after = closing ? closing.scores[key] : null;
        const row = document.createElement("div");
        row.className = "chart-row";
        const name = document.createElement("div");
        name.className = "chart-label";
        const strong = document.createElement("strong");
        strong.textContent = label;
        const small = document.createElement("small");
        small.textContent = "Llegada: " + (before === null ? "NE" : before) + " · Cierre: " + (closing ? (after === null ? "NE" : after) : "pendiente");
        name.append(strong, small);
        const bars = document.createElement("div");
        bars.className = "bars";
        [["Llegada", before, ""], ["Cierre", after, "final"]].forEach(([phaseLabel, value, klass]) => {
          const line = document.createElement("div");
          line.className = "bar-line";
          const labelNode = document.createElement("span");
          labelNode.textContent = phaseLabel;
          const track = document.createElement("div");
          track.className = "bar-track";
          const fill = document.createElement("div");
          fill.className = "bar-fill " + klass;
          fill.style.width = value === null || value === undefined ? "0%" : (Number(value) / 4 * 100) + "%";
          track.append(fill);
          line.append(labelNode, track);
          bars.append(line);
        });
        const delta = document.createElement("div");
        delta.className = "delta";
        const change = data.delta ? data.delta[key] : null;
        if (change === null || change === undefined) {
          delta.textContent = "NE";
          delta.classList.add("na");
        } else {
          delta.textContent = (change > 0 ? "+" : "") + change;
          if (change < 0) delta.classList.add("negative");
        }
        row.append(name, bars, delta);
        chart.append(row);
      });
    }

    reportNotice.replaceChildren();
    const p = document.createElement("p");
    const strong = document.createElement("strong");
    strong.textContent = "Lectura responsable. ";
    p.append(strong, document.createTextNode(data.interpretation_notice || "Indicadores descriptivos; requieren revisión del facilitador."));
    reportNotice.append(p);
    const last = data.snapshots[data.snapshots.length - 1];
    if (last) {
      const sourceP = document.createElement("p");
      sourceP.textContent = "Fuente del último registro: " + ({
        jointly_reviewed: "revisión conjunta",
        consultante_self_report: "autorreporte del consultante",
        facilitator_observation: "observación del facilitador"
      }[last.source] || last.source) + ".";
      reportNotice.append(sourceP);
    }
  }

  function reportText(data) {
    const arrival = data.snapshots.find((item) => item.phase === "arrival");
    const closing = data.snapshots.find((item) => item.phase === "closing");
    const lines = [
      "MOVIMIENTO DURANTE EL ENCUENTRO",
      "Objetivo contextual: " + (objectiveLabels[data.objective] || data.objective),
      "Estado: " + (data.status === "closed" ? "cerrado" : "en curso"),
      "Registros intermedios: " + data.snapshots.filter((item) => item.phase === "during").length,
      ""
    ];
    Object.entries(labels).forEach(([key, label]) => {
      const before = arrival?.scores[key];
      const after = closing?.scores[key];
      const delta = data.delta?.[key];
      lines.push(label + ": llegada " + (before === null || before === undefined ? "NE" : before)
        + "; cierre " + (after === null || after === undefined ? "NE" : after)
        + "; variación " + (delta === null || delta === undefined ? "no evaluable" : (delta > 0 ? "+" : "") + delta) + ".");
    });
    lines.push("", "Nota: indicadores descriptivos para revisión del facilitador; no son diagnóstico ni medida clínica validada. El cambio no demuestra causalidad. Revisar contexto, fuente y relato del consultante.");
    return lines.join("\n");
  }

  startButton.addEventListener("click", async () => {
    startButton.disabled = true;
    setupStatus.textContent = "Creando registro protegido…";
    try {
      const data = await apiRequest("/v1/session-movement/sessions", {
        method: "POST", body: JSON.stringify({ objective: objective.value })
      });
      activeSessionId = data.session_id;
      sessionIdView.textContent = activeSessionId;
      sessionIdRow.hidden = false;
      saveButton.disabled = false;
      setupStatus.textContent = "Registro creado. Guardá la llegada para habilitar observaciones intermedias y cierre.";
      notify("Registro creado.");
      await loadReport();
    } catch (error) {
      setupStatus.textContent = error.message;
      notify(error.message);
    } finally {
      startButton.disabled = false;
    }
  });

  phaseButtons.forEach((button) => button.addEventListener("click", () => setPhase(button.dataset.phase)));

  saveButton.addEventListener("click", async () => {
    if (!activeSessionId) {
      notify("Primero creá o recuperá un registro.");
      return;
    }
    saveButton.disabled = true;
    try {
      const data = await apiRequest("/v1/session-movement/sessions/" + encodeURIComponent(activeSessionId) + "/snapshots", {
        method: "POST",
        body: JSON.stringify({ phase: activePhase, source: source.value, scores: getScores() })
      });
      measureStatus.textContent = "Registro guardado: " + data.phase + ".";
      if (activePhase === "closing") {
        saveButton.disabled = true;
        measureStatus.textContent = "Cierre guardado. Ya podés copiar el bloque para el informe posterior.";
      }
      await loadReport();
      if (activePhase !== "closing") setPhase(activePhase === "arrival" ? "during" : "during");
      notify("Medición guardada.");
    } catch (error) {
      measureStatus.textContent = error.message;
      notify(error.message);
    } finally {
      if (activePhase !== "closing") saveButton.disabled = !activeSessionId;
    }
  });

  async function loadReport() {
    const id = activeSessionId || sessionIdView.textContent.trim();
    if (!id) {
      notify("Pegá un identificador de sesión para recuperar el resumen.");
      return;
    }
    activeSessionId = id;
    sessionIdView.textContent = id;
    sessionIdRow.hidden = false;
    const data = await apiRequest("/v1/session-movement/sessions/" + encodeURIComponent(id));
    renderReport(data);
    saveButton.disabled = data.status === "closed";
    if (data.status === "closed") setPhase("closing");
    else if (!data.snapshots.some((item) => item.phase === "arrival")) setPhase("arrival");
    else setPhase("during");
    measureStatus.textContent = "Registro recuperado. " + (data.status === "closed" ? "El cierre ya fue guardado." : "Podés continuar registrando el movimiento.");
  }

  document.querySelector("#refresh").addEventListener("click", async () => {
    const enteredId = window.prompt("Pegá el identificador del registro. No incluyas datos personales.");
    if (!enteredId) return;
    activeSessionId = enteredId.trim();
    try {
      await loadReport();
      notify("Registro recuperado.");
    } catch (error) {
      measureStatus.textContent = error.message;
      notify(error.message);
    }
  });

  document.querySelector("#copyId").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(activeSessionId);
      notify("Identificador copiado.");
    } catch {
      notify("Copiá manualmente el identificador visible.");
    }
  });

  document.querySelector("#copyReport").addEventListener("click", async () => {
    if (!latestReport) return;
    try {
      await navigator.clipboard.writeText(latestReport.report_block || reportText(latestReport));
      notify("Bloque de movimiento copiado para revisar e incorporar al informe.");
    } catch {
      notify("No se pudo copiar automáticamente. El resumen sigue visible en pantalla.");
    }
  });

  document.querySelector("#downloadReport").addEventListener("click", () => {
    if (!latestReport) return;
    const blob = new Blob([JSON.stringify(latestReport, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "xilac-movimiento-sesion.json";
    link.click();
    URL.revokeObjectURL(url);
  });

  setPhase("arrival");
})();
