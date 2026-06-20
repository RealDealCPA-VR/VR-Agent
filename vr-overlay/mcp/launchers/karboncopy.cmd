@echo off
REM VRAGENT launcher for the KarbonCopy MCP server (practice management).
REM Runs from the project dir so DATABASE_URL=file:./data/... and .env.local
REM (KARBONCOPY_API_KEY, APP_ENCRYPTION_KEY) resolve correctly.
cd /d "C:\Users\VR\Projects\KarbonCopy"
node_modules\.bin\tsx --tsconfig tsconfig.server.json src\mcp\server.ts %*
