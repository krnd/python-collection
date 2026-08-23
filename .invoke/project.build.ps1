#Requires -Version 5.1


# ################################ TASKS #######################################

# ###################### TEST ##############################

TASK test python:pytest:all


# ###################### ENVIRONMENT #######################

TASK env:setup python:venv:setup

TASK env:purge python:venv:purge


# ###################### STASH #############################

TASK stash {
    Start-Process "./.stash/stash.bat" `
        -WorkingDirectory "./.stash"
}
