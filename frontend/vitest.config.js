import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    globals: true,
    coverage: {
      provider: "v8",
      reporter: ["text", "html"],
      include: ["static/**/*.js"],
       exclude: [
        "tests/**",
        "node_modules/**",
        "static/main.js",
        "static/config.js",
        "static/dom.js",
        "static/state.js"
       ],
      // thresholds: {
      //   statements: 80,
      //   branches: 70,
      //   functions: 80,
      //   lines: 80
      // }
    }
  }
});