const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let backendProcess = null;

// Check if running in development
const isDev = !app.isPackaged;

// Log file for debugging
function log(message) {
  const logPath = path.join(app.getPath('userData'), 'app.log');
  const timestamp = new Date().toISOString();
  try {
    fs.appendFileSync(logPath, `[${timestamp}] ${message}\n`);
  } catch (e) {}
  console.log(message);
}

// Start backend server
function startBackend() {
  log(`isDev: ${isDev}, isPackaged: ${app.isPackaged}`);
  log(`resourcesPath: ${process.resourcesPath}`);
  
  if (isDev) {
    log('Development mode - backend should be started manually');
    return Promise.resolve();
  }

  // In production, start the bundled backend
  const backendPath = path.join(process.resourcesPath, 'backend', 'backend.exe');
  
  log(`Starting backend from: ${backendPath}`);
  log(`Backend exists: ${fs.existsSync(backendPath)}`);
  
  try {
    backendProcess = spawn(backendPath, [], {
      cwd: path.dirname(backendPath),
      stdio: ['ignore', 'pipe', 'pipe'],
      windowsHide: true
    });

    backendProcess.stdout.on('data', (data) => {
      log(`Backend stdout: ${data}`);
    });

    backendProcess.stderr.on('data', (data) => {
      log(`Backend stderr: ${data}`);
    });

    backendProcess.on('error', (err) => {
      log(`Failed to start backend: ${err}`);
    });

    backendProcess.on('close', (code) => {
      log(`Backend exited with code ${code}`);
      backendProcess = null;
    });

    // Wait for backend to start
    return new Promise((resolve) => setTimeout(resolve, 3000));
  } catch (error) {
    log(`Error starting backend: ${error}`);
    return Promise.resolve();
  }
}

// Stop backend server
function stopBackend() {
  if (backendProcess) {
    log('Stopping backend...');
    backendProcess.kill();
    backendProcess = null;
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    frame: false,
    transparent: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'assets', 'icon.ico'),
    title: 'Social Coach',
    show: false
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    // In production build, index.html is in the same directory
    mainWindow.loadFile(path.join(__dirname, 'index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(async () => {
  await startBackend();
  createWindow();
});

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  stopBackend();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

// Window controls
ipcMain.on('minimize-window', () => {
  mainWindow?.minimize();
});

ipcMain.on('maximize-window', () => {
  if (mainWindow?.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow?.maximize();
  }
});

ipcMain.on('close-window', () => {
  mainWindow?.close();
});
