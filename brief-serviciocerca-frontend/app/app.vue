<template>
  <div class="app-layout">
    <nav class="app-nav">
      <div class="nav-container">
        <NuxtLink
          to="/"
          class="nav-brand"
        >
          ServicioCerca
        </NuxtLink>

        <div class="nav-links">
          <NuxtLink
            to="/"
            class="nav-link"
            active-class="nav-link-active"
          >
            Red de cobertura
          </NuxtLink>
        </div>
      </div>
    </nav>

    <main class="app-main">
      <NuxtPage />
    </main>

    <footer class="app-footer">
      <div class="nav-container">
        ServicioCerca — Demo de gestión de cobertura técnica
      </div>
    </footer>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-nav {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  width: min(1200px, 100%);
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 14px 0;
}

.nav-brand {
  font-weight: 800;
  font-size: 1.2rem;
  color: #111827;
  text-decoration: none;
  letter-spacing: -0.02em;
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-link {
  padding: 8px 14px;
  border-radius: 8px;
  color: #4b5563;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.nav-link:hover {
  background: #f3f4f6;
  color: #111827;
}

.nav-link-active {
  background: #111827;
  color: white;
}

.nav-link-active:hover {
  background: #374151;
  color: white;
}

.app-main {
  flex: 1;
}

.app-footer {
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  color: #6b7280;
  font-size: 0.85rem;
  padding: 0 20px;
}

.app-footer .nav-container {
  justify-content: center;
  padding: 16px 0;
}

@media (max-width: 600px) {
  .nav-container {
    flex-direction: column;
    gap: 12px;
  }

  .nav-links {
    width: 100%;
  }

  .nav-link {
    flex: 1;
    text-align: center;
  }
}
</style>
