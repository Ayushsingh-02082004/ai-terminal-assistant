/* ==========================================================================
   CLI AGENT - FRONTEND INTERACTIVE LOGIC
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  initLiveTerminalDemo();
  initOsTabs();
  initPromptFilters();
  initCopyButtons();
});

/* --------------------------------------------------------------------------
   1. LIVE TERMINAL MOCKUP SIMULATION
   -------------------------------------------------------------------------- */
function initLiveTerminalDemo() {
  const terminalBody = document.getElementById("terminal-live-body");
  if (!terminalBody) return;

  const scenarios = [
    {
      prompt: "check git status and summarize last 3 commits",
      router: "[Router Agent]: Identified intent [Git Operations] ➔ Executing git status & git log",
      output: "On branch main\nYour branch is up to date with 'origin/main'.\n\nRecent Commits:\n- 7b274d3 merge: resolve merge conflicts and integrate all guardrails into main\n- a608cbc fix: add deep path inspector & 200KB read limit\n- 4abab49 fix: relax max_execution_time to 300s"
    },
    {
      prompt: "check syntax of backend/src/cli_agent/crew.py",
      router: "[Router Agent]: Identified intent [Code Operations] ➔ Validating AST bytecode syntax",
      output: "Syntax check passed: 'backend/src/cli_agent/crew.py' compiled with 0 errors."
    },
    {
      prompt: "read file venv/lib/python3.11/site-packages/pip/__init__.py",
      router: "[Router Agent]: Identified intent [File Operations] ➔ Executing deep path check",
      output: "Skipping this dependency file or directory."
    }
  ];

  let currentIdx = 0;

  async function runDemoCycle() {
    const sc = scenarios[currentIdx];
    terminalBody.innerHTML = "";

    // 1. Render User Input Line with Typing Effect
    const userLine = document.createElement("div");
    userLine.className = "term-line";
    userLine.innerHTML = `<span class="term-prompt">User &gt;</span> <span id="typed-text"></span><span class="typing-cursor"></span>`;
    terminalBody.appendChild(userLine);

    const typedSpan = document.getElementById("typed-text");
    for (let i = 0; i < sc.prompt.length; i++) {
      typedSpan.textContent += sc.prompt[i];
      await sleep(40);
    }
    await sleep(400);

    // Remove typing cursor from prompt line
    const cursor = userLine.querySelector(".typing-cursor");
    if (cursor) cursor.remove();

    // 2. Render Router Output
    const routerDiv = document.createElement("div");
    routerDiv.className = "term-router";
    routerDiv.textContent = sc.router;
    terminalBody.appendChild(routerDiv);
    await sleep(600);

    // 3. Render Execution Result Card
    const outDiv = document.createElement("div");
    outDiv.className = "term-output";
    outDiv.innerHTML = sc.output.replace(/\n/g, "<br>");
    terminalBody.appendChild(outDiv);

    // Prepare next scenario
    currentIdx = (currentIdx + 1) % scenarios.length;
    await sleep(4500);
    runDemoCycle();
  }

  runDemoCycle();
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/* --------------------------------------------------------------------------
   2. OS INSTALLATION TABS SWITCHER
   -------------------------------------------------------------------------- */
function initOsTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetOs = btn.getAttribute("data-os");

      tabBtns.forEach((b) => b.classList.remove("active"));
      tabContents.forEach((c) => c.classList.remove("active"));

      btn.classList.add("active");
      const activeContent = document.getElementById(`tab-${targetOs}`);
      if (activeContent) activeContent.classList.add("active");
    });
  });
}

/* --------------------------------------------------------------------------
   3. PROMPT CATEGORY FILTER
   -------------------------------------------------------------------------- */
function initPromptFilters() {
  const filterBtns = document.querySelectorAll(".filter-btn");
  const promptCards = document.querySelectorAll(".prompt-card");

  filterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const cat = btn.getAttribute("data-cat");

      filterBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      promptCards.forEach((card) => {
        if (cat === "all" || card.getAttribute("data-cat") === cat) {
          card.style.display = "block";
        } else {
          card.style.display = "none";
        }
      });
    });
  });
}

/* --------------------------------------------------------------------------
   4. COPY-TO-CLIPBOARD WITH TOAST FEEDBACK
   -------------------------------------------------------------------------- */
function initCopyButtons() {
  const copyBtns = document.querySelectorAll(".btn-copy");
  const toast = document.getElementById("toast-notification");

  copyBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const textToCopy = btn.getAttribute("data-copy");
      if (!textToCopy) return;

      navigator.clipboard.writeText(textToCopy).then(() => {
        showToast("Copied command to clipboard!");
      }).catch(() => {
        // Fallback for older browsers
        const temp = document.createElement("textarea");
        temp.value = textToCopy;
        document.body.appendChild(temp);
        temp.select();
        document.execCommand("copy");
        document.body.removeChild(temp);
        showToast("Copied command to clipboard!");
      });
    });
  });

  function showToast(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("show");
    setTimeout(() => {
      toast.classList.remove("show");
    }, 2500);
  }
}
