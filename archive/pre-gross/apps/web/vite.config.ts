import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const runtimeTarget =
  process.env.SIGNAL_SPACE_RUNTIME_TARGET ?? 'http://127.0.0.1:8765';
const runtimeOrigin =
  process.env.SIGNAL_SPACE_RUNTIME_ORIGIN ?? 'http://127.0.0.1:5173';

const runtimeProxy = {
  '/runtime': {
    target: runtimeTarget,
    headers: { Origin: runtimeOrigin },
    rewrite: (path: string) => path.replace(/^\/runtime/, ''),
  },
};

export default defineConfig({
  plugins: [react()],
  server: { proxy: runtimeProxy },
  preview: { proxy: runtimeProxy },
});
