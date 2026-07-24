import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: Number(process.env.VITE_PORT) || 5173,
  },
  build: {
    sourcemap: false,
    // Don't leak source content on error overlays in dev; production
    // builds already exclude source maps.
  },
});
