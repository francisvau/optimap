import { defineConfig } from 'vitest/config';
import path from 'node:path';
import react from '@vitejs/plugin-react-swc';

export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    build: {
        outDir: 'public',
    },
    test: {
        include: ['test/unit/**/*.{test,spec}.ts'],
    },
    server: {
        host: true,
        allowedHosts: ['optimap.local'],
        hmr: {
            clientPort: 443,
        },
    },
});
