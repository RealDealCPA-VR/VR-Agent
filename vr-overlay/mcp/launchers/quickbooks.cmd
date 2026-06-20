@echo off
REM VRAGENT launcher for the QuickBooks Desktop MCP server.
REM Runs from the project dir (Hermes MCP config has no cwd key).
REM Default = SIMULATION mode (safe, in-memory mock books).
REM For LIVE books: set QB_LIVE=1 and QB_COMPANY_FILE below, and have
REM QuickBooks Desktop open with the company file. (Node 20.x required for live.)
REM   set QB_LIVE=1
REM   set QB_COMPANY_FILE=C:\path\to\company.qbw
cd /d "C:\Users\VR\Projects\Quickbooks MCP Desktop"
node dist\index.js %*
