const themeToggle = document.querySelector("#theme-toggle");
const themeIcon = themeToggle.querySelector(".theme-toggle-icon");
const themeLabel = themeToggle.querySelector(".theme-toggle-label");
const themeColor = document.querySelector('meta[name="theme-color"]');
const tabs = Array.from(document.querySelectorAll('[role="tab"]'));

function updateThemeButton(isNight) {
  themeToggle.setAttribute("aria-pressed", String(isNight));
  themeToggle.setAttribute(
    "aria-label",
    isNight ? "Zum Tagesmodus wechseln" : "Zum Nachtmodus wechseln"
  );
  themeIcon.textContent = isNight ? "☀" : "☾";
  themeLabel.textContent = isNight ? "Tagesmodus" : "Nachtmodus";
  themeColor.setAttribute("content", isNight ? "#111815" : "#f5f4ef");
}

updateThemeButton(getComputedStyle(document.documentElement).colorScheme === "dark");

themeToggle.addEventListener("click", () => {
  const isNight = themeToggle.getAttribute("aria-pressed") !== "true";
  document.documentElement.dataset.theme = isNight ? "night" : "light";
  updateThemeButton(isNight);
});

function activateTab(selectedTab, moveFocus = false) {
  tabs.forEach((tab) => {
    const isSelected = tab === selectedTab;
    const panel = document.getElementById(tab.getAttribute("aria-controls"));

    tab.classList.toggle("is-active", isSelected);
    tab.setAttribute("aria-selected", String(isSelected));
    tab.tabIndex = isSelected ? 0 : -1;
    panel.hidden = !isSelected;
    panel.classList.toggle("is-active", isSelected);
  });

  if (moveFocus) {
    selectedTab.focus();
  }
}

tabs.forEach((tab, index) => {
  tab.addEventListener("click", () => activateTab(tab));
  tab.addEventListener("keydown", (event) => {
    let nextIndex;

    switch (event.key) {
      case "ArrowRight":
        nextIndex = (index + 1) % tabs.length;
        break;
      case "ArrowLeft":
        nextIndex = (index - 1 + tabs.length) % tabs.length;
        break;
      case "Home":
        nextIndex = 0;
        break;
      case "End":
        nextIndex = tabs.length - 1;
        break;
      default:
        return;
    }

    event.preventDefault();
    activateTab(tabs[nextIndex], true);
  });
});

async function loadNews() {
  const newsList = document.querySelector("#news-list");

  try {
    const response = await fetch(new URL("news.json", document.baseURI));
    if (!response.ok) {
      throw new Error(`news.json konnte nicht geladen werden (HTTP ${response.status}).`);
    }

    const data = await response.json();
    if (!Array.isArray(data.news)) {
      throw new Error("Das Feld \"news\" in news.json muss eine Liste sein.");
    }

    const articles = data.news.map((item, index) => {
      if (
        !item ||
        typeof item.date !== "string" ||
        typeof item.category !== "string" ||
        typeof item.title !== "string" ||
        typeof item.description !== "string" ||
        !item.date.trim() ||
        !item.category.trim() ||
        !item.title.trim() ||
        !item.description.trim()
      ) {
        throw new Error(`News-Eintrag ${index + 1} hat fehlende oder ungültige Felder.`);
      }

      const article = document.createElement("article");
      article.className = "news-card";

      const date = document.createElement("p");
      date.className = "news-date";
      date.textContent = `${item.date} · ${item.category}`;

      const title = document.createElement("h3");
      title.textContent = item.title;

      const description = document.createElement("p");
      description.textContent = item.description;

      article.append(date, title, description);
      return article;
    });

    newsList.replaceChildren(...articles);
    if (articles.length === 0) {
      const emptyMessage = document.createElement("p");
      emptyMessage.className = "news-status";
      emptyMessage.textContent = "Aktuell gibt es keine News.";
      newsList.append(emptyMessage);
    }
    newsList.setAttribute("aria-busy", "false");
  } catch (error) {
    console.error("Die News konnten nicht geladen werden:", error);
    newsList.replaceChildren();
    const errorMessage = document.createElement("p");
    errorMessage.className = "news-status";
    errorMessage.textContent =
      "Die News konnten nicht geladen werden. Bitte news.json prüfen und die Seite neu laden.";
    newsList.append(errorMessage);
    newsList.setAttribute("aria-busy", "false");
  }
}

loadNews();
activateTab(tabs[0]);
