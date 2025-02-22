#Requires -Version 5.1


# ################################ TASKS #######################################

TASK python:test:all python:venv:activate, {
    EXEC {
        pytest
    }
}

TASK python:test:clean python:venv:activate, {
    EXEC {
        pytest `
            --cache-clear
    }
}
