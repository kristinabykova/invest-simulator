import { state } from "./state.js";
import {
  periodSelect,
  wfCalcBtn,
  registerOpenBtn,
  loginOpenBtn,
  logoutBtn,
  registerModal,
  loginModal,
  registerCloseBtn,
  loginCloseBtn,
  registerSubmitBtn,
  loginSubmitBtn,
  buyBtn,
  sellBtn,
} from "./dom.js";
import { apiGetJson, apiPostJson } from "./api.js";
import { registerUser, loginUser, logoutUser } from "./auth.js";
import { openModal, closeModal } from "./utils.js";
import { renderStocksList, loadChart } from "./stocks.js";
import { setCalcEnabled, renderWhatIf, renderAI, renderExplanations } from "./whatif.js";
import { refreshPortfolioUI, buySelectedStock, sellSelectedStock } from "./portfolio.js";

async function init() {
  try {
    const stocks = await apiGetJson("/stocks/");
    renderStocksList(stocks);
  } catch (err) {
    console.error("Ошибка загрузки акций:", err);
  }

  await refreshPortfolioUI();

  if (periodSelect) {
    periodSelect.addEventListener("change", () => {
      state.currentDays = Number(periodSelect.value);
      if (state.currentStock) loadChart(state.currentStock);
    });
  }

  if (wfCalcBtn) {
    wfCalcBtn.addEventListener("click", async () => {
      if (!state.currentStock || !state.wfFrom || !state.wfTo) return;

      const payload = {
        ticker: state.currentStock.ticker,
        from_: state.wfFrom,
        to: state.wfTo,
        interval: 10,
        lots_count: Number(document.getElementById("whatIfLot").value)
      };

      try {
        const data = await apiPostJson("/analyze/", payload);
        renderWhatIf(data);

        apiPostJson("/analyze/ai", payload)
          .then(aiData => {
            if (aiData) {
              renderAI(aiData);
            } else {
              renderExplanations(data.explanations);
              document.getElementById("aiHeader").style.display = "block";
              document.getElementById("aiWarning").style.display = "none";
            }
          })
          .catch(err => {
            console.error("AI ошибка:", err);
          });

      } catch (e) {
        console.error("Ошибка what-if:", e);
      }
    });
  }

  setCalcEnabled();

  if (registerOpenBtn) {
    registerOpenBtn.addEventListener("click", () => openModal(registerModal));
  }

  if (loginOpenBtn) {
    loginOpenBtn.addEventListener("click", () => openModal(loginModal));
  }

  if (registerCloseBtn) {
    registerCloseBtn.addEventListener("click", () => closeModal(registerModal));
  }

  if (loginCloseBtn) {
    loginCloseBtn.addEventListener("click", () => closeModal(loginModal));
  }

  if (registerSubmitBtn) {
    registerSubmitBtn.addEventListener("click", async () => {
      const ok = await registerUser();
      if (ok) {
        await refreshPortfolioUI();
      }
    });
  }

  if (loginSubmitBtn) {
    loginSubmitBtn.addEventListener("click", async () => {
      const ok = await loginUser();
      if (ok) {
        await refreshPortfolioUI();
      }
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
      const ok = await logoutUser();
      if (ok) {
        await refreshPortfolioUI();
      }
    });
  }

  if (buyBtn) {
    buyBtn.addEventListener("click", buySelectedStock);
  }

  if (sellBtn) {
    sellBtn.addEventListener("click", sellSelectedStock);
  }

  if (registerModal) {
    registerModal.addEventListener("click", (e) => {
      if (e.target === registerModal) closeModal(registerModal);
    });
  }

  if (loginModal) {
    loginModal.addEventListener("click", (e) => {
      if (e.target === loginModal) closeModal(loginModal);
    });
  }
}

init();