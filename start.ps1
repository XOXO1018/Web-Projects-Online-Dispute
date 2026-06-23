# ===================================================
# 智链解纷 Windows 本地一键启动脚本 V2.0
# 用法见下方帮助信息
# ===================================================

param(
    [switch]$backend,
    [switch]$frontend,
    [switch]$all,
    [switch]$seed,
    [switch]$stop,
    [switch]$check
)

$ErrorActionPreference = "Continue"
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$BACKEND_PORT = 8000
$FRONTEND_PORT = 5173

function Test-Port($port) {
    $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }
    return $null -ne $conn
}

function Wait-For-Service($port, $maxWait = 30) {
    $waited = 0
    while (-not (Test-Port $port) -and $waited -lt $maxWait) {
        Start-Sleep -Seconds 1
        $waited++
    }
    return (Test-Port $port)
}

function Test-Health($port) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$port/api/health" -TimeoutSec 5 -UseBasicParsing
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Stop-Services {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "  正在停止服务..." -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow

    $servicesStopped = $false

    # 找出占用端口的进程并杀掉
    foreach ($port in @($BACKEND_PORT, $FRONTEND_PORT)) {
        $procs = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
            Where-Object { $_.State -eq 'Listen' } |
            Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($procId in $procs) {
            if ($procId -and $procId -ne 0) {
                try {
                    $procName = (Get-Process -Id $procId -ErrorAction SilentlyContinue).ProcessName
                    Stop-Process -Id $procId -Force
                    Write-Host "  [OK] 已停止 $port 端口进程 ($procName, PID: $procId)" -ForegroundColor Green
                    $servicesStopped = $true
                } catch {
                    Write-Host "  [ERROR] 无法停止 $port 端口进程: $_" -ForegroundColor Red
                }
            }
        }
    }

    if ($servicesStopped) {
        Write-Host ""
        Write-Host "[OK] 所有服务已停止" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "[*] 没有检测到运行中的服务" -ForegroundColor Cyan
    }
}

function Start-Backend {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  启动后端服务" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    if (Test-Port $BACKEND_PORT) {
        Write-Host "[*] 端口 $BACKEND_PORT 已被占用，跳过后端启动" -ForegroundColor Yellow
        return $true
    }

    $pythonCmd = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $pythonCmd) {
        Write-Host "[ERROR] 未找到 Python，请确认已安装并加入 PATH" -ForegroundColor Red
        return $false
    }
    Write-Host "[OK] Python: $pythonCmd" -ForegroundColor Gray

    $backendDir = Join-Path $PROJECT_ROOT "backend"
    $reqFile = Join-Path $backendDir "requirements.txt"
    
    # 检查依赖
    if (Test-Path $reqFile) {
        Write-Host "[*] 检查 Python 依赖..." -ForegroundColor Gray
        pip install -r $reqFile -q 2>&1 | Out-Null
    }

    # 数据库初始化
    if ($seed) {
        Write-Host ""
        Write-Host "[*] 初始化数据库..." -ForegroundColor Blue
        Push-Location $backendDir
        python init_db.py
        Pop-Location
        Write-Host "[OK] 数据库初始化完成" -ForegroundColor Green
    }

    # 独立进程启动后端
    $logDir = Join-Path $backendDir "logs"
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
    $logFile = Join-Path $logDir "server_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
    
    Write-Host "[*] 启动后端服务..." -ForegroundColor Gray
    Start-Process -FilePath $pythonCmd -ArgumentList "demo_server.py" `
        -WorkingDirectory $backendDir -WindowStyle Minimized -RedirectStandardOutput $logFile

    # 等待服务启动
    Write-Host "[*] 等待后端服务启动..." -ForegroundColor Gray
    if (Wait-For-Service $BACKEND_PORT 15) {
        Write-Host ""
        Write-Host "[OK] 后端已启动" -ForegroundColor Green
        Write-Host "    API文档: http://localhost:$BACKEND_PORT/api/docs" -ForegroundColor White
        Write-Host "    健康检查: http://localhost:$BACKEND_PORT/api/health" -ForegroundColor White
        return $true
    } else {
        Write-Host "[ERROR] 后端启动失败，请检查 $logFile" -ForegroundColor Red
        return $false
    }
}

function Start-Frontend {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  启动前端服务" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    if (Test-Port $FRONTEND_PORT) {
        Write-Host "[*] 端口 $FRONTEND_PORT 已被占用，跳过前端启动" -ForegroundColor Yellow
        return $true
    }

    $nodeCmd = (Get-Command node -ErrorAction SilentlyContinue).Source
    if (-not $nodeCmd) {
        # 尝试常见安装路径作为回退
        $fallbackPaths = @(
            "C:\Program Files\nodejs\node.exe",
            "C:\Program Files (x86)\nodejs\node.exe",
            "$env:APPDATA\nvm\current\node.exe"
        )
        foreach ($fp in $fallbackPaths) {
            if (Test-Path $fp) {
                $nodeCmd = $fp
                Write-Host "[OK] Node.js (fallback): $nodeCmd" -ForegroundColor Gray
                break
            }
        }
    }
    if (-not $nodeCmd) {
        Write-Host "[ERROR] 未找到 Node.js，请确认已安装并加入 PATH" -ForegroundColor Red
        return $false
    }
    Write-Host "[OK] Node.js: $nodeCmd" -ForegroundColor Gray

    $frontendDir = Join-Path $PROJECT_ROOT "frontend"
    $nodeModules = Join-Path $frontendDir "node_modules"

    # 检查 node_modules
    if (-not (Test-Path $nodeModules)) {
        Write-Host "[*] 安装前端依赖 (npm install)..." -ForegroundColor Gray
        Push-Location $frontendDir
        npm install
        Pop-Location
        Write-Host "[OK] 依赖安装完成" -ForegroundColor Green
    }

    # 启动 Vite 开发服务器
    Write-Host "[*] 启动前端服务..." -ForegroundColor Gray
    $viteBin = Join-Path $frontendDir "node_modules\vite\bin\vite.js"
    Start-Process -FilePath $nodeCmd -ArgumentList $viteBin `
        -WorkingDirectory $frontendDir -WindowStyle Minimized

    # 等待服务启动
    Write-Host "[*] 等待前端服务启动..." -ForegroundColor Gray
    if (Wait-For-Service $FRONTEND_PORT 20) {
        Write-Host ""
        Write-Host "[OK] 前端已启动" -ForegroundColor Green
        Write-Host "    访问地址: http://localhost:$FRONTEND_PORT" -ForegroundColor White
        return $true
    } else {
        Write-Host "[ERROR] 前端启动失败，请手动运行 npm run dev" -ForegroundColor Red
        return $false
    }
}

function Check-Services {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  服务状态检查" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    $allHealthy = $true
    
    # 检查后端
    Write-Host ""
    if (Test-Port $BACKEND_PORT) {
        $healthy = Test-Health $BACKEND_PORT
        if ($healthy) {
            Write-Host "[OK] 后端服务: 运行中 (健康)" -ForegroundColor Green
        } else {
            Write-Host "[!] 后端服务: 运行中 (未通过健康检查)" -ForegroundColor Yellow
            $allHealthy = $false
        }
    } else {
        Write-Host "[ERROR] 后端服务: 未运行" -ForegroundColor Red
        $allHealthy = $false
    }
    
    # 检查前端
    Write-Host ""
    if (Test-Port $FRONTEND_PORT) {
        Write-Host "[OK] 前端服务: 运行中" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] 前端服务: 未运行" -ForegroundColor Red
        $allHealthy = $false
    }
    
    Write-Host ""
    if ($allHealthy) {
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  所有服务运行正常！" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  前端:  http://localhost:$FRONTEND_PORT" -ForegroundColor White
        Write-Host "  后端:  http://localhost:$BACKEND_PORT" -ForegroundColor White
        Write-Host "  API:   http://localhost:$BACKEND_PORT/docs" -ForegroundColor White
        Write-Host ""
    }
}

# ==================== 主逻辑 ====================

if ($stop) {
    Stop-Services
    return
}

if ($check) {
    Check-Services
    return
}

if ($all) {
    # 同时启动前后端
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  智链解纷 · 一键启动服务" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    $backendOk = Start-Backend
    $frontendOk = Start-Frontend

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  启动完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    if ($backendOk) {
        Write-Host "  访问首页: http://localhost:$FRONTEND_PORT" -ForegroundColor White
        Write-Host "  API文档: http://localhost:$BACKEND_PORT/api/docs" -ForegroundColor White
    }
    if ($frontendOk) {
        Write-Host ""
        Write-Host "  演示账号: demo@zjfl.com / Demo@12345" -ForegroundColor Gray
        Write-Host "  管理账号: admin@zjfl.com / admin123" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "  常用命令:" -ForegroundColor Cyan
    Write-Host "    查看状态: .\start.ps1 -check" -ForegroundColor Gray
    Write-Host "    停止服务: .\start.ps1 -stop" -ForegroundColor Gray
    Write-Host "    重置数据: .\start.ps1 -all -seed" -ForegroundColor Gray
    Write-Host "========================================" -ForegroundColor Green
    return
}

if ($backend) {
    Start-Backend
    return
}

if ($frontend) {
    Start-Frontend
    return
}

# 无参数 --> 显示帮助
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  智链解纷 · 启动脚本 V2.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "用法:" -ForegroundColor White
Write-Host "  .\start.ps1 -all              启动前后端服务 (推荐)" -ForegroundColor Gray
Write-Host "  .\start.ps1 -backend          仅启动后端" -ForegroundColor Gray
Write-Host "  .\start.ps1 -frontend         仅启动前端" -ForegroundColor Gray
Write-Host "  .\start.ps1 -all -seed        启动并重置数据库" -ForegroundColor Gray
Write-Host "  .\start.ps1 -check            检查服务状态" -ForegroundColor Gray
Write-Host "  .\start.ps1 -stop             停止所有服务" -ForegroundColor Gray
Write-Host ""
Write-Host "快捷启动示例:" -ForegroundColor White
Write-Host "  首次运行 (重置数据库):" -ForegroundColor Yellow
Write-Host "    .\start.ps1 -all -seed" -ForegroundColor White
Write-Host ""
Write-Host "  日常启动:" -ForegroundColor Yellow
Write-Host "    .\start.ps1 -all" -ForegroundColor White
Write-Host ""
Write-Host "  查看运行状态:" -ForegroundColor Yellow
Write-Host "    .\start.ps1 -check" -ForegroundColor White
Write-Host ""
Write-Host "  停止所有服务:" -ForegroundColor Yellow
Write-Host "    .\start.ps1 -stop" -ForegroundColor White
Write-Host ""
