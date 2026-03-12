import { existsSync } from 'node:fs'
import { spawn } from 'node:child_process'
import path from 'node:path'
import process from 'node:process'

const repoRoot = process.cwd()
const pythonPath = path.join(repoRoot, '.venv', 'Scripts', 'python.exe')
const frontendNodeModules = path.join(repoRoot, 'frontend', 'node_modules')
const dryRun = process.argv.includes('--dry-run')

if (!existsSync(pythonPath)) {
  console.error('Missing virtual environment Python: .venv\\Scripts\\python.exe')
  console.error('Run `python -m venv .venv` and install Python dependencies first.')
  process.exit(1)
}

if (!existsSync(frontendNodeModules)) {
  console.error('Missing frontend dependencies: frontend\\node_modules')
  console.error('Run `npm install --prefix frontend` first.')
  process.exit(1)
}

const backendCommand = {
  command: pythonPath,
  args: ['-m', 'uvicorn', 'app.main:app', '--reload', '--host', '127.0.0.1', '--port', '8000'],
  options: { cwd: repoRoot, stdio: 'inherit' },
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
