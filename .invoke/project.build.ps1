#Requires -Version 5.1


# ################################ TASKS #######################################

# ###################### SETUP #############################

TASK setup          python:venv:setup


# ###################### TEST ##############################

TASK test           python:test:all


# ###################### CLEAN #############################

TASK clean          python:test:clean
TASK purge          clean, python:venv:clean
