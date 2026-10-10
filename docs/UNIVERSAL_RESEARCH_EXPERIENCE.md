# Universal Research Experience — XIL-AC

**Status:** interactive static prototype implemented; production integration and browser-level verification pending  
**Scope:** every user-facing research task, regardless of domain.  
**Applies to:** the shared research interface and presentation layer, not only Constelaciones Familiares y Existenciales (CFE).

## Product principle

**High internal capability, low external complexity.** Research should feel clear, fast, visually considered, and easy to navigate on mobile. The interface approved by the product owner in ChatGPT's research response is the quality reference: clear hierarchy, relevant imagery, concise synthesis, useful visual structure, and deeper detail available without overwhelming the first view.

This document defines the target experience. It does not claim that a production frontend already exists or that these requirements have been implemented.

## 1. Universal research shell

Every research result uses the same core information architecture:

1. **Research question and scope** — what is being investigated, with the user's intended scope preserved.
2. **Executive synthesis** — the most useful answer first, concise and independently understandable.
3. **Visual overview** — choose the most informative representation for the topic: relevant images, comparison table, timeline, process diagram, map, chart, taxonomy, or conceptual model. Do not add visuals merely for decoration.
4. **Main findings** — grouped into short, scannable sections with descriptive headings.
5. **Evidence and uncertainty** — distinguish verified information, interpretation, hypothesis, disagreement, unknowns, and limitations.
6. **Sources and traceability** — visible citations close to the claims they support; source list and research date when relevant.
7. **Practical implications** — next steps, applications, or decisions only where appropriate to the user's request.
8. **Further exploration** — optional deeper sections, questions, methods, or alternate views without crowding the first screen.

## 2. Visual design system

- Responsive and mobile-first; comfortable reading on a phone.
- Consistent spacing, alignment, typography hierarchy, and restrained color.
- Cards and panels only when they clarify grouping or comparison; avoid excessive containers.
- Images must be relevant, informative, and appropriately captioned; avoid generic stock imagery and repeated visuals.
- Use diagrams, charts, tables, and timelines when they communicate better than prose. Every visualization must have a clear purpose and a textual equivalent where needed.
- Keep headings and metadata compact; use short paragraphs, lists, and progressive disclosure for depth.
- Provide useful empty, loading, error, and partial-result states.
- Support keyboard navigation, screen readers, sufficient contrast, readable type, and reduced-motion preferences.
- Avoid unnecessary animation, visual noise, decorative badges, and large full-width imagery when a compact layout is clearer.

## 3. Research-adaptive presentation

The shared shell stays consistent; the visual components adapt to the subject and task.

| Research type | Preferred visual structures when useful |
|---|---|
| Scientific / medical | evidence summary, mechanism diagram, study comparison, uncertainty and safety notes |
| Historical / cultural | timeline, chronology, maps, source comparison |
| Product / technology | feature comparison, architecture diagram, decision matrix |
| Social / political / current affairs | dated timeline, stakeholder map, claims-versus-evidence comparison |
| Business / strategy | options matrix, process map, assumptions and risks |
| Education / conceptual | concept map, worked example, learning sequence |
| Local / travel | map and route where location is central |
| CFE / personal development | conceptual map, reflective questions, application examples, explicit separation of metaphor from evidence |

These are defaults, not rigid templates. Select visuals based on the research question and available evidence; do not force a chart, image, or diagram into every answer.

## 4. Evidence integrity and safety

- Never make visual polish imply stronger evidence than the sources support.
- Label fact, interpretation, hypothesis, and speculation in plain language.
- Preserve meaningful disagreements and unknowns instead of manufacturing consensus.
- Cite source-derived claims; show dates for time-sensitive findings.
- In medical, legal, financial, and other high-impact domains, make limitations and appropriate professional guidance easy to find.
- Do not present symbolic, spiritual, or personal-development frameworks as scientifically established causal models unless evidence supports that claim.
- Images and diagrams must not distort source findings or be presented as clinical/technical proof.

## 5. Interaction and performance

- The first screen should answer “What did we find?” before asking the user to navigate.
- Allow deeper sections to expand progressively; preserve the user's place when possible.
- Keep controls purposeful: source details, compare views, methodology, glossary, and next-step actions only when relevant.
- Stream or progressively reveal results when supported, while clearly marking incomplete sections.
- Avoid duplicate summaries, repeated citations, and redundant cards.
- Preserve a clean reading experience on narrow screens and low-bandwidth connections.

## 6. Architecture requirements

- Implement the research shell as a shared, domain-agnostic presentation layer.
- Keep domain-specific research logic, source retrieval, evidence evaluation, and safety rules outside the visual component where possible.
- Define a stable research-result contract so different research agents can render through the same shell.
- Keep source metadata and evidence labels structured, not inferred from styling.
- Preserve XIL-AC governance: human control, traceability, uncertainty, permission boundaries, and fail-safe behavior.
- Keep STANDARD / CREATOR / EXPERIMENTAL boundaries intact; do not let visual presentation silently promote experimental hypotheses into trusted knowledge.

## 7. Acceptance criteria

The feature is not complete until all of the following are demonstrated:

- [ ] The same research shell renders results from at least three unrelated domains.
- [ ] Domain-specific visuals change appropriately without changing the core navigation and hierarchy.
- [ ] Mobile layouts are usable without horizontal scrolling for ordinary text and tables.
- [ ] Citations remain adjacent to supported claims and open the correct source.
- [ ] Evidence status, uncertainty, and conflicting findings remain visible.
- [ ] Missing images or chart data do not break the result.
- [ ] Loading, partial, empty, and error states are tested.
- [ ] Accessibility checks cover keyboard operation, contrast, headings, and alternative text.
- [ ] Tests confirm the visual layer does not modify research claims or evidence labels.
- [ ] The UI is documented as implemented only after code, tests, and a working preview have been verified.

## 8. Delivery sequence

1. Audit the current frontend and research-result data contract.
2. Define the shared research-result schema and visual tokens.
3. Build the universal research shell and reusable components.
4. Add domain-adaptive visual selection with safe fallbacks.
5. Test representative topics, mobile layouts, accessibility, evidence integrity, and failure states.
6. Integrate through the existing review and Production Gate process.

**Definition of done:** one coherent, polished research experience across all topics, with adaptable visuals and consistent evidence standards—not a CFE-only screen and not a static mockup presented as a working product.
