(() => {
  "use strict";
  const form = document.querySelector("#researchForm");
  const question = document.querySelector("#researchQuestion");
  const domain = document.querySelector("#domain");
  const resultTitle = document.querySelector("#resultTitle");
  const summaryText = document.querySelector("#summaryText");
  const results = document.querySelector("#results");
  const toast = document.querySelector("#toast");
  let toastTimer;

  const domainCopy = {
    science: { label: "Ciencia y salud", summary: "Una investigación científica sólida distingue los resultados observados, la calidad de los estudios, las explicaciones posibles y aquello que todavía no se sabe. Esta pantalla es una demostración visual: no contiene una investigación ejecutada ni fuentes verificadas.", topics: ["Evidencia", "Mecanismos", "Estudios", "Incertidumbre"] },
    history: { label: "Historia y cultura", summary: "Una investigación histórica compara fuentes, sitúa los acontecimientos en su contexto y distingue los documentos contemporáneos de las interpretaciones posteriores. Esta pantalla es una demostración visual, no una investigación histórica ejecutada.", topics: ["Cronología", "Fuentes", "Contexto", "Interpretaciones"] },
    technology: { label: "Tecnología", summary: "Una comparación tecnológica debe hacer explícitos los criterios, las capacidades, las dependencias, los riesgos y los límites de cada opción. Esta pantalla es una demostración visual: no contiene una evaluación técnica verificada.", topics: ["Arquitectura", "Capacidades", "Riesgos", "Alternativas"] },
    business: { label: "Negocios y estrategia", summary: "Un análisis estratégico compara alternativas según objetivos, recursos, supuestos, riesgos e indicadores de resultado. Esta pantalla es una demostración visual, no una recomendación basada en datos reales.", topics: ["Objetivos", "Opciones", "Riesgos", "Resultados"] },
    education: { label: "Educación y conceptos", summary: "Una exploración conceptual organiza las ideas principales, muestra sus relaciones y las acompaña con ejemplos que permitan comprobar la comprensión. Esta pantalla es una demostración visual, no un material didáctico investigado.", topics: ["Conceptos", "Relaciones", "Ejemplos", "Aplicación"] },
    cfe: { label: "Desarrollo personal y CFE", summary: "Una exploración personal puede comparar perspectivas, proponer preguntas y distinguir metáforas de afirmaciones verificables. Las interpretaciones no deben presentarse como causas demostradas sin evidencia. Esta pantalla es una demostración visual.", topics: ["Experiencia", "Perspectivas", "Preguntas", "Aplicación"] }
  };

  function showToast(message) {
    toast.textContent = message;
    toast.classList.add("visible");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove("visible"), 2400);
  }

  function renderDemo() {
    const prompt = question.value.trim();
    if (!prompt) {
      question.focus();
      showToast("Escribí una pregunta para continuar.");
      return;
    }
    const selected = domainCopy[domain.value] || domainCopy.science;
    resultTitle.textContent = prompt.length > 68 ? prompt.slice(0, 65) + "…" : prompt;
    summaryText.textContent = selected.summary;
    const center = document.querySelector(".topic-center strong");
    center.textContent = selected.label;
    center.style.fontSize = selected.label.length > 15 ? "12px" : "";
    document.querySelectorAll(".topic-node strong").forEach((node, index) => {
      node.textContent = selected.topics[index];
    });
    results.setAttribute("aria-busy", "false");
    results.classList.remove("updated");
    void results.offsetWidth;
    results.classList.add("updated");
    showToast("Vista de demostración adaptada. No se ejecutó una investigación real.");
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    renderDemo();
  });

  document.querySelectorAll("[data-prompt]").forEach((button) => {
    button.addEventListener("click", () => {
      question.value = button.dataset.prompt;
      question.focus();
    });
  });

  document.querySelectorAll(".finding").forEach((button) => {
    button.addEventListener("click", () => {
      const expanded = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", String(!expanded));
    });
  });

  document.querySelector("#newResearch").addEventListener("click", () => {
    question.value = "";
    question.focus();
    window.scrollTo({ top: 0, behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
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
})();
