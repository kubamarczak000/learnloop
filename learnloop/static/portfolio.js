(() => {
  const h = React.createElement;
  const query = `query PersonalPortfolio { portfolio { headline intro skills contact { github linkedin } projects { name description category stack demoUrl sourceUrl screenshotUrl status featured } } }`;

  function ProjectCard({ project, index }) {
    if (project.status === "building") {
      return h("article", { className: "project-card building-card" },
        h("div", { className: "building-status" }, h("span", null, "◌"), "W budowie"),
        h("h3", null, project.name),
        h("div", { className: "project-tags" }, project.stack.map((tech) => h("span", { key: tech }, tech)))
      );
    }

    return h("article", { className: `project-card${project.featured ? " project-featured" : ""}` },
      h("div", { className: "project-art" },
        h("img", { className: "project-screenshot", src: project.screenshotUrl, alt: `Zrzut ekranu aplikacji ${project.name}` }),
        h("span", { className: "screenshot-email-cover", "aria-hidden": "true" })
      ),
      h("div", { className: "project-card-body" },
        h("div", { className: "project-card-overline" }, h("span", null, project.category), h("span", null, "2026")),
        h("h3", null, project.name),
        h("p", null, project.description),
        h("div", { className: "project-tags" }, project.stack.map((tech) => h("span", { key: tech }, tech))),
        h("div", { className: "project-links" },
          h("a", { href: project.demoUrl, target: "_blank", rel: "noreferrer" }, "Otwórz aplikację", h("span", null, "↗")),
          h("a", { href: project.sourceUrl, target: "_blank", rel: "noreferrer" }, "Kod źródłowy", h("span", null, "↗"))
        )
      )
    );
  }

  function Portfolio() {
    const [portfolio, setPortfolio] = React.useState(null);
    const [loadError, setLoadError] = React.useState(false);
    React.useEffect(() => {
      fetch("/api/graphql", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query }) })
        .then((response) => { if (!response.ok) throw new Error("API error"); return response.json(); })
        .then((result) => { if (!result.data?.portfolio) throw new Error("Missing portfolio data"); setPortfolio(result.data.portfolio); })
        .catch(() => setLoadError(true));
    }, []);

    const skills = portfolio?.skills || ["Python", "Flask", "GraphQL", "React", "Bootstrap", "SQLite", "Git"];
    const projects = portfolio?.projects || [];
    const contact = portfolio?.contact || {
      github: "https://github.com/kubamarczak000",
      linkedin: "https://www.linkedin.com/in/jakub-marczak-b28aa33b7/",
    };

    return h(React.Fragment, null,
      h("nav", { className: "navbar portfolio-nav" }, h("div", { className: "container nav-inner" },
        h("a", { className: "personal-brand", href: "#start" }, h("span", { className: "monogram" }, "</>"), "Portfolio"),
        h("div", { className: "nav-links" }, h("a", { href: "#projekty" }, "Projekty"), h("a", { href: "#omnie" }, "O mnie"), h("a", { href: "#technologie" }, "Technologie")),
        h("a", { className: "nav-cta", href: "#kontakt" }, "Kontakt ↗"))),
      h("main", { id: "start" },
        h("section", { className: "hero-section" }, h("div", { className: "container hero-grid" },
          h("div", { className: "hero-copy" },
            h("div", { className: "hero-kicker" }, h("span", null), "PORTFOLIO · PYTHON DEVELOPER"),
            h("h1", null, portfolio?.headline || "Aplikacje webowe tworzone w Pythonie."),
            h("p", { className: "hero-desc" }, portfolio?.intro || "Jestem na początku swojej drogi jako programista. Buduję praktyczne projekty, uczę się nowych technologii i pokazuję tutaj efekty tej pracy."),
            h("div", { className: "hero-actions" }, h("a", { className: "button-primary", href: "#projekty" }, "Zobacz moje projekty", h("span", null, "↓")), h("a", { className: "button-text", href: "#omnie" }, "Poznaj mnie bliżej ↘")),
            h("div", { className: "hero-note" }, h("span", null, "✳"), " Nowe projekty i eksperymenty będą pojawiać się właśnie tutaj.")),
          h("div", { className: "hero-visual" },
            h("div", { className: "code-card" },
              h("div", { className: "code-card-top" }, h("div", { className: "window-dots" }, h("i"), h("i"), h("i")), h("span", null, "hello.py"), h("span", null, "⌘")),
              h("div", { className: "code-body" },
                h("div", null, h("span", { className: "code-number" }, "01"), h("span", { className: "code-purple" }, "class"), " Portfolio:"),
                h("div", null, h("span", { className: "code-number" }, "02"), "  role = ", h("span", { className: "code-green" }, `"Python developer"`)),
                h("div", null, h("span", { className: "code-number" }, "03"), "  focus = ["),
                h("div", null, h("span", { className: "code-number" }, "04"), "    ", h("span", { className: "code-orange" }, "'Python'"), ","),
                h("div", null, h("span", { className: "code-number" }, "05"), "    ", h("span", { className: "code-orange" }, "'Web apps'"), ","),
                h("div", null, h("span", { className: "code-number" }, "06"), "  ]"),
                h("div", null, h("span", { className: "code-number" }, "07"), "  status = ", h("span", { className: "code-green" }, "'building'"))
              ),
              h("div", { className: "code-card-bottom" }, h("span", null, "●"), " Python 3.11+", h("span", null, "UTF-8"))
            ),
            h("div", { className: "orbit orbit-one" }), h("div", { className: "orbit orbit-two" }),
            h("div", { className: "floating-badge" }, h("span", null, "✦"), h("div", null, h("strong", null, "Zawsze w budowie"), h("small", null, "Uczę się, tworzę, poprawiam")))
          )
        )),
        h("section", { className: "projects-section container", id: "projekty" },
          h("div", { className: "section-heading" }, h("div", null, h("div", { className: "section-label" }, "01 / WYBRANE PRACE"), h("h2", null, "Projekty")), h("p", null, "Aplikacje i pomysły, nad którymi pracuję.")),
          loadError ? h("p", { className: "load-error" }, "Nie udało się pobrać listy projektów. Odśwież stronę, aby spróbować ponownie.") : projects.length ? h("div", { className: "projects-grid" }, projects.map((project, index) => h(ProjectCard, { project, index, key: project.name }))) : h("div", { className: "project-loading" }, "Ładowanie projektów…"),
          h("div", { className: "add-more-note" }, h("span", null, "+"), h("p", null, "To portfolio będzie rosło razem z kolejnymi projektami.", h("br"), h("small", null, "Następne realizacje pojawią się tutaj.")))
        ),
        h("section", { className: "about-section", id: "omnie" }, h("div", { className: "container about-inner" },
          h("div", null, h("div", { className: "section-label" }, "02 / O MNIE"), h("h2", null, "Rozwijam się, budując rzeczy, których sam chcę używać.")),
          h("div", null, h("p", null, "Najwięcej uczę się w praktyce — planuję funkcję, buduję ją, a potem sprawdzam, co można zrobić lepiej. Interesuje mnie tworzenie aplikacji webowych od strony serwera i interfejsu."), h("p", null, "To portfolio jest miejscem na moje aktualne projekty, eksperymenty i kolejne kroki w nauce programowania."))
        )),
        h("section", { className: "skills-section container", id: "technologie" },
          h("div", { className: "section-label" }, "03 / NARZĘDZIA"), h("div", { className: "skills-heading" }, h("h2", null, "Technologie, z którymi pracuję."), h("p", null, "Stosuję je w projektach i rozwijam swoje umiejętności.")),
          h("div", { className: "skills-grid" }, skills.map((skill, index) => h("div", { className: "skill-pill", key: skill }, h("span", null, `0${index + 1}`), h("strong", null, skill), h("span", { className: "skill-star" }, "↗")))
        ),
        h("section", { className: "contact-section container", id: "kontakt" }, h("div", { className: "contact-card" },
          h("div", null, h("div", { className: "section-label" }, "04 / KONTAKT"), h("h2", null, "Znajdź mnie w sieci."), h("p", null, "Zobacz moje projekty i odezwij się przez wybrany profil.")),
          h("div", { className: "contact-links" },
            h("a", { className: "contact-link", href: contact.github, target: "_blank", rel: "noreferrer" }, h("span", { className: "contact-icon" }, "GH"), "GitHub", h("span", { className: "contact-arrow" }, "↗")),
            h("a", { className: "contact-link", href: contact.linkedin, target: "_blank", rel: "noreferrer" }, h("span", { className: "contact-icon" }, "in"), "LinkedIn", h("span", { className: "contact-arrow" }, "↗"))
          )
        )))
      ),
      h("footer", { className: "portfolio-footer container" }, h("a", { className: "personal-brand", href: "#start" }, h("span", { className: "monogram" }, "</>"), "Portfolio"), h("span", null, "Aktualizowane wraz z nowymi projektami"), h("a", { href: "#start" }, "Na górę ↑"))
    );
  }

  ReactDOM.createRoot(document.getElementById("portfolio-root")).render(h(Portfolio));
})();
