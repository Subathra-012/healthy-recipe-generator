// ═══════════════════════════════════════════════════════════════
// ✨ NUTRIGEN AI — PREMIUM SaaS DASHBOARD ENGINE
// ═══════════════════════════════════════════════════════════════

console.log("🚀 NutriGen AI Dashboard v5.0 Loaded!");

// ── State ──
let chart = null;
let calorieChartInstance = null;
let macroChartInstance = null;
let proteinChart = null;
let currentRecipeData = null;
let currentPlanData = null;
let currentMode = null;

// ═══════════════════════════════════════════════════════════════
// 🏗️ INITIALIZATION
// ═══════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
  initTheme();
  initGreeting();
  initDashboardCharts();
  initMealPlanPreview();
  initRecentRecipes();
  initNotifications();
  initScrollAnimations();
  initLanguageListener();
  fetchHistoryData();
});

// ═══════════════════════════════════════════════════════════════
// 🗂️ SIDEBAR LOGIC
// ═══════════════════════════════════════════════════════════════

function initSidebar() {
  const collapsed = localStorage.getItem('sidebarCollapsed') === 'true';
  if (collapsed) document.body.classList.add('sidebar-collapsed');

  const toggle = document.getElementById('sidebarToggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      document.body.classList.toggle('sidebar-collapsed');
      localStorage.setItem('sidebarCollapsed', document.body.classList.contains('sidebar-collapsed'));
    });
  }
}

function toggleMobileSidebar() {
  document.body.classList.toggle('sidebar-open');
}

function closeMobileSidebar() {
  document.body.classList.remove('sidebar-open');
}

function toggleSidebar() {
  // Legacy support
  document.body.classList.toggle('sidebar-collapsed');
  localStorage.setItem('sidebarCollapsed', document.body.classList.contains('sidebar-collapsed'));
}

// ═══════════════════════════════════════════════════════════════
// 🎨 THEME (Dark / Light Mode)
// ═══════════════════════════════════════════════════════════════

function initTheme() {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light') {
    document.body.classList.add('light-mode');
    updateThemeIcon();
  }
}

function toggleTheme() {
  document.body.classList.toggle('light-mode');
  const isLight = document.body.classList.contains('light-mode');
  localStorage.setItem('theme', isLight ? 'light' : 'dark');
  updateThemeIcon();

  // Re-render charts with new colors
  if (calorieChartInstance) {
    calorieChartInstance.destroy();
    initCalorieChart();
  }
  if (macroChartInstance) {
    macroChartInstance.destroy();
    initMacroChart();
  }
}

function updateThemeIcon() {
  const icon = document.getElementById('themeIcon');
  if (icon) {
    const isLight = document.body.classList.contains('light-mode');
    icon.className = isLight ? 'fas fa-sun' : 'fas fa-moon';
  }
}

// ═══════════════════════════════════════════════════════════════
// 👋 GREETING & QUOTES
// ═══════════════════════════════════════════════════════════════

function initGreeting() {
  updateGreeting();
}

function updateGreeting() {
  const hour = new Date().getHours();
  let greeting = 'Good Evening';
  let emoji = '🌙';
  if (hour < 12) { greeting = 'Good Morning'; emoji = '☀️'; }
  else if (hour < 17) { greeting = 'Good Afternoon'; emoji = '🌤️'; }

  const el = document.getElementById('greetingMessage');
  if (el) el.textContent = `${greeting}, Chef! ${emoji}`;

  const quotes = [
    '"Let food be thy medicine and medicine be thy food." — Hippocrates',
    '"One cannot think well, love well, sleep well, if one has not dined well." — Virginia Woolf',
    '"The only time to eat diet food is while waiting for the steak to cook." — Julia Child',
    '"Cooking is like love. It should be entered into with abandon or not at all." — Harriet Van Horne',
    '"People who love to eat are always the best people." — Julia Child',
    '"Tell me what you eat, and I will tell you what you are." — Jean Anthelme Brillat-Savarin'
  ];
  const quoteEl = document.getElementById('dailyQuote');
  if (quoteEl) quoteEl.textContent = quotes[Math.floor(Math.random() * quotes.length)];
}

// ═══════════════════════════════════════════════════════════════
// 📊 DASHBOARD CHARTS
// ═══════════════════════════════════════════════════════════════

function initDashboardCharts() {
  initCalorieChart();
  initMacroChart();
}

function initCalorieChart() {
  const ctx = document.getElementById('calorieChart');
  if (!ctx) return;

  const isLight = document.body.classList.contains('light-mode');
  const consumed = 1450;
  const total = 2000;
  const remaining = total - consumed;

  calorieChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Consumed', 'Remaining'],
      datasets: [{
        data: [consumed, remaining],
        backgroundColor: [
          '#6366f1',
          isLight ? '#e2e8f0' : '#1e293b'
        ],
        borderWidth: 0,
        borderRadius: 6,
        spacing: 2,
      }]
    },
    options: {
      cutout: '78%',
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: isLight ? '#ffffff' : '#1e293b',
          titleColor: isLight ? '#0f172a' : '#f1f5f9',
          bodyColor: isLight ? '#475569' : '#94a3b8',
          borderColor: isLight ? '#e2e8f0' : '#334155',
          borderWidth: 1,
          cornerRadius: 8,
          padding: 12,
          callbacks: {
            label: ctx => `${ctx.label}: ${ctx.raw} kcal`
          }
        }
      },
      animation: {
        animateRotate: true,
        duration: 1200,
        easing: 'easeOutQuart'
      }
    }
  });
}

function initMacroChart() {
  const ctx = document.getElementById('macroChart');
  if (!ctx) return;

  const isLight = document.body.classList.contains('light-mode');

  macroChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Protein', 'Carbs', 'Fat', 'Fiber'],
      datasets: [{
        label: 'Current (g)',
        data: [82, 180, 55, 28],
        backgroundColor: [
          'rgba(99, 102, 241, 0.8)',
          'rgba(6, 182, 212, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(16, 185, 129, 0.8)'
        ],
        borderRadius: 8,
        borderSkipped: false,
        barThickness: 40,
      }, {
        label: 'Target (g)',
        data: [120, 250, 70, 35],
        backgroundColor: [
          'rgba(99, 102, 241, 0.15)',
          'rgba(6, 182, 212, 0.15)',
          'rgba(245, 158, 11, 0.15)',
          'rgba(16, 185, 129, 0.15)'
        ],
        borderRadius: 8,
        borderSkipped: false,
        barThickness: 40,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: {
          grid: {
            color: isLight ? 'rgba(0,0,0,0.06)' : 'rgba(255,255,255,0.04)',
            drawBorder: false,
          },
          ticks: {
            color: isLight ? '#64748b' : '#64748b',
            font: { size: 11 }
          }
        },
        y: {
          grid: { display: false },
          ticks: {
            color: isLight ? '#334155' : '#94a3b8',
            font: { size: 13, weight: '600' }
          }
        }
      },
      plugins: {
        legend: {
          position: 'top',
          align: 'end',
          labels: {
            color: isLight ? '#475569' : '#94a3b8',
            usePointStyle: true,
            pointStyle: 'rectRounded',
            padding: 16,
            font: { size: 11 }
          }
        },
        tooltip: {
          backgroundColor: isLight ? '#ffffff' : '#1e293b',
          titleColor: isLight ? '#0f172a' : '#f1f5f9',
          bodyColor: isLight ? '#475569' : '#94a3b8',
          borderColor: isLight ? '#e2e8f0' : '#334155',
          borderWidth: 1,
          cornerRadius: 8,
          padding: 12,
          callbacks: {
            label: ctx => `${ctx.dataset.label}: ${ctx.raw}g`
          }
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      }
    }
  });
}

// ═══════════════════════════════════════════════════════════════
// 📅 WEEKLY MEAL PLAN PREVIEW
// ═══════════════════════════════════════════════════════════════

function initMealPlanPreview() {
  const grid = document.getElementById('mealPlanGrid');
  if (!grid) return;

  const today = new Date().getDay(); // 0=Sun
  const meals = [
    { day: 'Sun', emoji: '🥞', name: 'Fluffy Pancakes', cal: 420 },
    { day: 'Mon', emoji: '🥗', name: 'Quinoa Bowl', cal: 385 },
    { day: 'Tue', emoji: '🍗', name: 'Grilled Chicken', cal: 520 },
    { day: 'Wed', emoji: '🍣', name: 'Salmon Sushi', cal: 440 },
    { day: 'Thu', emoji: '🥘', name: 'Thai Curry', cal: 490 },
    { day: 'Fri', emoji: '🌮', name: 'Fish Tacos', cal: 410 },
    { day: 'Sat', emoji: '🍝', name: 'Pesto Pasta', cal: 460 },
  ];

  grid.innerHTML = meals.map((m, i) => `
        <div class="meal-day-card ${i === today ? 'today' : ''}" style="animation-delay: ${i * 0.05}s;">
            <div class="day-name">${m.day}</div>
            <span class="day-emoji float-animation" style="animation-delay: ${i * 0.3}s;">${m.emoji}</span>
            <div class="day-meal-name">${m.name}</div>
            <div class="day-calories">${m.cal} kcal</div>
        </div>
    `).join('');
}

// ═══════════════════════════════════════════════════════════════
// 🍕 RECENT RECIPES
// ═══════════════════════════════════════════════════════════════

function initRecentRecipes() {
  const grid = document.getElementById('recentRecipesGrid');
  if (!grid) return;

  const recipes = [
    {
      title: 'Mediterranean Salad',
      time: '15 min',
      cal: '320 kcal',
      badge: 'Vegan',
      gradient: 'linear-gradient(135deg, #10b981, #06b6d4)',
      icon: '🥗'
    },
    {
      title: 'Teriyaki Chicken Bowl',
      time: '25 min',
      cal: '520 kcal',
      badge: 'High Protein',
      gradient: 'linear-gradient(135deg, #f59e0b, #ef4444)',
      icon: '🍲'
    },
    {
      title: 'Overnight Oats',
      time: '5 min',
      cal: '280 kcal',
      badge: 'Breakfast',
      gradient: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
      icon: '🥣'
    },
    {
      title: 'Avocado Toast',
      time: '10 min',
      cal: '340 kcal',
      badge: 'Quick Meal',
      gradient: 'linear-gradient(135deg, #06b6d4, #10b981)',
      icon: '🥑'
    }
  ];

  grid.innerHTML = recipes.map((r, i) => `
        <div class="recipe-card animate-in" style="animation-delay: ${0.8 + i * 0.1}s;">
            <div class="recipe-card-img-wrapper">
                <div class="recipe-card-img" style="background: ${r.gradient}; display: flex; align-items: center; justify-content: center; font-size: 3rem;">
                    ${r.icon}
                </div>
                <span class="recipe-card-badge">${r.badge}</span>
            </div>
            <div class="recipe-card-body">
                <div class="recipe-card-title">${r.title}</div>
                <div class="recipe-card-meta">
                    <span><i class="fas fa-clock"></i> ${r.time}</span>
                    <span><i class="fas fa-fire"></i> ${r.cal}</span>
                </div>
            </div>
        </div>
    `).join('');
}

// ═══════════════════════════════════════════════════════════════
// 🔔 NOTIFICATIONS
// ═══════════════════════════════════════════════════════════════

function initNotifications() {
  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    const wrapper = document.getElementById('notifWrapper');
    const dropdown = document.getElementById('notifDropdown');
    if (wrapper && dropdown && !wrapper.contains(e.target)) {
      dropdown.classList.remove('show');
    }
  });
}

function toggleNotifications() {
  const dropdown = document.getElementById('notifDropdown');
  if (dropdown) dropdown.classList.toggle('show');
}

// ═══════════════════════════════════════════════════════════════
// 🔀 VIEW SWITCHING
// ═══════════════════════════════════════════════════════════════

function switchView(viewId) {
  // Hide all views
  document.querySelectorAll('.view-section').forEach(v => {
    v.style.display = 'none';
  });

  // Show selected view
  const target = document.getElementById(viewId);
  if (target) {
    target.style.display = 'block';
    target.style.animation = 'none';
    target.offsetHeight; // trigger reflow
    target.style.animation = 'fadeSlideIn 0.4s ease-out';
  }

  // Update sidebar active state
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.remove('active');
    if (item.dataset.view === viewId) {
      item.classList.add('active');
    }
  });

  // Update topbar title
  const titles = {
    'dashboardView': '<i class="fas fa-th-large"></i> Dashboard',
    'recipeView': '<i class="fas fa-wand-magic-sparkles"></i> Generate Recipe',
    'planView': '<i class="fas fa-calendar-week"></i> Weekly Plan',
    'ingredientsView': '<i class="fas fa-basket-shopping"></i> My Ingredients',
    'dishSearchView': '<i class="fas fa-magnifying-glass"></i> Search by Dish Name',
    'groceryView': '<i class="fas fa-cart-shopping"></i> Grocery Optimizer',
    'historyView': '<i class="fas fa-clock-rotate-left"></i> Session History'
  };
  const pageTitleEl = document.getElementById('pageTitle');
  if (pageTitleEl && titles[viewId]) {
    pageTitleEl.innerHTML = titles[viewId];
  }

  // Close mobile sidebar
  closeMobileSidebar();

  // Load history data when switching to history view
  if (viewId === 'historyView') {
    fetchHistoryData();
  }

  // Load grocery data when switching to grocery view
  if (viewId === 'groceryView') {
    loadPantryItems();
    loadBudgetStatus();
  }
}

// Legacy support
function showSection(sectionId) {
  const viewMap = {
    'generate': 'recipeView',
    'plan': 'planView',
    'ingredients': 'ingredientsView',
    'history': 'historyView'
  };
  switchView(viewMap[sectionId] || sectionId);
}

// ═══════════════════════════════════════════════════════════════
// 📊 LOGIN / SESSION HISTORY
// ═══════════════════════════════════════════════════════════════

async function fetchHistoryData() {
  const tbody = document.getElementById('historyTableBody');
  if (!tbody) return;

  // Show loading state
  tbody.innerHTML = `<tr>
    <td colspan="5" style="text-align: center; padding: 40px !important; color: var(--text-tertiary);">
      <i class="fas fa-spinner fa-spin"></i> Loading history...
    </td>
  </tr>`;

  try {
    const res = await fetch('/api/history');
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    const data = await res.json();
    const history = data.history || [];

    if (history.length === 0) {
      tbody.innerHTML = `<tr>
        <td colspan="5" style="text-align: center; padding: 40px !important; color: var(--text-tertiary);">
          <div style="font-size: 2rem; margin-bottom: 8px;">📭</div>
          No login history found yet.
        </td>
      </tr>`;
      return;
    }

    tbody.innerHTML = history.map((entry, idx) => {
      const isActive = entry.logout_time === 'Active';
      const statusBadge = isActive
        ? '<span style="background: rgba(16,185,129,0.15); color: #10b981; padding: 2px 8px; border-radius: 20px; font-size: 0.75rem;">● Active</span>'
        : `<span style="color: var(--text-secondary);">${entry.logout_time || 'N/A'}</span>`;

      return `<tr style="animation: fadeSlideIn 0.3s ease-out ${idx * 0.05}s both;">
        <td>${entry.date || 'N/A'}</td>
        <td>${entry.login_time || 'N/A'}</td>
        <td>${statusBadge}</td>
        <td>${entry.duration || 'N/A'}</td>
        <td style="max-width: 250px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${(entry.features || '').replace(/"/g, '&quot;')}">${entry.features || 'N/A'}</td>
      </tr>`;
    }).join('');
  } catch (err) {
    console.error('Failed to fetch history:', err);
    tbody.innerHTML = `<tr>
      <td colspan="5" style="text-align: center; padding: 40px !important; color: #ef4444;">
        <i class="fas fa-exclamation-triangle"></i> Failed to load history. Please try again.
      </td>
    </tr>`;
  }
}

// ═══════════════════════════════════════════════════════════════
// 🍳 GENERATE RECIPE
// ═══════════════════════════════════════════════════════════════

async function generateRecipe(isGourmet = false, isStrict = false) {
  const ingredient = isStrict
    ? (document.getElementById('strictIngredients')?.value || '')
    : (document.getElementById('ingredient')?.value || 'Chicken');

  const preference = document.getElementById('preference')?.value || 'Balanced';
  const age = document.getElementById('userAge')?.value || 30;
  const gender = document.getElementById('userGender')?.value || 'Male';
  const height = document.getElementById('userHeight')?.value || 170;
  const weight = document.getElementById('userWeight')?.value || 70;
  const activityEl = document.getElementById('activity');
  const activity = activityEl ? activityEl.value : 'Moderate';
  const allergies = document.getElementById('allergies')?.value || '';
  const goal = document.getElementById('goal')?.value || 'Nutrient Dense';

  const loadingEl = document.getElementById('loading');
  const resultEl = document.getElementById('resultSection');
  if (loadingEl) loadingEl.style.display = 'block';
  if (resultEl) resultEl.style.display = 'none';

  // Switch to recipe view if in strict mode
  if (isStrict) switchView('recipeView');

  // Collect active cuisine & dietary filters
  const filters = getActiveFilters();

  const body = {
    ingredient,
    preference,
    is_gourmet: isGourmet,
    is_strict: isStrict,
    age: parseInt(age),
    gender,
    height: parseInt(height),
    weight: parseInt(weight),
    activity_level: activity,
    allergies,
    goal,
    cuisines: filters.cuisines,
    dietary: filters.dietary
  };

  try {
    const res = await fetch('/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await res.json();
    currentRecipeData = data;
    currentMode = 'RECIPE';

    if (data.error) {
      alert("Error: " + data.error);
    } else {
      updateUI(data, ingredient, preference);
    }
  } catch (err) {
    console.error("Recipe generation failed:", err);
    alert("Something went wrong. Please try again.");
  } finally {
    if (loadingEl) loadingEl.style.display = 'none';
  }
}

// ═══════════════════════════════════════════════════════════════
// 🎨 UPDATE UI (Recipe Result)
// ═══════════════════════════════════════════════════════════════

function updateUI(data, ingredient, preference) {
  const resultEl = document.getElementById('resultSection');
  if (resultEl) {
    resultEl.style.display = 'block';
    resultEl.style.animation = 'fadeSlideIn 0.5s ease-out';
  }

  // Recipe Name
  const nameEl = document.getElementById('recipeName');
  if (nameEl) nameEl.textContent = data.english_name || data.recipe_name || data.name || 'Your Custom Recipe';

  // Description — backend sends 'intro'
  const descEl = document.getElementById('description');
  if (descEl) descEl.textContent = data.intro || data.description || '';

  // Prep Time
  const prepEl = document.getElementById('prepTime');
  if (prepEl) prepEl.textContent = data.prep_time || data.time || '30 min';

  // Nutrients — backend sends 'nutrients' (not 'nutrition')
  const nutrition = data.nutrients || data.nutrition || {};

  // Calories
  const calEl = document.getElementById('calCount');
  if (calEl) {
    const c = nutrition.calories || data.calories?.total || data.calories || 0;
    const calVal = typeof c === 'object' ? (c.total || 0) : c;
    calEl.textContent = `${calVal} kcal`;
  }

  // Nutrient badges
  const protEl = document.getElementById('proteinVal');
  const carbEl = document.getElementById('carbsVal');
  const fatEl = document.getElementById('fatVal');
  const fiberEl = document.getElementById('fiberVal');

  if (protEl) protEl.textContent = (nutrition.protein || '0') + 'g Protein';
  if (carbEl) carbEl.textContent = (nutrition.carbs || '0') + 'g Carbs';
  if (fatEl) fatEl.textContent = (nutrition.fat || '0') + 'g Fat';
  if (fiberEl) fiberEl.textContent = (nutrition.fiber || '0') + 'g Fiber';

  const kcalEl = document.getElementById('kcalVal');
  const kcalDisplay = nutrition.calories || data.calories?.total || 0;
  const kcalNum = typeof kcalDisplay === 'object' ? (kcalDisplay.total || 0) : kcalDisplay;
  if (kcalEl) kcalEl.textContent = kcalNum + ' kcal';

  // Ingredients list
  renderList('ingredientsListDisplay', data.ingredients || []);

  // Instructions — backend sends 'cooking_steps'
  renderSteps('stepsListDisplay', data.cooking_steps || data.instructions || data.steps || []);

  // Tips
  renderList('tipsListDisplay', data.tips || data.chef_tips || []);

  // Chart — include calories
  const calTotal = nutrition.calories || data.calories?.total || 0;
  const calValue = typeof calTotal === 'object' ? (calTotal.total || 0) : calTotal;
  if (nutrition.protein || nutrition.carbs || nutrition.fat || calValue) {
    drawChart(nutrition, calValue);
  }

  // Image — fetch dynamically based on recipe name
  const recipeName = data.recipe_name || data.name || 'Delicious Food';
  const englishName = data.english_name || recipeName;
  fetchRecipeImage(englishName, recipeName);

  // Store ingredients data for copy
  const dataEl = document.getElementById('ingredientsData');
  if (dataEl) {
    dataEl.textContent = JSON.stringify(data.ingredients || []);
  }
}

// ═══════════════════════════════════════════════════════════════
// 🔍 SEARCH BY DISH NAME
// ═══════════════════════════════════════════════════════════════

function setDishName(name) {
  const input = document.getElementById('dishNameInput');
  if (input) {
    input.value = name;
    input.focus();
  }
}

let dishChartInstance = null;

async function generateDishRecipe() {
  const dishName = document.getElementById('dishNameInput')?.value?.trim();
  if (!dishName) {
    alert('Please enter a dish name.');
    return;
  }

  const loadingEl = document.getElementById('dishLoading');
  const resultEl = document.getElementById('dishResultSection');
  if (loadingEl) loadingEl.style.display = 'block';
  if (resultEl) resultEl.style.display = 'none';

  try {
    const res = await fetch('/generate_dish', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dish_name: dishName })
    });
    const data = await res.json();

    if (data.error) {
      alert('Error: ' + data.error);
    } else {
      updateDishUI(data, dishName);
    }
  } catch (err) {
    console.error('Dish recipe generation failed:', err);
    alert('Something went wrong. Please try again.');
  } finally {
    if (loadingEl) loadingEl.style.display = 'none';
  }
}

function updateDishUI(data, dishName) {
  const resultEl = document.getElementById('dishResultSection');
  if (resultEl) {
    resultEl.style.display = 'block';
    resultEl.style.animation = 'fadeSlideIn 0.5s ease-out';
  }

  // Recipe Name
  const nameEl = document.getElementById('dishRecipeName');
  if (nameEl) nameEl.textContent = data.english_name || data.recipe_name || dishName;

  // Description
  const descEl = document.getElementById('dishDescription');
  if (descEl) descEl.textContent = data.intro || '';

  // Prep Time
  const prepEl = document.getElementById('dishPrepTime');
  if (prepEl) prepEl.textContent = data.prep_time || '30 mins';

  // Calories
  const calEl = document.getElementById('dishCalCount');
  if (calEl) {
    const c = data.nutrients?.calories || data.calories?.total || 0;
    calEl.textContent = `${c} kcal`;
  }

  // Category & Cuisine — extract from data if available
  const catEl = document.getElementById('dishCategory');
  const cuisineEl = document.getElementById('dishCuisine');
  // The parse_generated_output doesn't pass category/cuisine directly,
  // so we show sensible defaults
  if (catEl) catEl.textContent = data.category || 'Recipe';
  if (cuisineEl) cuisineEl.textContent = data.cuisine || 'International';

  // Nutrients
  const nutrition = data.nutrients || {};
  const protEl = document.getElementById('dishProteinVal');
  const carbEl = document.getElementById('dishCarbsVal');
  const fatEl = document.getElementById('dishFatVal');
  const fiberEl = document.getElementById('dishFiberVal');

  if (protEl) protEl.textContent = (nutrition.protein || '0') + 'g';
  if (carbEl) carbEl.textContent = (nutrition.carbs || '0') + 'g';
  if (fatEl) fatEl.textContent = (nutrition.fat || '0') + 'g';
  if (fiberEl) fiberEl.textContent = (nutrition.fiber || '0') + 'g';

  // Ingredients list
  renderList('dishIngredientsList', data.ingredients || []);

  // Instructions
  renderSteps('dishStepsList', data.cooking_steps || data.instructions || data.steps || []);

  // Tips
  renderList('dishTipsList', data.tips || data.chef_tips || []);

  // Chart
  if (nutrition.protein || nutrition.carbs || nutrition.fat) {
    drawDishChart(nutrition);
  }

  // Image — fetch dynamically
  const recipeName = data.recipe_name || dishName;
  const englishName = data.english_name || recipeName;
  fetchDishImage(englishName, recipeName);
}

function drawDishChart(nutrition) {
  const ctx = document.getElementById('dishNutrientChart');
  if (!ctx) return;

  if (dishChartInstance) {
    dishChartInstance.destroy();
  }

  dishChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Protein', 'Carbs', 'Fat'],
      datasets: [{
        data: [
          parseFloat(nutrition.protein) || 0,
          parseFloat(nutrition.carbs) || 0,
          parseFloat(nutrition.fat) || 0
        ],
        backgroundColor: [
          'rgba(99, 102, 241, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)'
        ],
        borderColor: [
          'rgba(99, 102, 241, 1)',
          'rgba(16, 185, 129, 1)',
          'rgba(245, 158, 11, 1)'
        ],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: 'rgba(255,255,255,0.7)',
            padding: 15,
            font: { size: 12, family: 'Inter' }
          }
        }
      }
    }
  });
}

async function fetchDishImage(englishName, displayName) {
  const heroContainer = document.getElementById('dishHeroImage');
  const imgEl = document.getElementById('dishFoodImage');
  const shimmer = document.getElementById('dishHeroShimmer');
  const badge = document.getElementById('dishImageBadge');
  if (!heroContainer || !imgEl) return;

  heroContainer.style.display = 'block';
  imgEl.style.opacity = '0';
  imgEl.style.display = 'none';
  if (shimmer) shimmer.style.display = 'block';
  if (badge) badge.style.display = 'none';
  heroContainer.classList.remove('show-placeholder');

  const oldPlaceholder = heroContainer.querySelector('.recipe-image-placeholder');
  if (oldPlaceholder) oldPlaceholder.remove();

  const query = encodeURIComponent(englishName || displayName);

  try {
    const res = await fetch(`/api/food-image?query=${query}`);
    const data = await res.json();

    if (data.image_url) {
      const tempImg = new Image();
      tempImg.onload = () => {
        imgEl.src = data.image_url;
        imgEl.alt = displayName || 'Dish Image';
        imgEl.style.display = 'block';
        if (shimmer) shimmer.style.display = 'none';
        requestAnimationFrame(() => {
          imgEl.style.opacity = '1';
          imgEl.classList.add('image-loaded');
        });
        if (badge) {
          const label = data.source === 'pexels_generic' ? '📷 Similar' : '📷 Photo';
          badge.innerHTML = `<i class="fas fa-camera"></i> ${label}`;
          badge.style.display = 'inline-flex';
        }
      };
      tempImg.onerror = () => {
        showDishPlaceholder(heroContainer, imgEl, shimmer, displayName);
      };
      tempImg.src = data.image_url;
      setTimeout(() => {
        if (imgEl.style.opacity === '0' || imgEl.style.display === 'none') {
          showDishPlaceholder(heroContainer, imgEl, shimmer, displayName);
        }
      }, 10000);
    } else {
      showDishPlaceholder(heroContainer, imgEl, shimmer, displayName);
    }
  } catch (err) {
    console.error('Dish image fetch error:', err);
    showDishPlaceholder(heroContainer, imgEl, shimmer, displayName);
  }
}

function showDishPlaceholder(container, imgEl, shimmer, name) {
  imgEl.style.display = 'none';
  if (shimmer) shimmer.style.display = 'none';
  container.classList.add('show-placeholder');
  if (!container.querySelector('.recipe-image-placeholder')) {
    const ph = document.createElement('div');
    ph.className = 'recipe-image-placeholder';
    ph.innerHTML = `
      <i class="fas fa-utensils"></i>
      <span>Image Preview Not Available</span>
      <small>${name || ''}</small>
    `;
    container.appendChild(ph);
  }
}

// ═══════════════════════════════════════════════════════════════
// 🖼️ RECIPE IMAGE FETCHER
// ═══════════════════════════════════════════════════════════════

async function fetchRecipeImage(englishName, displayName) {
  const heroContainer = document.getElementById('recipeHeroImage');
  const imgEl = document.getElementById('foodImage');
  const shimmer = document.getElementById('recipeHeroShimmer');
  const badge = document.getElementById('imageSourceBadge');
  if (!heroContainer || !imgEl) return;

  // Show hero container with shimmer loading
  heroContainer.style.display = 'block';
  imgEl.style.opacity = '0';
  imgEl.style.display = 'none';
  if (shimmer) shimmer.style.display = 'block';
  if (badge) badge.style.display = 'none';
  heroContainer.classList.remove('show-placeholder');

  // Remove any previous placeholder
  const oldPlaceholder = heroContainer.querySelector('.recipe-image-placeholder');
  if (oldPlaceholder) oldPlaceholder.remove();

  const query = encodeURIComponent(englishName || displayName);

  try {
    const res = await fetch(`/api/food-image?query=${query}`);
    const data = await res.json();

    if (data.image_url) {
      // Preload image before showing
      const tempImg = new Image();
      tempImg.onload = () => {
        imgEl.src = data.image_url;
        imgEl.alt = displayName || 'Recipe Image';
        imgEl.style.display = 'block';
        if (shimmer) shimmer.style.display = 'none';

        // Trigger fade-in animation
        requestAnimationFrame(() => {
          imgEl.style.opacity = '1';
          imgEl.classList.add('image-loaded');
        });

        // Show source badge
        if (badge) {
          const sourceLabel = data.source === 'pexels_generic' ? '📷 Similar Dish' : '📷 Photo';
          badge.innerHTML = `<i class="fas fa-camera"></i> ${sourceLabel}`;
          badge.style.display = 'inline-flex';
        }
      };
      tempImg.onerror = () => {
        showImagePlaceholder(heroContainer, imgEl, shimmer, displayName);
      };
      tempImg.src = data.image_url;

      // Timeout fallback — if image takes too long
      setTimeout(() => {
        if (imgEl.style.opacity === '0' || imgEl.style.display === 'none') {
          showImagePlaceholder(heroContainer, imgEl, shimmer, displayName);
        }
      }, 10000);
    } else {
      showImagePlaceholder(heroContainer, imgEl, shimmer, displayName);
    }
  } catch (err) {
    console.error('Image fetch error:', err);
    showImagePlaceholder(heroContainer, imgEl, shimmer, displayName);
  }
}

function showImagePlaceholder(container, imgEl, shimmer, recipeName) {
  imgEl.style.display = 'none';
  if (shimmer) shimmer.style.display = 'none';
  container.classList.add('show-placeholder');

  // Add placeholder content if not already present
  if (!container.querySelector('.recipe-image-placeholder')) {
    const placeholder = document.createElement('div');
    placeholder.className = 'recipe-image-placeholder';
    placeholder.innerHTML = `
      <i class="fas fa-utensils"></i>
      <span>Image Preview Not Available</span>
      <small>${recipeName || ''}</small>
    `;
    container.appendChild(placeholder);
  }
}

// ═══════════════════════════════════════════════════════════════
// 📝 RENDER HELPERS
// ═══════════════════════════════════════════════════════════════

function renderList(elementId, items) {
  const el = document.getElementById(elementId);
  if (!el) return;
  if (!items || items.length === 0) {
    el.innerHTML = '<li>No data</li>';
    return;
  }
  el.innerHTML = items.map(item => `<li>${item}</li>`).join('');
}

function renderSteps(elementId, steps) {
  const el = document.getElementById(elementId);
  if (!el) return;
  if (!steps || steps.length === 0) {
    el.innerHTML = '<p style="color: var(--text-tertiary);">No instructions available.</p>';
    return;
  }
  el.innerHTML = steps.map(step => {
    const text = typeof step === 'string' ? step : step.text || step.instruction || '';
    return `<div class="step-item">${text}</div>`;
  }).join('');
}

function renderMacroBar(label, macro) {
  const val = parseInt(macro) || 0;
  const max = 150;
  const pct = Math.min((val / max) * 100, 100);
  const colors = {
    'Protein': '#6366f1',
    'Carbs': '#06b6d4',
    'Fat': '#f59e0b',
    'Fiber': '#10b981'
  };
  return `
        <div class="macro-bar-container">
            <div class="macro-bar-label">
                <span>${label}</span>
                <span>${val}g</span>
            </div>
            <div class="macro-bar-track">
                <div class="macro-bar-fill" style="width: ${pct}%; background: ${colors[label] || '#6366f1'};"></div>
            </div>
        </div>
    `;
}

// ═══════════════════════════════════════════════════════════════
// 📊 CHARTS (Recipe Result)
// ═══════════════════════════════════════════════════════════════

function drawChart(nutrients, calories = 0) {
  const ctx = document.getElementById('nutrientChart');
  if (!ctx) return;

  if (chart) chart.destroy();

  const isLight = document.body.classList.contains('light-mode');

  const protein = parseFloat(nutrients.protein) || 0;
  const carbs = parseFloat(nutrients.carbs) || 0;
  const fat = parseFloat(nutrients.fat) || 0;
  const fiber = parseFloat(nutrients.fiber) || 0;
  const kcal = parseFloat(calories) || parseFloat(nutrients.calories) || 0;

  chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Protein (g)', 'Carbs (g)', 'Fat (g)', 'Fiber (g)', 'Calories (kcal)'],
      datasets: [{
        data: [protein, carbs, fat, fiber, kcal],
        backgroundColor: [
          'rgba(99, 102, 241, 0.85)',
          'rgba(6, 182, 212, 0.85)',
          'rgba(245, 158, 11, 0.85)',
          'rgba(16, 185, 129, 0.85)',
          'rgba(239, 68, 68, 0.85)'
        ],
        borderWidth: 0,
        borderRadius: 4,
        spacing: 2,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'right',
          labels: {
            color: isLight ? '#475569' : '#94a3b8',
            padding: 16,
            usePointStyle: true,
            pointStyle: 'circle',
            font: { size: 12 }
          }
        },
        tooltip: {
          backgroundColor: isLight ? '#fff' : '#1e293b',
          titleColor: isLight ? '#0f172a' : '#f1f5f9',
          bodyColor: isLight ? '#475569' : '#94a3b8',
          borderColor: isLight ? '#e2e8f0' : '#334155',
          borderWidth: 1,
          cornerRadius: 8,
          padding: 12,
          callbacks: {
            label: ctx => {
              const unit = ctx.label.includes('kcal') ? 'kcal' : 'g';
              return `${ctx.label}: ${ctx.raw}${unit === 'kcal' ? '' : unit}`;
            }
          }
        }
      },
      animation: {
        duration: 800,
        easing: 'easeOutQuart'
      }
    }
  });
}

function drawCalorieChart(caloriesData) {
  // Backwards compatibility - called from updateUI if present
  const ctx = document.getElementById('nutrientChart');
  if (!ctx) return;
  // Use drawChart instead for consistency
}

// ═══════════════════════════════════════════════════════════════
// 🗓️ GENERATE WEEKLY PLAN
// ═══════════════════════════════════════════════════════════════

async function generatePlan(isStrict = false) {
  const age = document.getElementById('age')?.value || 30;
  const gender = document.getElementById('gender')?.value || 'Male';
  const height = document.getElementById('height')?.value || 170;
  const weight = document.getElementById('weight')?.value || 70;
  const activity = document.getElementById('planActivity')?.value || 'Moderate';
  const allergies = document.getElementById('planAllergies')?.value || '';
  const preference = document.getElementById('planPreference')?.value || 'Standard';
  const goal = document.getElementById('planGoal')?.value || 'Healthy Living';

  const ingredient = isStrict
    ? (document.getElementById('strictIngredients')?.value || '')
    : '';

  const loadingEl = document.getElementById('planLoading') || document.getElementById('loading');
  const resultEl = document.getElementById('planResultSection');
  if (loadingEl) loadingEl.style.display = 'block';
  if (resultEl) resultEl.style.display = 'none';

  if (isStrict) switchView('planView');

  const body = {
    age: parseInt(age),
    gender,
    height: parseInt(height),
    weight: parseInt(weight),
    activity_level: activity,
    allergies,
    preference,
    goal,
    is_strict: isStrict,
    ingredient: ingredient
  };

  try {
    const res = await fetch('/generate_plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const response = await res.json();
    // Backend wraps response in {success, data, raw_text}
    const data = response.data || response;
    currentPlanData = data;
    currentMode = 'PLAN';

    if (response.error) {
      alert("Error: " + response.error);
    } else {
      updatePlanUI(data);
    }
  } catch (err) {
    console.error("Plan generation failed:", err);
    alert("Something went wrong. Please try again.");
  } finally {
    if (loadingEl) loadingEl.style.display = 'none';
  }
}
// ═══════════════════════════════════════════════════════════════
// 🥕 STRICT INGREDIENT MODE (My Ingredients View)
// ═══════════════════════════════════════════════════════════════

function generateStrictRecipe() {
  // Uses the strict ingredients from the My Ingredients view
  const ingredients = document.getElementById('strictIngredients')?.value?.trim();
  if (!ingredients) {
    alert('Please enter your available ingredients.');
    return;
  }

  const loadingEl = document.getElementById('strictLoading');
  const resultEl = document.getElementById('strictResultSection');
  if (loadingEl) loadingEl.style.display = 'block';
  if (resultEl) resultEl.style.display = 'none';

  const body = {
    ingredient: ingredients,
    food_type: 'Balanced',
    goal: 'Healthy Living',
    strict_mode: true,
    strict_ingredients: ingredients
  };

  fetch('/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        alert('Error: ' + data.error);
      } else {
        updateStrictUI(data);
      }
    })
    .catch(err => {
      console.error('Strict recipe generation failed:', err);
      alert('Something went wrong. Please try again.');
    })
    .finally(() => {
      if (loadingEl) loadingEl.style.display = 'none';
    });
}

function generateStrictPlan() {
  // Calls the plan generator with strict ingredient mode
  generatePlan(true);
}

function updateStrictUI(data) {
  const resultEl = document.getElementById('strictResultSection');
  if (resultEl) {
    resultEl.style.display = 'block';
    resultEl.style.animation = 'fadeSlideIn 0.5s ease-out';
  }

  // Recipe Name
  const nameEl = document.getElementById('strictRecipeName');
  if (nameEl) nameEl.textContent = data.english_name || data.recipe_name || 'Your Recipe';

  // Description
  const descEl = document.getElementById('strictDescription');
  if (descEl) descEl.textContent = data.intro || data.description || '';

  // Prep Time
  const prepEl = document.getElementById('strictPrepTime');
  if (prepEl) prepEl.textContent = data.prep_time || '30 min';

  // Calories
  const calEl = document.getElementById('strictCalCount');
  const nutrition = data.nutrients || data.nutrition || {};
  if (calEl) {
    const c = nutrition.calories || 0;
    calEl.textContent = `${c} kcal`;
  }

  // Nutrient badges
  const protEl = document.getElementById('strictProteinVal');
  const carbEl = document.getElementById('strictCarbsVal');
  const fatEl = document.getElementById('strictFatVal');
  const fiberEl = document.getElementById('strictFiberVal');

  if (protEl) protEl.textContent = (nutrition.protein || '0') + 'g';
  if (carbEl) carbEl.textContent = (nutrition.carbs || '0') + 'g';
  if (fatEl) fatEl.textContent = (nutrition.fat || '0') + 'g';
  if (fiberEl) fiberEl.textContent = (nutrition.fiber || '0') + 'g';

  // Ingredients list
  renderList('strictIngredientsListDisplay', data.ingredients || []);

  // Instructions
  renderSteps('strictStepsListDisplay', data.cooking_steps || data.instructions || []);

  // Tips
  renderList('strictTipsListDisplay', data.tips || data.chef_tips || []);

  // Chart
  if (nutrition.protein || nutrition.carbs || nutrition.fat) {
    drawStrictChart(nutrition);
  }

  // Image
  const recipeName = data.recipe_name || 'Delicious Food';
  const englishName = data.english_name || recipeName;
  fetchStrictImage(englishName, recipeName);

  // Store for copy
  const dataEl = document.getElementById('strictIngredientsData');
  if (dataEl) dataEl.textContent = JSON.stringify(data.ingredients || []);
}

let strictChartInstance = null;

function drawStrictChart(nutrition) {
  const ctx = document.getElementById('strictNutrientChart');
  if (!ctx) return;
  if (strictChartInstance) strictChartInstance.destroy();

  strictChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Protein', 'Carbs', 'Fat'],
      datasets: [{
        data: [
          parseFloat(nutrition.protein) || 0,
          parseFloat(nutrition.carbs) || 0,
          parseFloat(nutrition.fat) || 0
        ],
        backgroundColor: [
          'rgba(99, 102, 241, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)'
        ],
        borderWidth: 0,
        borderRadius: 4,
      }]
    },
    options: {
      responsive: true,
      cutout: '60%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: document.body.classList.contains('light-mode') ? '#475569' : '#94a3b8',
            padding: 16,
            usePointStyle: true,
            font: { size: 12 }
          }
        }
      }
    }
  });
}

async function fetchStrictImage(englishName, displayName) {
  const heroContainer = document.getElementById('strictHeroImage');
  const imgEl = document.getElementById('strictFoodImage');
  const shimmer = document.getElementById('strictHeroShimmer');
  const badge = document.getElementById('strictImageBadge');
  if (!heroContainer || !imgEl) return;

  heroContainer.style.display = 'block';
  imgEl.style.opacity = '0';
  imgEl.style.display = 'none';
  if (shimmer) shimmer.style.display = 'block';
  if (badge) badge.style.display = 'none';
  heroContainer.classList.remove('show-placeholder');

  const oldPlaceholder = heroContainer.querySelector('.recipe-image-placeholder');
  if (oldPlaceholder) oldPlaceholder.remove();

  const query = encodeURIComponent(englishName || displayName);

  try {
    const res = await fetch(`/api/food-image?query=${query}`);
    const data = await res.json();

    if (data.image_url) {
      const tempImg = new Image();
      tempImg.onload = () => {
        imgEl.src = data.image_url;
        imgEl.alt = displayName || 'Recipe Image';
        imgEl.style.display = 'block';
        if (shimmer) shimmer.style.display = 'none';
        requestAnimationFrame(() => {
          imgEl.style.opacity = '1';
          imgEl.classList.add('image-loaded');
        });
        if (badge) {
          badge.innerHTML = `<i class="fas fa-camera"></i> Photo`;
          badge.style.display = 'inline-flex';
        }
      };
      tempImg.onerror = () => {
        showDishPlaceholder(heroContainer, imgEl, shimmer, displayName);
      };
      tempImg.src = data.image_url;
      setTimeout(() => {
        if (imgEl.style.opacity === '0' || imgEl.style.display === 'none') {
          showDishPlaceholder(heroContainer, imgEl, shimmer, displayName);
        }
      }, 10000);
    } else {
      showDishPlaceholder(heroContainer, imgEl, shimmer, displayName);
    }
  } catch (err) {
    console.error('Strict image fetch error:', err);
    showDishPlaceholder(heroContainer, imgEl, shimmer, displayName);
  }
}

// ═══════════════════════════════════════════════════════════════
// 📋 UPDATE PLAN UI
// ═══════════════════════════════════════════════════════════════

function updatePlanUI(data) {
  const resultEl = document.getElementById('planResultSection');
  if (resultEl) {
    resultEl.style.display = 'block';
    resultEl.style.animation = 'fadeSlideIn 0.5s ease-out';
  }

  // Summary
  const summaryEl = document.getElementById('planSummary');
  if (summaryEl && data.summary) {
    summaryEl.innerHTML = `
            <div class="glass-panel-header">
                <div class="glass-panel-title"><i class="fas fa-chart-line"></i> Nutrition Summary</div>
            </div>
            <p style="color: var(--text-secondary); line-height: 1.7;">${data.summary}</p>
        `;
  }

  // Weekly plan — backend sends 'schedule' (from meal_plan_7_days)
  const container = document.getElementById('weeklyPlanContainer');
  const days = data.plan || data.schedule;
  if (container && days) {
    container.innerHTML = '';

    const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const emojis = ['🍳', '🥗', '🍲', '🐟', '🥘', '🌮', '🍝'];

    if (Array.isArray(days)) {
      days.forEach((day, i) => {
        const dayData = typeof day === 'string' ? day : JSON.stringify(day, null, 2);
        const dayCard = document.createElement('div');
        dayCard.className = 'plan-day-card animate-in';
        dayCard.style.animationDelay = `${i * 0.1}s`;
        dayCard.innerHTML = `
                    <h3>${emojis[i % 7]} ${dayNames[i % 7]}</h3>
                    <div style="color: var(--text-secondary); white-space: pre-wrap; line-height: 1.7; font-size: 0.9rem;">${dayData}</div>
                `;
        container.appendChild(dayCard);
      });
    } else if (typeof days === 'object') {
      Object.entries(days).forEach(([dayName, meals], i) => {
        const dayCard = document.createElement('div');
        dayCard.className = 'plan-day-card animate-in';
        dayCard.style.animationDelay = `${i * 0.1}s`;

        // Format meals nicely
        let mealHtml = '';
        if (typeof meals === 'object' && meals !== null) {
          const mealTypes = ['Breakfast', 'Lunch', 'Dinner', 'Snack'];
          for (const [key, val] of Object.entries(meals)) {
            if (key === 'daily_nutrition') {
              // Format nutrition as a compact row
              const nutri = typeof val === 'object' ? Object.entries(val).map(([k, v]) => `${k}: ${v}`).join(' • ') : val;
              mealHtml += `<div style="margin-top:8px; padding:8px 12px; background:rgba(99,102,241,0.1); border-radius:8px; font-size:0.8rem; color:var(--text-tertiary);"><i class="fas fa-chart-pie"></i> ${nutri}</div>`;
            } else {
              const icon = key === 'Breakfast' ? '🌅' : key === 'Lunch' ? '☀️' : key === 'Dinner' ? '🌙' : '🍎';
              mealHtml += `<div style="margin-bottom:6px;"><strong style="color:var(--text-primary);">${icon} ${key}:</strong> <span style="color:var(--text-secondary);">${val}</span></div>`;
            }
          }
        } else {
          mealHtml = typeof meals === 'string' ? meals : JSON.stringify(meals, null, 2);
        }

        // Format day name: "Day_1" -> "Day 1"
        const displayName = dayName.replace(/_/g, ' ');
        dayCard.innerHTML = `
                    <h3>${emojis[i % 7]} ${displayName}</h3>
                    <div style="line-height: 1.7; font-size: 0.9rem;">${mealHtml}</div>
                `;
        container.appendChild(dayCard);
      });
    }
  }

  // Grocery list — backend sends 'grocery' (not 'grocery_list')
  const groceryEl = document.getElementById('groceryListContainer');
  const groceryData = data.grocery_list || data.grocery;
  if (groceryEl && groceryData) {
    let groceryHtml = '';
    if (typeof groceryData === 'object' && !Array.isArray(groceryData)) {
      // Object format: {"Produce": ["Item1", "Item2"], "Protein": ["Item3"]}
      for (const [category, items] of Object.entries(groceryData)) {
        const itemList = Array.isArray(items) ? items : [items];
        groceryHtml += `<div style="margin-bottom:12px;"><strong style="color:var(--accent-primary);">${category}</strong><ul style="margin:4px 0 0 16px; color:var(--text-secondary);">`;
        itemList.forEach(item => { groceryHtml += `<li>${item}</li>`; });
        groceryHtml += `</ul></div>`;
      }
    } else if (Array.isArray(groceryData)) {
      groceryHtml = groceryData.map(item => `<div style="color:var(--text-secondary);padding:2px 0;">• ${item}</div>`).join('');
    } else {
      groceryHtml = `<div style="color:var(--text-secondary);white-space:pre-wrap;">${groceryData}</div>`;
    }
    groceryEl.innerHTML = `
            <div class="glass-panel-header">
                <div class="glass-panel-title"><i class="fas fa-basket-shopping"></i> Grocery List</div>
            </div>
            <div style="line-height: 1.7; font-size: 0.9rem;">${groceryHtml}</div>
        `;
  }

  // Store optimized grocery data for the Grocery Optimizer view
  if (data.optimized_grocery) {
    window._lastOptimizedGrocery = data.optimized_grocery;
    renderOptimizedGrocery(data.optimized_grocery);
  }

  // Protein chart for plan
  if (data.nutrition || data.macros) {
    const n = data.nutrition || data.macros;
    drawPlanProteinChart(
      parseFloat(n.protein) || 0,
      parseFloat(n.carbs) || 0,
      parseFloat(n.fat) || 0
    );
  }
}

function drawPlanProteinChart(protein, carbs, fat) {
  const ctx = document.getElementById('nutrientChart');
  if (!ctx) return;

  if (proteinChart) proteinChart.destroy();

  const isLight = document.body.classList.contains('light-mode');

  proteinChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Protein', 'Carbs', 'Fat'],
      datasets: [{
        data: [protein, carbs, fat],
        backgroundColor: [
          'rgba(99, 102, 241, 0.85)',
          'rgba(6, 182, 212, 0.85)',
          'rgba(245, 158, 11, 0.85)'
        ],
        borderWidth: 0,
        borderRadius: 4,
      }]
    },
    options: {
      responsive: true,
      cutout: '60%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: isLight ? '#475569' : '#94a3b8',
            padding: 16,
            usePointStyle: true,
            font: { size: 12 }
          }
        }
      }
    }
  });
}

// ═══════════════════════════════════════════════════════════════
// 🛒 UTILITIES
// ═══════════════════════════════════════════════════════════════

function resetForm() {
  ['ingredient', 'allergies'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  const resultEl = document.getElementById('resultSection');
  if (resultEl) resultEl.style.display = 'none';
}

function copyGroceryList() {
  const data = document.getElementById('ingredientsData');
  if (data) {
    const items = JSON.parse(data.textContent || '[]');
    navigator.clipboard.writeText(items.join('\n'))
      .then(() => showToast('Grocery list copied!'))
      .catch(() => alert('Failed to copy'));
  }
}

function copyRecipe() {
  const name = document.getElementById('recipeName')?.textContent || '';
  const desc = document.getElementById('description')?.textContent || '';
  const text = `${name}\n\n${desc}`;
  navigator.clipboard.writeText(text)
    .then(() => showToast('Recipe copied!'))
    .catch(() => alert('Failed to copy'));
}

function shareWhatsApp() {
  const name = document.getElementById('recipeName')?.textContent || '';
  const desc = document.getElementById('description')?.textContent || '';
  const text = `🍽️ ${name}\n\n${desc}\n\n— Generated by NutriGen AI`;
  window.open(`https://wa.me/?text=${encodeURIComponent(text)}`);
}

// Simple toast notification
function showToast(message) {
  const toast = document.createElement('div');
  toast.textContent = message;
  toast.style.cssText = `
        position: fixed; bottom: 24px; right: 24px;
        background: var(--accent-primary); color: white;
        padding: 12px 24px; border-radius: 8px; z-index: 10000;
        font-size: 0.9rem; font-weight: 500;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
        animation: fadeSlideIn 0.3s ease-out;
    `;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s';
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}

let strictChart = null;

async function generateStrictRecipe() {
  const ingredient = document.getElementById('strictIngredients')?.value || '';
  if (!ingredient.trim()) {
    alert('Please enter your available ingredients first.');
    return;
  }

  const loadingEl = document.getElementById('strictLoading');
  const resultEl = document.getElementById('strictResultSection');
  if (loadingEl) loadingEl.style.display = 'block';
  if (resultEl) resultEl.style.display = 'none';

  // Scroll down to show loading
  loadingEl?.scrollIntoView({ behavior: 'smooth', block: 'center' });

  const body = {
    ingredient,
    food_type: 'Balanced',
    goal: 'Nutrient Dense',
    allergies: '',
    strict_mode: true,
    strict_ingredients: ingredient,
    age: 30,
    gender: 'Male',
    height: 170,
    weight: 70,
    activity_level: 'Moderate'
  };

  try {
    const res = await fetch('/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await res.json();

    if (data.error) {
      alert("Error: " + data.error);
    } else {
      currentRecipeData = data;
      currentMode = 'RECIPE';
      updateStrictUI(data);
    }
  } catch (err) {
    console.error("Strict recipe generation failed:", err);
    alert("Something went wrong. Please try again.");
  } finally {
    if (loadingEl) loadingEl.style.display = 'none';
  }
}

function updateStrictUI(data) {
  const resultEl = document.getElementById('strictResultSection');
  if (resultEl) {
    resultEl.style.display = 'block';
    resultEl.style.animation = 'fadeSlideIn 0.5s ease-out';
    resultEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // Recipe Name
  const nameEl = document.getElementById('strictRecipeName');
  if (nameEl) nameEl.textContent = data.recipe_name || 'Your Recipe';

  // Prep Time & Calories
  const prepEl = document.getElementById('strictPrepTime');
  if (prepEl) prepEl.textContent = data.prep_time || '--';
  const calEl = document.getElementById('strictCalCount');
  if (calEl) calEl.textContent = data.nutrients?.calories ? `${data.nutrients.calories} kcal` : '--';

  // Description
  const descEl = document.getElementById('strictDescription');
  if (descEl) descEl.textContent = data.intro || '';

  // Nutrients
  const nutrients = data.nutrients || {};
  const setVal = (id, val, unit) => {
    const el = document.getElementById(id);
    if (el) el.textContent = `${val || 0}${unit}`;
  };
  setVal('strictProteinVal', nutrients.protein, 'g');
  setVal('strictCarbsVal', nutrients.carbs, 'g');
  setVal('strictFatVal', nutrients.fat, 'g');
  setVal('strictFiberVal', nutrients.fiber, 'g');

  // Ingredients list
  const ingEl = document.getElementById('strictIngredientsListDisplay');
  if (ingEl && data.ingredients) {
    ingEl.innerHTML = data.ingredients.map(item =>
      `<li><span class="list-bullet">•</span> ${typeof item === 'string' ? item : item.text || item.item || ''}</li>`
    ).join('');
  }

  // Instructions
  renderSteps('strictStepsListDisplay', data.cooking_steps || []);

  // Tips
  const tipsEl = document.getElementById('strictTipsListDisplay');
  if (tipsEl && data.tips) {
    tipsEl.innerHTML = data.tips.map(t =>
      `<li><span class="list-bullet">💡</span> ${t}</li>`
    ).join('');
  }

  // Grocery data (hidden, for copy)
  const groceryDataEl = document.getElementById('strictIngredientsData');
  if (groceryDataEl) {
    groceryDataEl.textContent = JSON.stringify(data.ingredients || []);
  }

  // Image
  if (data.english_name || data.image_search_query) {
    fetchStrictRecipeImage(data);
  }

  // Chart
  drawStrictChart(nutrients);
}

function drawStrictChart(nutrients) {
  const ctx = document.getElementById('strictNutrientChart');
  if (!ctx) return;
  if (strictChart) strictChart.destroy();

  const isLight = document.body.classList.contains('light-mode');
  const protein = parseFloat(nutrients.protein) || 0;
  const carbs = parseFloat(nutrients.carbs) || 0;
  const fat = parseFloat(nutrients.fat) || 0;
  const fiber = parseFloat(nutrients.fiber) || 0;
  const kcal = parseFloat(nutrients.calories) || 0;

  strictChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Protein (g)', 'Carbs (g)', 'Fat (g)', 'Fiber (g)', 'Calories (kcal)'],
      datasets: [{
        data: [protein, carbs, fat, fiber, kcal],
        backgroundColor: [
          'rgba(99, 102, 241, 0.85)',
          'rgba(6, 182, 212, 0.85)',
          'rgba(245, 158, 11, 0.85)',
          'rgba(16, 185, 129, 0.85)',
          'rgba(239, 68, 68, 0.85)'
        ],
        borderWidth: 0,
        borderRadius: 4,
        spacing: 2,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'right',
          labels: {
            color: isLight ? '#475569' : '#94a3b8',
            padding: 16,
            usePointStyle: true,
            pointStyle: 'circle',
            font: { size: 12 }
          }
        }
      },
      animation: { duration: 800, easing: 'easeOutQuart' }
    }
  });
}

async function fetchStrictRecipeImage(data) {
  const heroDiv = document.getElementById('strictHeroImage');
  const imgEl = document.getElementById('strictFoodImage');
  const shimmer = document.getElementById('strictHeroShimmer');
  if (!heroDiv || !imgEl) return;

  heroDiv.style.display = 'block';
  if (shimmer) shimmer.style.display = 'block';

  const searchName = data.english_name || data.recipe_name || 'food';
  try {
    const res = await fetch(`/api/recipe-image?query=${encodeURIComponent(searchName)}`);
    const imgData = await res.json();
    if (imgData.url) {
      imgEl.src = imgData.url;
      imgEl.onload = () => { if (shimmer) shimmer.style.display = 'none'; };
      imgEl.onerror = () => {
        heroDiv.style.display = 'none';
      };
    } else {
      heroDiv.style.display = 'none';
    }
  } catch {
    heroDiv.style.display = 'none';
  }
}

function copyStrictRecipe() {
  const name = document.getElementById('strictRecipeName')?.textContent || '';
  const desc = document.getElementById('strictDescription')?.textContent || '';
  const text = `${name}\n\n${desc}`;
  navigator.clipboard.writeText(text)
    .then(() => showToast('Recipe copied!'))
    .catch(() => alert('Failed to copy'));
}

function shareStrictWhatsApp() {
  const name = document.getElementById('strictRecipeName')?.textContent || '';
  const desc = document.getElementById('strictDescription')?.textContent || '';
  const text = `🍽️ ${name}\n\n${desc}\n\n— Generated by NutriGen AI`;
  window.open(`https://wa.me/?text=${encodeURIComponent(text)}`);
}

function copyStrictGroceryList() {
  const data = document.getElementById('strictIngredientsData');
  if (data) {
    const items = JSON.parse(data.textContent || '[]');
    const text = items.map(i => typeof i === 'string' ? i : i.item || i).join('\n');
    navigator.clipboard.writeText(text)
      .then(() => showToast('Grocery list copied!'))
      .catch(() => alert('Failed to copy'));
  }
}

function generateStrictPlan() {
  generatePlan(true);
}

// ═══════════════════════════════════════════════════════════════
// 🌍 TRANSLATION
// ═══════════════════════════════════════════════════════════════

function initLanguageListener() {
  const langSelect = document.getElementById('languageSelect');
  if (langSelect) {
    langSelect.addEventListener('change', function () {
      translateContent(this.value);
    });
  }
}

async function translateContent(lang) {
  if (lang === 'en') return; // already English

  if (!currentRecipeData && !currentPlanData) {
    console.log("No data to translate");
    return;
  }

  const dataToTranslate = currentMode === 'RECIPE' ? currentRecipeData : currentPlanData;

  try {
    const res = await fetch('/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data: dataToTranslate,
        target_lang: lang,
        mode: currentMode
      })
    });

    const translated = await res.json();
    if (translated.error) {
      console.error("Translation error:", translated.error);
      return;
    }

    if (currentMode === 'RECIPE') {
      updateUI(translated, '', '');
    } else {
      updatePlanUI(translated);
    }
  } catch (err) {
    console.error("Translation failed:", err);
  }
}

// ═══════════════════════════════════════════════════════════════
// 📜 HISTORY
// ═══════════════════════════════════════════════════════════════

async function fetchHistoryData() {
  try {
    const res = await fetch('/api/history');
    const data = await res.json();
    const tbody = document.getElementById('historyTableBody');
    if (!tbody) return;

    if (!data || !data.history || data.history.length === 0) {
      tbody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; padding: 40px !important; color: var(--text-tertiary);">
                        No login history found
                    </td>
                </tr>
            `;
      return;
    }

    tbody.innerHTML = data.history.map(entry => {
      const date = entry.date || 'N/A';
      const loginTime = entry.login_time || 'N/A';
      const logoutTime = entry.logout_time || 'Active';
      const duration = entry.duration || 'N/A';
      const features = entry.features || 'Logged In';

      return `
                <tr>
                    <td>${date}</td>
                    <td>${loginTime}</td>
                    <td>${logoutTime}</td>
                    <td>${duration}</td>
                    <td>${features}</td>
                </tr>
            `;
    }).join('');
  } catch (err) {
    console.error("Failed to fetch history:", err);
  }
}

function showLoginHistory() {
  switchView('historyView');
  fetchHistoryData();
}

// ═══════════════════════════════════════════════════════════════
// 🚪 LOGOUT
// ═══════════════════════════════════════════════════════════════

function logout() {
  window.location.href = '/logout';
}

// ═══════════════════════════════════════════════════════════════
// ✨ SCROLL ANIMATIONS
// ═══════════════════════════════════════════════════════════════

function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -40px 0px'
  });

  document.querySelectorAll('.animate-on-scroll').forEach(el => {
    observer.observe(el);
  });
}

// ═══════════════════════════════════════════════════════════════
// 🎭 RIPPLE EFFECT FOR BUTTONS
// ═══════════════════════════════════════════════════════════════

document.addEventListener('click', (e) => {
  const btn = e.target.closest('.ripple');
  if (!btn) return;

  const circle = document.createElement('span');
  const diameter = Math.max(btn.clientWidth, btn.clientHeight);
  const radius = diameter / 2;
  const rect = btn.getBoundingClientRect();

  circle.style.cssText = `
        width: ${diameter}px; height: ${diameter}px;
        left: ${e.clientX - rect.left - radius}px;
        top: ${e.clientY - rect.top - radius}px;
        position: absolute; border-radius: 50%;
        background: rgba(255, 255, 255, 0.25);
        transform: scale(0); pointer-events: none;
        animation: ripple-effect 0.5s ease-out;
    `;

  btn.style.position = 'relative';
  btn.style.overflow = 'hidden';
  btn.appendChild(circle);
  setTimeout(() => circle.remove(), 500);
});

// ═══════════════════════════════════════════════════════════════
// 🛒 GROCERY OPTIMIZER
// ═══════════════════════════════════════════════════════════════

// --- Budget ---
async function setBudget() {
  const amount = document.getElementById('budgetAmount').value;
  const currency = document.getElementById('budgetCurrency').value;
  try {
    const res = await fetch('/api/budget/set', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount, currency })
    });
    const data = await res.json();
    if (data.success) {
      showBudgetProgress(data.budget);
    }
  } catch (e) { console.error('Budget set error:', e); }
}

async function loadBudgetStatus() {
  try {
    const res = await fetch('/api/budget/status');
    const data = await res.json();
    if (data.success && data.budget && data.budget.amount > 0) {
      document.getElementById('budgetAmount').value = data.budget.amount;
      showBudgetProgress(data.budget);
    }
  } catch (e) { console.error('Budget load error:', e); }
}

function showBudgetProgress(budget) {
  const area = document.getElementById('budgetProgressArea');
  if (!area) return;
  area.style.display = 'block';
  const spent = budget.spent || 0;
  const total = budget.amount || 1;
  const pct = Math.min((spent / total) * 100, 100);
  const fill = document.getElementById('budgetBarFill');
  const sym = budget.currency === 'USD' ? '$' : '₹';

  document.getElementById('budgetSpentLabel').textContent = `${sym}${spent.toFixed(0)} spent`;
  document.getElementById('budgetTotalLabel').textContent = `of ${sym}${total.toFixed(0)}`;

  fill.style.width = pct + '%';
  fill.className = 'budget-bar-fill';
  if (pct > 100) fill.classList.add('over');
  else if (pct > 80) fill.classList.add('warning');

  const msg = document.getElementById('budgetStatusMsg');
  if (budget.status === 'over') msg.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Over budget!';
  else if (budget.status === 'warning') msg.innerHTML = '<i class="fas fa-exclamation-circle"></i> Approaching budget limit';
  else msg.innerHTML = '<i class="fas fa-check-circle"></i> Within budget';
}

async function clearBudget() {
  try {
    await fetch('/api/budget/clear', { method: 'POST' });
    document.getElementById('budgetProgressArea').style.display = 'none';
  } catch (e) { console.error(e); }
}

// --- Pantry ---
async function addPantryItem() {
  const name = document.getElementById('pantryItemName').value.trim();
  if (!name) return;
  const qty = document.getElementById('pantryItemQty').value || 1;
  const unit = document.getElementById('pantryItemUnit').value;
  try {
    const res = await fetch('/api/pantry', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, quantity: qty, unit })
    });
    const data = await res.json();
    if (data.success) {
      document.getElementById('pantryItemName').value = '';
      document.getElementById('pantryItemQty').value = '1';
      renderPantryList(data.items);
    }
  } catch (e) { console.error('Pantry add error:', e); }
}

async function removePantryItem(name) {
  try {
    const res = await fetch('/api/pantry/remove', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });
    const data = await res.json();
    if (data.success) renderPantryList(data.items);
  } catch (e) { console.error(e); }
}

async function clearPantry() {
  try {
    await fetch('/api/pantry/clear', { method: 'POST' });
    renderPantryList([]);
  } catch (e) { console.error(e); }
}

async function loadPantryItems() {
  try {
    const res = await fetch('/api/pantry');
    const data = await res.json();
    if (data.success) renderPantryList(data.items);
  } catch (e) { console.error(e); }
}

function renderPantryList(items) {
  const container = document.getElementById('pantryList');
  if (!container) return;
  if (!items || items.length === 0) {
    container.innerHTML = '<p style="color: var(--text-tertiary); font-size:0.85rem;">No pantry items yet.</p>';
    return;
  }
  container.innerHTML = items.map(item => `
    <div class="pantry-chip">
      <span class="pantry-chip-name">${item.name}</span>
      <span class="pantry-chip-qty">${item.quantity} ${item.unit}</span>
      <button class="pantry-chip-remove" onclick="removePantryItem('${item.name}')" title="Remove">
        <i class="fas fa-times"></i>
      </button>
    </div>
  `).join('');
}

// --- Optimized Grocery List ---
function renderOptimizedGrocery(og) {
  if (!og) return;

  // Show/hide sections
  const section = document.getElementById('optimizedGrocerySection');
  const empty = document.getElementById('groceryEmptyState');
  if (section) section.style.display = 'block';
  if (empty) empty.style.display = 'none';

  // Cost summary
  const costEl = document.getElementById('groceryCostSummary');
  if (costEl && og.cost_summary) {
    const cs = og.cost_summary;
    const sym = cs.currency === 'USD' ? '$' : '₹';
    costEl.innerHTML = `
      <div class="cost-card"><div class="cost-label">Total Items</div><div class="cost-value">${og.total_unique || 0}</div></div>
      <div class="cost-card"><div class="cost-label">Estimated Cost</div><div class="cost-value">${sym}${(cs.total || 0).toFixed(0)}</div></div>
      <div class="cost-card"><div class="cost-label">Avg/Item</div><div class="cost-value">${sym}${(cs.average_per_item || 0).toFixed(0)}</div></div>
    `;
  }

  // Categories
  const catContainer = document.getElementById('groceryCategoriesContainer');
  if (catContainer && og.categories) {
    const catIcons = { 'vegetables': '🥬', 'fruits': '🍎', 'grains': '🌾', 'proteins': '🥩', 'dairy': '🧀', 'spices': '🌶️', 'condiments': '🧂', 'oils': '🫒', 'other': '📦' };
    let html = '';
    for (const [cat, items] of Object.entries(og.categories)) {
      if (!items || items.length === 0) continue;
      const icon = catIcons[cat.toLowerCase()] || '📦';
      html += `
        <div class="grocery-category">
          <h4 class="grocery-category-title">${icon} ${cat}</h4>
          <div class="grocery-items-list">
            ${items.map(item => `
              <div class="grocery-item-row ${item.pantry_deducted ? 'deducted' : ''}">
                <span class="grocery-item-name">${item.name}</span>
                <span class="grocery-item-qty">${item.display_qty || (item.quantity + ' ' + (item.unit || ''))}</span>
                ${item.cost !== undefined ? `<span class="grocery-item-cost">₹${item.cost.toFixed(0)}</span>` : ''}
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }
    catContainer.innerHTML = html;
  }

  // Budget progress update
  if (og.budget_status) {
    showBudgetProgress(og.budget_status);
  }

  // Pantry deductions
  if (og.pantry_deductions && og.pantry_deductions.length > 0) {
    const logEl = document.getElementById('pantryDeductionsLog');
    const listEl = document.getElementById('deductionsList');
    if (logEl && listEl) {
      logEl.style.display = 'block';
      listEl.innerHTML = og.pantry_deductions.map(d => `
        <div style="display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.05); font-size:0.85rem;">
          <span style="color:var(--text-secondary);">${d.item}</span>
          <span style="color:${d.status === 'fully_covered' ? '#10B981' : '#F59E0B'};">${d.status === 'fully_covered' ? '✓ Covered' : '◐ Partial'}</span>
        </div>
      `).join('');
    }
  }
}

// Copy / Share
function copyOptimizedList() {
  const og = window._lastOptimizedGrocery;
  if (!og || !og.categories) return;
  let text = '🛒 Grocery List\n\n';
  for (const [cat, items] of Object.entries(og.categories)) {
    if (!items || items.length === 0) continue;
    text += `📦 ${cat}\n`;
    items.forEach(i => { text += `  • ${i.name}: ${i.display_qty || i.quantity}\n`; });
    text += '\n';
  }
  if (og.cost_summary) text += `💰 Total: ₹${og.cost_summary.total.toFixed(0)}\n`;
  navigator.clipboard.writeText(text).then(() => alert('Grocery list copied!'));
}

function shareOptimizedList() {
  const og = window._lastOptimizedGrocery;
  if (!og || !og.categories) return;
  let text = '🛒 *Grocery List*%0A%0A';
  for (const [cat, items] of Object.entries(og.categories)) {
    if (!items || items.length === 0) continue;
    text += `*${cat}*%0A`;
    items.forEach(i => { text += `  • ${i.name}: ${i.display_qty || i.quantity}%0A`; });
    text += '%0A';
  }
  window.open(`https://wa.me/?text=${text}`, '_blank');
}


// ═══════════════════════════════════════════════════════════════
// 📷 IMAGE-BASED INGREDIENT DETECTION
// ═══════════════════════════════════════════════════════════════

let _detectedIngredients = [];

// Drag & Drop setup — bind after DOM load
document.addEventListener('DOMContentLoaded', () => {
  const zone = document.getElementById('imageDropZone');
  if (!zone) return;
  ['dragenter', 'dragover'].forEach(evt => {
    zone.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); zone.classList.add('drag-over'); });
  });
  ['dragleave', 'drop'].forEach(evt => {
    zone.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); zone.classList.remove('drag-over'); });
  });
  zone.addEventListener('drop', e => {
    const files = e.dataTransfer.files;
    if (files.length > 0) processImageUpload(files[0]);
  });
});

function handleImageSelect(event) {
  const file = event.target.files[0];
  if (file) processImageUpload(file);
}

async function processImageUpload(file) {
  // Validate
  const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
  if (!validTypes.includes(file.type)) {
    alert('Please upload a JPG, PNG, or WebP image.');
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    alert('Image too large. Max 10MB.');
    return;
  }

  // Show preview
  const preview = document.getElementById('imagePreview');
  const content = document.getElementById('dropZoneContent');
  const overlay = document.getElementById('imageDetectionOverlay');
  const detected = document.getElementById('detectedIngredientsArea');

  const reader = new FileReader();
  reader.onload = (e) => {
    preview.src = e.target.result;
    preview.style.display = 'block';
    content.style.display = 'none';
  };
  reader.readAsDataURL(file);

  // Show loading
  overlay.style.display = 'flex';
  detected.style.display = 'none';

  // Send to API
  const formData = new FormData();
  formData.append('image', file);

  try {
    const res = await fetch('/api/detect-ingredients', { method: 'POST', body: formData });
    const data = await res.json();

    overlay.style.display = 'none';

    if (data.error) {
      alert('Detection failed: ' + data.error);
      return;
    }

    _detectedIngredients = data.detected_items || [];
    renderDetectedChips(_detectedIngredients);

    // Scene description
    const sceneEl = document.getElementById('sceneDescription');
    if (sceneEl) sceneEl.textContent = data.scene_description || '';

    detected.style.display = 'block';
    detected.style.animation = 'fadeSlideIn 0.4s ease-out';
  } catch (err) {
    overlay.style.display = 'none';
    console.error('Image detection error:', err);
    alert('Failed to analyze image. Please try again.');
  }
}

function renderDetectedChips(items) {
  const container = document.getElementById('detectedChipsContainer');
  if (!container) return;
  container.innerHTML = items.map((item, i) => {
    const pct = Math.round(item.confidence * 100);
    const color = pct >= 90 ? '#10B981' : pct >= 70 ? '#F59E0B' : '#EF4444';
    return `
      <div class="detected-chip animate-in" style="animation-delay: ${i * 0.05}s;">
        <span class="detected-chip-name">${item.name}</span>
        <span class="detected-chip-conf" style="background: ${color}20; color: ${color};">${pct}%</span>
        <span class="detected-chip-cat">${item.category}</span>
      </div>
    `;
  }).join('');
}

function useDetectedIngredients() {
  if (_detectedIngredients.length === 0) return;
  const names = _detectedIngredients
    .filter(i => i.confidence >= 0.5)
    .map(i => i.name)
    .join(', ');
  const ingredientInput = document.getElementById('ingredient');
  if (ingredientInput) {
    ingredientInput.value = names;
    ingredientInput.style.animation = 'none';
    ingredientInput.offsetHeight;
    ingredientInput.style.animation = 'glowPulse 0.6s ease-out';
  }
}


// ═══════════════════════════════════════════════════════════════
// 🎤 VOICE INPUT INTEGRATION (Web Speech API)
// ═══════════════════════════════════════════════════════════════

let _voiceRecognition = null;
let _voiceActive = false;

function startVoiceInput(targetFieldId) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert('Voice input is not supported in this browser. Please use Chrome or Edge.');
    return;
  }

  // Toggle off if already active
  if (_voiceActive && _voiceRecognition) {
    _voiceRecognition.stop();
    return;
  }

  _voiceRecognition = new SpeechRecognition();
  _voiceRecognition.continuous = false;
  _voiceRecognition.interimResults = true;
  _voiceRecognition.lang = 'en-US';
  _voiceActive = true;

  // UI feedback
  const btn = document.getElementById('micBtnIngredient');
  if (btn) btn.classList.add('recording');
  showVoiceToast('🎤 Listening... Speak now');

  _voiceRecognition.onresult = (event) => {
    let transcript = '';
    for (let i = 0; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
    }

    // Show live transcript
    showVoiceToast(`🎤 "${transcript}"`);

    // On final result, process the command
    if (event.results[event.results.length - 1].isFinal) {
      processVoiceResult(transcript.trim(), targetFieldId);
    }
  };

  _voiceRecognition.onerror = (event) => {
    console.error('Voice recognition error:', event.error);
    if (event.error === 'no-speech') {
      showVoiceToast('No speech detected. Try again.', 2000);
    } else {
      showVoiceToast(`Voice error: ${event.error}`, 2000);
    }
    stopVoiceUI();
  };

  _voiceRecognition.onend = () => {
    stopVoiceUI();
  };

  _voiceRecognition.start();
}

function stopVoiceUI() {
  _voiceActive = false;
  const btn = document.getElementById('micBtnIngredient');
  if (btn) btn.classList.remove('recording');
}

function processVoiceResult(transcript, targetFieldId) {
  // Try to parse as a smart command first
  const parsed = parseVoiceCommand(transcript);

  if (parsed.hasSmartFields) {
    // Auto-fill form fields
    if (parsed.diet) {
      const pref = document.getElementById('preference');
      if (pref) {
        const opt = [...pref.options].find(o => o.value.toLowerCase().includes(parsed.diet.toLowerCase()));
        if (opt) pref.value = opt.value;
      }
    }
    if (parsed.goal) {
      const goalEl = document.getElementById('goal');
      if (goalEl) {
        const opt = [...goalEl.options].find(o => o.text.toLowerCase().includes(parsed.goal.toLowerCase()) || o.value.toLowerCase().includes(parsed.goal.toLowerCase()));
        if (opt) goalEl.value = opt.value;
      }
    }
    if (parsed.ingredient) {
      const el = document.getElementById(targetFieldId);
      if (el) el.value = parsed.ingredient;
    }
    showVoiceToast(`✅ Filled: ${parsed.summary}`, 3000);
  } else {
    // Plain text — just fill the target field
    const el = document.getElementById(targetFieldId);
    if (el) el.value = transcript;
    showVoiceToast(`✅ "${transcript}"`, 2000);
  }
}

function parseVoiceCommand(transcript) {
  const lower = transcript.toLowerCase();
  const result = { hasSmartFields: false, diet: null, goal: null, ingredient: null, summary: '' };

  // Diet patterns
  const dietMap = {
    'vegetarian': 'Vegetarian', 'veg': 'Vegetarian', 'vegan': 'Vegan',
    'keto': 'Keto', 'paleo': 'Paleo', 'gluten free': 'Gluten-Free', 'gluten-free': 'Gluten-Free',
    'non veg': 'Non-Vegetarian', 'non-veg': 'Non-Vegetarian', 'non vegetarian': 'Non-Vegetarian',
    'high protein': 'High-Protein', 'balanced': 'Balanced'
  };
  for (const [key, value] of Object.entries(dietMap)) {
    if (lower.includes(key)) { result.diet = value; result.hasSmartFields = true; break; }
  }

  // Goal patterns
  const goalMap = {
    'weight loss': 'Weight Loss', 'lose weight': 'Weight Loss', 'slim': 'Weight Loss',
    'muscle gain': 'Muscle Gain', 'build muscle': 'Muscle Gain', 'bulk': 'Muscle Gain',
    'energy': 'Energy Boost', 'energy boost': 'Energy Boost',
    'sleep': 'Better Sleep', 'better sleep': 'Better Sleep',
    'general health': 'Nutrient Dense', 'healthy': 'Nutrient Dense'
  };
  for (const [key, value] of Object.entries(goalMap)) {
    if (lower.includes(key)) { result.goal = value; result.hasSmartFields = true; break; }
  }

  // Meal type / time patterns → extract as ingredient/context
  const mealPatterns = /\b(breakfast|lunch|dinner|snack|brunch|dessert)\b/i;
  const mealMatch = lower.match(mealPatterns);

  // Known ingredients extraction — remove diet/goal words and extract remaining food words
  const foodWords = lower
    .replace(/\b(high protein|low calorie|low carb|weight loss|muscle gain|energy boost|better sleep|general health|vegetarian|vegan|keto|paleo|gluten free|non veg|balanced|under \d+ calories?|breakfast|lunch|dinner|snack)\b/gi, '')
    .replace(/\b(give me|make me|i want|prepare|cook|recipe for|recipe|a|an|the|some|with|and|for|please)\b/gi, '')
    .trim();

  if (foodWords.length > 1) {
    result.ingredient = foodWords.replace(/\s+/g, ' ').trim();
    result.hasSmartFields = true;
  } else if (mealMatch) {
    result.ingredient = mealMatch[1];
    result.hasSmartFields = true;
  }

  // Build summary
  const parts = [];
  if (result.diet) parts.push(`Diet: ${result.diet}`);
  if (result.goal) parts.push(`Goal: ${result.goal}`);
  if (result.ingredient) parts.push(`Ingredient: ${result.ingredient}`);
  result.summary = parts.join(' | ');

  return result;
}

// Voice toast notification
let _voiceToastTimer = null;
function showVoiceToast(message, duration = 4000) {
  let toast = document.getElementById('voiceToast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'voiceToast';
    toast.className = 'voice-toast';
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(_voiceToastTimer);
  _voiceToastTimer = setTimeout(() => toast.classList.remove('show'), duration);
}


// ═══════════════════════════════════════════════════════════════
// 🏷️ CUISINE & DIETARY FILTER SYSTEM
// ═══════════════════════════════════════════════════════════════

function toggleFilter(chipEl) {
  chipEl.classList.toggle('active');
}

function getActiveFilters() {
  const cuisines = [];
  const dietary = [];
  document.querySelectorAll('.filter-chip.active').forEach(chip => {
    const type = chip.dataset.filterType;
    const value = chip.dataset.filterValue;
    if (type === 'cuisine') cuisines.push(value);
    else if (type === 'dietary') dietary.push(value);
  });
  return { cuisines, dietary };
}

function clearAllFilters() {
  document.querySelectorAll('.filter-chip.active').forEach(chip => {
    chip.classList.remove('active');
  });
}

// ═══════════════════════════════════════════════════════════════
// 📊 LOGIN HISTORY
// ═══════════════════════════════════════════════════════════════

async function fetchHistoryData() {
  const tbody = document.getElementById('historyTableBody');
  if (!tbody) return;

  try {
    const res = await fetch('/api/history');
    const data = await res.json();

    if (data.error) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:40px; color:var(--text-tertiary);">Unable to load history: ${data.error}</td></tr>`;
      return;
    }

    const history = data.history || [];

    if (history.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:40px; color:var(--text-tertiary);"><i class="fas fa-clock-rotate-left" style="font-size:2rem; display:block; margin-bottom:12px; opacity:0.3;"></i>No login history yet. Your session data will appear here.</td></tr>`;
      return;
    }

    tbody.innerHTML = history.map((entry, i) => {
      const isActive = entry.logout_time === 'Active';
      const statusBadge = isActive
        ? '<span style="background:rgba(16,185,129,0.15); color:#10b981; padding:2px 8px; border-radius:20px; font-size:0.75rem; font-weight:600;">● Active</span>'
        : `<span style="color:var(--text-secondary);">${entry.logout_time || 'N/A'}</span>`;

      // Format features as small tags
      const features = entry.features || 'Logged In';
      const featureTags = features.split(', ').map(f =>
        `<span style="display:inline-block; background:rgba(99,102,241,0.1); color:var(--accent-primary); padding:2px 8px; border-radius:12px; font-size:0.72rem; margin:2px 2px;">${f}</span>`
      ).join('');

      return `
        <tr style="animation: fadeSlideIn 0.3s ease-out ${i * 0.05}s both;">
          <td style="font-weight:500; color:var(--text-primary);">
            <i class="fas fa-calendar-day" style="color:var(--accent-primary); margin-right:6px; opacity:0.7;"></i>${entry.date || 'N/A'}
          </td>
          <td style="color:var(--text-secondary);">
            <i class="fas fa-right-to-bracket" style="color:#10b981; margin-right:6px; opacity:0.7;"></i>${entry.login_time || 'N/A'}
          </td>
          <td>${statusBadge}</td>
          <td style="color:var(--text-secondary);">
            <i class="fas fa-stopwatch" style="color:var(--accent-warning); margin-right:6px; opacity:0.7;"></i>${entry.duration || 'N/A'}
          </td>
          <td style="max-width:300px;">${featureTags}</td>
        </tr>
      `;
    }).join('');

  } catch (err) {
    console.error('Failed to fetch history:', err);
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:40px; color:var(--text-tertiary);">Failed to load history. Please try again.</td></tr>`;
  }
}

// ═══════════════════════════════════════════════════════════════
// 🌐 LANGUAGE LISTENER
// ═══════════════════════════════════════════════════════════════

function initLanguageListener() {
  // Placeholder for language change handling
  const langSelect = document.getElementById('languageSelect');
  if (langSelect) {
    langSelect.addEventListener('change', () => {
      console.log('Language changed to:', langSelect.value);
    });
  }
}
