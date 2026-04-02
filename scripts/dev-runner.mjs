import { existsSync, readFileSync } from 'node:fs'
import { spawn, spawnSync } from 'node:child_process'
import path from 'node:path'
import process from 'node:process'

const repoRoot = process.cwd()
const frontendNodeModules = path.join(repoRoot, 'frontend', 'node_modules')
const dryRun = process.argv.includes('--dry-run')
const envFiles = ['.env.local', '.env']

function loadDotEnv(filePath) {
  if (!existsSync(filePath)) {
    return {}
  }

  const result = {}
  const lines = readFileSync(filePath, 'utf8').split(/\r?\n/)
  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('#')) {
      continue
    }

    const sep = trimmed.indexOf('=')
    if (sep <= 0) {
      continue
    }

    const key = trimmed.slice(0, sep).trim()
    let value = trimmed.slice(sep + 1).trim()
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1)
    }

    result[key] = value
  }

  return result
}

const fileEnv = {}
for (const envFile of envFiles) {
  const envPath = path.join(repoRoot, envFile)
  Object.assign(fileEnv, loadDotEnv(envPath))
}

const backendEnv = {
  ...process.env,
  ...fileEnv,
}

if (!backendEnv.APP_ENV) {
  backendEnv.APP_ENV = 'local'
}

function canExecutePython(command, args = []) {
  const probe = spawnSync(command, [...args, '-c', 'import sys; print(sys.executable)'], {
    cwd: repoRoot,
    encoding: 'utf8',
    shell: false,
  })
  return probe.status === 0
}

function resolvePythonCommand() {
  const candidates = [
    { command: path.join(repoRoot, '.venv', 'Scripts', 'python.exe'), args: [], label: '.venv\\Scripts\\python.exe' },
    { command: 'python', args: [], label: 'python' },
    { command: 'py', args: ['-3'], label: 'py -3' },
  ]

  for (const candidate of candidates) {
    if (candidate.command.endsWith('.exe') && !existsSync(candidate.command)) {
      continue
    }
    if (canExecutePython(candidate.command, candidate.args)) {
      return candidate
    }
  }

  console.error('Unable to find a working Python interpreter for backend startup.')
  console.error('Checked: .venv\\Scripts\\python.exe, python, py -3')
  process.exit(1)
}

if (!existsSync(frontendNodeModules)) {
  console.error('Missing frontend dependencies: frontend\\node_modules')
  console.error('Run `npm install --prefix frontend` first.')
  process.exit(1)
}

const pythonCommand = resolvePythonCommand()

const backendCommand = {
  command: pythonCommand.command,
  args: [...pythonCommand.args, '-m', 'uvicorn', 'app.main:app', '--reload', '--host', '127.0.0.1', '--port', '8000'],
  options: { cwd: repoRoot, stdio: 'inherit', env: backendEnv },
}

const frontendCommand = {
  command: process.platform === 'win32' ? 'npm.cmd' : 'npm',
  args: ['--prefix', 'frontend', 'run', 'dev', '--', '--host', '127.0.0.1'],
  options: { cwd: repoRoot, stdio: 'inherit' },
}

if (dryRun) {
  console.log('[DRY RUN] backend:', backendCommand.command, backendCommand.args.join(' '))
  console.log('[DRY RUN] frontend:', frontendCommand.command, frontendCommand.args.join(' '))
  process.exit(0)
}

const children = []
let shuttingDown = false

function stopChild(child) {
  if (!child || child.killed) {
    return
  }

  if (process.platform === 'win32' && child.pid) {
    spawn('taskkill', ['/pid', String(child.pid), '/t', '/f'], { stdio: 'ignore' })
    return
  }

  child.kill('SIGTERM')
}

function shutdown(exitCode = 0) {
  if (shuttingDown) {
    return
  }

  shuttingDown = true
  for (const child of children) {
    stopChild(child)
  }

  setTimeout(() => {
    process.exit(exitCode)
  }, 300)
}

function startProcess(label, descriptor) {
  const child = spawn(descriptor.command, descriptor.args, descriptor.options)
  children.push(child)

  child.on('exit', (code, signal) => {
    if (shuttingDown) {
      return
    }

    if (code === 0 || signal === 'SIGTERM') {
      console.log(`${label} exited.`)
      shutdown(0)
      return
    }

    console.error(`${label} exited unexpectedly with code ${code ?? 'unknown'}.`)
    shutdown(code ?? 1)
  })

  child.on('error', (error) => {
    if (shuttingDown) {
      return
    }

    console.error(`Failed to start ${label}: ${error.message}`)
    shutdown(1)
  })

  return child
}

console.log('Starting backend and frontend dev services...')
startProcess('backend', backendCommand)
startProcess('frontend', frontendCommand)

process.on('SIGINT', () => shutdown(0))
process.on('SIGTERM', () => shutdown(0))
