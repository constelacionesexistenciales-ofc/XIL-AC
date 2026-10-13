(() => {
  "use strict";

  const form = document.querySelector("#researchForm");
  const question = document.querySelector("#researchQuestion");
  const accessToken = document.querySelector("#accessToken");
  const domain = document.querySelector("#domain");
  const publicConfirmation = document.querySelector("#confirmPublicQuery");
  const resultTitle = document.querySelector("#resultTitle");
  const summaryText = document.querySelector("#summaryText");
  const results = document.querySelector("#results");
  const findingList = document.querySelector("#findingList");
  const findingsTitle = document.querySelector(".findings-panel h3");
  const toast = document.querySelector("#toast");
  let toastTimer;

  const domainCopy = {
    science: { label: "Ciencia y salud", topics: ["Estudios", "Mecanismos", "Datos", "Límites"] },
    history: { label: "Historia y cultura", topics: ["Cronología", "Fuentes", "Contexto", "Debates"] },
    technology: { label: "Tecnología", topics: ["Arquitectura", "Capacidades", "Riesgos", "Alternativas"] },
    business: { label: "Negocios y estrategia", topics: ["Objetivos", "Opciones", "Riesgos", "Resultados"] },
    education: { label: "Educación y conceptos", topics: ["Conceptos", "Relaciones", "Ejemplos", "Aplicación"] },
    cfe: { label: "Desarrollo personal y CFE", topics: ["Experiencia", "Perspectivas", "Preguntas", "Aplicación"] }
  };


  const localPrivacyPatterns = [
    /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/i,
    /\b(?:DNI|CUIL|CUIT|pasaporte)\s*(?:n(?:ro|úm(?:ero)?)?\.?\s*)?[:#-]?\s*[A-Z0-9.-]{6,}\b/i,
    /\b(?:teléfono|telefono|celular|whatsapp|contacto)\s*[:=]?\s*\+?\d[\d\s().-]{7,}\d\b/i,
    /\b(?:nombre completo|nombre y apellido|nombre del consultante|consultante|paciente)\s*[:=]\s*[^\n,;]{2,80}/i,
    /\b(?:mi domicilio|mi dirección|mi direccion|vive en|reside en)\s*[:=]?\s*[^\n,;]{5,100}/i,
    /\b(?:mi fecha de nacimiento|fecha de nacimiento|nací el|naci el)\s*[:=]?\s*\d{1,4}[/-]\d{1,2}[/-]\d{1,4}/i,
    /\bmi\s+(?:diagnóstico|diagnostico|medicación|medicacion|historia clínica|historia clinica|tratamiento|psiquiatra|psicólogo|psicologo)\b/i,
    /\b(?:me diagnosticaron|me recetaron|me internaron|padezco|sufro de|estoy en tratamiento por)\b/i,
    /\b(?:quiero quitarme la vida|quiero hacerme daño|quiero hacerme dano|voy a hacerme daño|voy a hacerme dano|fui víctima de|fui victima de|me abusaron|me agredieron|sufrí abuso|sufri abuso|sufrí violencia|sufri violencia)\b/i
  ];

  function containsLikelyPersonalSensitiveData(value) {
    return localPrivacyPatterns.some((pattern) => pattern.test(value));
  }

  function showToast(message) {
    toast.textContent = message;
    toast.classList.add("visible");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove("visible"), 3200);
  }

  function adaptVisual(domainKey) {
    const selected = domainCopy[domainKey] || { label: "Investigación general", topics: ["Fuentes", "Contexto", "Contraste", "Límites"] };
    const center = document.querySelector(".topic-center strong");
    center.textContent = selected.label;
    center.style.fontSize = selected.label.length > 15 ? "11px" : "";
    document.querySelectorAll(".topic-node strong").forEach((node, index) => {
      node.textContent = selected.topics[index];
    });
  }

  function makeSourceCard(source, index) {
    const item = document.createElement("article");
    item.className = "source-result";

    const number = document.createElement("span");
    number.className = "finding-number";
    number.textContent = String(index + 1).padStart(2, "0");

    const body = document.createElement("div");
    body.className = "source-result-copy";

    const title = document.createElement("a");
    title.className = "source-result-title";
    title.href = source.url;
    title.target = "_blank";
    title.rel = "noopener noreferrer";
    title.textContent = source.title || "Fuente sin título";

    const meta = document.createElement("div");
    meta.className = "source-result-meta";
    meta.textContent = source.domain || "Dominio de origen";

    const description = document.createElement("p");
    description.className = "source-result-description";
    description.textContent = source.description || "El proveedor no devolvió una descripción para esta página.";

    body.append(title, meta, description);
    item.append(number, body);
    return item;
  }

  function renderSources(data) {
    resultTitle.textContent = question.value.trim();
    const count = Number.isInteger(data.result_count) ? data.result_count : 0;
    const retrieved = data.retrieved_at ? new Date(data.retrieved_at) : null;
    const dateLabel = retrieved && !Number.isNaN(retrieved.valueOf())
      ? retrieved.toLocaleString()
      : "fecha no disponible";
    summaryText.textContent = count
      ? "La búsqueda web recuperó " + count + " resultados para esta consulta. Los enlaces provienen del proveedor configurado; su presencia no implica que cada fuente sea fiable ni que sus afirmaciones estén verificadas. No se generó una síntesis automática."
      : "La búsqueda se completó, pero el proveedor no devolvió resultados utilizables. Probá reformular la consulta.";
    const heading = document.querySelector(".summary-card .card-kicker");
    heading.textContent = "BÚSQUEDA COMPLETADA · " + dateLabel;
    findingsTitle.textContent = "Fuentes recuperadas (" + count + ")";
    findingList.replaceChildren();
    if (count) {
      data.results.forEach((source, index) => findingList.append(makeSourceCard(source, index)));
    } else {
      const empty = document.createElement("p");
      empty.className = "empty-state";
      empty.textContent = "No se encontraron resultados válidos. No se inventaron fuentes.";
      findingList.append(empty);
    }
    results.setAttribute("aria-busy", "false");
    adaptVisual(domain.value);
  }

  function renderError(message) {
    resultTitle.textContent = "No se pudo completar la búsqueda";
    summaryText.textContent = message;
    document.querySelector(".summary-card .card-kicker").textContent = "BÚSQUEDA NO COMPLETADA";
    results.setAttribute("aria-busy", "false");
    showToast(message);
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = question.value.trim();
    const token = accessToken.value.trim();
    if (query.length < 3) {
      question.focus();
      showToast("Escribí una pregunta de al menos 3 caracteres.");
      return;
    }
    if (containsLikelyPersonalSensitiveData(query)) {
      renderError("La pregunta parece incluir datos personales o una situación sensible. Por prevención, no se envió a la API ni al proveedor externo. Reformulala sin datos identificables.");
      question.focus();
      return;
    }
    if (!token) {
      accessToken.focus();
      showToast("Ingresá un token autorizado. No se guarda en el navegador.");
      return;
    }

    const submit = form.querySelector('button[type="submit"]');
    submit.disabled = true;
    submit.textContent = "Buscando…";
    results.setAttribute("aria-busy", "true");
    resultTitle.textContent = "Buscando fuentes…";
    summaryText.textContent = "La consulta se enviará al proveedor configurado después de pasar la autenticación y los controles de privacidad.";
    document.querySelector(".summary-card .card-kicker").textContent = "CONSULTANDO";

    try {
      const response = await fetch("/v1/research", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ query, count: 5, domain: domain.value, confirm_public_query: publicConfirmation.checked })
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        const messages = {
          401: "El token no es válido o venció.",
          403: "Tu rol no tiene permiso para investigar.",
          423: "La consulta activó el control preventivo de privacidad. No la enviaremos al proveedor.",
          502: "El proveedor de búsqueda no está disponible. Probá más tarde.",
          503: "La búsqueda no está configurada o el servicio no está listo. Revisá la configuración del servidor."
        };
        throw new Error(messages[response.status] || "La búsqueda no se completó. Código HTTP " + response.status + ".");
      }
      if (payload.status !== "completed" || !Array.isArray(payload.results)) {
        throw new Error("El servicio devolvió una respuesta inesperada; no se mostrarán resultados como verificados.");
      }
      renderSources(payload);
      showToast("Búsqueda completada. Revisá cada fuente antes de usar sus afirmaciones.");
    } catch (error) {
      renderError(error instanceof TypeError
        ? "No se pudo conectar con la API de investigación. Comprobá que la interfaz esté abierta desde el servidor XIL-AC."
        : error.message || "Ocurrió un error inesperado.");
    } finally {
      submit.disabled = false;
      submit.innerHTML = 'Explorar <span aria-hidden="true">↗</span>';
    }
  });

  document.querySelectorAll("[data-prompt]").forEach((button) => {
    button.addEventListener("click", () => {
      question.value = button.dataset.prompt;
      question.focus();
    });
  });

  domain.addEventListener("change", () => adaptVisual(domain.value));

  document.querySelector("#newResearch").addEventListener("click", () => {
    question.value = "";
    publicConfirmation.checked = false;
    resultTitle.textContent = "Preparado para investigar";
    summaryText.textContent = "Ingresá tu pregunta y un token autorizado. La búsqueda consultará el proveedor configurado y mostrará enlaces reales. La síntesis automática aún no está conectada.";
    document.querySelector(".summary-card .card-kicker").textContent = "ESTADO DE LA INVESTIGACIÓN";
    findingList.replaceChildren();
    findingsTitle.textContent = "Fuentes recuperadas";
    question.focus();
    window.scrollTo({
      top: 0,
      behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth"
    });
  });

  document.querySelector("#copySummary").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(question.value.trim());
      showToast("Pregunta copiada.");
    } catch {
      question.focus();
      question.select();
      showToast("Seleccionamos la pregunta: copiala desde el campo.");
    }
  });

  adaptVisual(domain.value);
})();