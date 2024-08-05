import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  // base: "/record",
  base: "/",
  server: {
    port: 80, // default: 3000
    host: "0.0.0.0", // default: localhost
    watch: {
      ignored: ["**/coverage/**"], // goal: when the coverage folder is updated when I run the e2e test then do not do the reload. Ref: https://github.com/vitejs/vite/issues/3190
    },
  },
  preview: {
    port: 80,
  },
  build: {
    // target: "chrome106", // Size of the bundle created did not change
  },
});
