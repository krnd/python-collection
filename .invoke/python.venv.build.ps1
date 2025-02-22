#Requires -Version 5.1


# ################################ VARIABLES ###################################

$script:__InvokeBuild::Builder["python.venv"] = @{
    LockfileExtension = @{
        ".in"  = ".txt"
        ".pip" = ".lock"
    }
}


# ################################ CONFIGURATION ###############################

CONFIGURE python.venv.shorthands `
    -Default $true

CONFIGURE python.venv.version `
    -Default "default"
CONFIGURE python.venv.path `
    -Default ".venv"

CONFIGURE python.venv.requirements `
    -Default "requirements.txt"
CONFIGURE python.venv.compilants `
    -Default @()


# ################################ SHORTHANDS ##################################

INVOKEBUILD:SETUP {
    if (CONF python.venv.shorthands) {
        if (__InvokeBuild::IsTaskMissing "..") {
            TASK .. python:venv:activate
        }
    }
}


# ################################ TASKS #######################################

TASK python:venv:activate {
    EXEC {
        & (Join-Path `
            (CONF python.venv.path) `
            (Join-Path "Scripts" "Activate.ps1")
        )
    }
}

TASK python:venv:deactivate {
    try { deactivate } catch {}
}

TASK python:venv:setup `
    python:venv:create, `
    python:venv:compile, `
    python:venv:install

TASK python:venv:create python:venv:deactivate, {
    $Version = (CONF python.venv.version)
    $Environment = (CONF python.venv.path)
    if (-not (Test-Path $Environment -PathType Container)) {
        if ($Version -and ($Version -ne "default")) {
            EXEC { py -$Version -m venv $Environment }
        } else {
            EXEC { py -m venv $Environment }
        }
    }
}, python:venv:activate, {
    EXEC {
        python `
            -m pip install pip `
            --upgrade `
            --quiet
    }
    EXEC {
        python `
            -m pip install pip-tools `
            --upgrade `
            --quiet
    }
}

TASK python:venv:compile python:venv:activate, {
    $INVOKE = $script:__InvokeBuild
    $BUILDER = $INVOKE::Builder["python.venv"]

    $Compilants = (CONF python.venv.compilants)

    $Requirements = (CONF python.venv.requirements)
    $Extension = [IO.Path]::GetExtension($Requirements)
    foreach ($Item in $BUILDER.LockfileExtension.GetEnumerator()) {
        if ($Item.Value -eq $Extension) {
            $Requirements = [IO.Path]::ChangeExtension(
                $Requirements,
                $Item.Name)
            $Extension = $null
        } elseif ($Item.Name -eq $Extension) {
            $Extension = $null
        }
    }
    if ($null -ne $Extension) {
        # Unable to revert extension of requirements file.
    } elseif (Test-Path $Requirements -PathType Leaf) {
        $Compilants += $Requirements
    }

    $Compilants | ForEach-Object {
        $File = (Get-Item $_)
        $Lockfile = [IO.Path]::ChangeExtension(
            $File.FullName,
            $BUILDER.LockfileExtension[$File.Extension])
        EXEC {
            pip-compile $File.FullName `
                --output-file $Lockfile `
                --strip-extras `
                --no-header `
                --no-annotate `
                --quiet
        }
    }
}

TASK python:venv:install python:venv:activate, {
    $Requirements = (CONF python.venv.requirements)
    if (Test-Path $Requirements -PathType Leaf) {
        EXEC {
            pip install `
                --requirement $Requirements `
                --quiet
        }
    }
}

TASK python:venv:reinstall python:venv:activate, {
    EXEC {
        python `
            -m pip install pip `
            --force-reinstall `
            --upgrade `
            --quiet
    }
    EXEC {
        python `
            -m pip install pip-tools `
            --force-reinstall `
            --upgrade `
            --quiet
    }
}, {
    $Requirements = (CONF python.venv.requirements)
    if (Test-Path $Requirements -PathType Leaf) {
        EXEC {
            pip install `
                --requirement $Requirements `
                --force-reinstall `
                --upgrade `
                --quiet
        }
    }
}

TASK python:venv:purge python:venv:deactivate, {
    REMOVE (CONF python.venv.path)
}
