import { defineConfig } from "vite";

export default defineConfig({
    server: {
    proxy: {
        "/api": {
            target: "http://facturas-api:3000",
            changeOrigin: true,
            secure: false,
            ws: true,
        },
    },
    },
});
