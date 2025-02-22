#Requires -Version 5.1


# ################################ VARIABLES ###################################

$script:__InvokeBuild::Plugin::Argument = @{
    File   = $MyInvocation.MyCommand.Name
    Prefix = "ARGUMENT"
}


# ################################ FUNCTIONS ###################################

function __InvokeBuild::Plugin::Argument::*GET {
    [CmdletBinding(PositionalBinding = $false, DefaultParameterSetName = "Any")]
    param (
        [Parameter(Mandatory, Position = 0)]
        [string]
        $Name,
        [Parameter(Position = 1)]
        [AllowNull()]
        [object]
        $Default,
        [Parameter(Mandatory, ParameterSetName = "Test")]
        [switch]
        $Test,
        [Parameter(Mandatory, ParameterSetName = "Switch")]
        [switch]
        $Switch,
        [Parameter(Mandatory, ParameterSetName = "Boolean")]
        [switch]
        $Boolean,
        [Parameter(Mandatory, ParameterSetName = "Number")]
        [switch]
        $Number,
        [Parameter(Mandatory, ParameterSetName = "String")]
        [switch]
        $String,
        [Parameter(ParameterSetName = "Any")]
        [Parameter(ParameterSetName = "Boolean")]
        [Parameter(ParameterSetName = "Number")]
        [Parameter(ParameterSetName = "String")]
        [switch]
        $Required
    )
    $INVOKE = $script:__InvokeBuild
    $PLUGIN = $INVOKE::Plugin::Argument
    $ARGUMENTS = $INVOKE::Arguments

    if (-not $ARGUMENTS) {
        if ($Test) {
            return $false
        } elseif ($Switch) {
            return $false
        } elseif (-not $Required) {
            return $Default
        } elseif ($null -ne $Default) {
            return $Default
        }
        throw "[$($PLUGIN::Prefix):GET] " `
            + "Argument '$Name' not found."
    }

    $Index = $ARGUMENTS.IndexOf("-$Name")
    if ($Test) {
        return ($Index -ge 0)
    } elseif ($Switch) {
        return ($Index -ge 0)
    } elseif ($Index -lt 0) {
        if (-not $Required) {
            return $Default
        } elseif ($null -ne $Default) {
            return $Default
        }
        throw "[$($PLUGIN::Prefix):GET] " `
            + "Argument '$Name' not found."
    }

    if (($Index + 1) -ge $ARGUMENTS.Length) {
        throw "[$($PLUGIN::Prefix):GET] " `
            + "Argument '$Name' has no value."
    }

    $RawValue = $ARGUMENTS[$Index + 1]
    if ($Boolean) {
        $Value = $RawValue -as [boolean]
    } elseif ($Number) {
        $Value = $RawValue -as [double]
        if ($Value -eq ($Value -as [int])) {
            $Value = $Value -as [int]
        }
    } elseif ($String) {
        $Value = $RawValue -as [string]
    } else {
        $Value = $RawValue
    }

    return $Value
}

Set-Alias ARGUMENT:GET __InvokeBuild::Plugin::Argument::*GET
Set-Alias ARG __InvokeBuild::Plugin::Argument::*GET
