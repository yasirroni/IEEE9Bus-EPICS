# Test System EPICS: IEEE-9-Bus

The following repository contains operational data for the IEEE 9-bus system:

<div align="center"> <img src="images/9bus.jpg"  height ="347"width="474" alt="9bus"></img></div>

## Original Data

The original data in PSS/E format `.raw` is provided in `raw_data/scenarios/original` folder. The original power flow data has three thermal units with a total capacity 820 MW and a total load of 315 MW.
 
Additional scenarios are provided in the `raw_data/scenarios` folder, with extra load added (418, 487, 625, 763 MW) with feasible AC power flow. Basic dynamic data is provided in the file `raw_data/RTS_CtrlsModified_STAB1.dyr`.

## Modified System

A modified system is provided on which unit 1 of 250 MW, is replaced by two generic renewable units of 125 MW using the files `raw_data/scenarios/RTS_Esc487MW_RE.raw` with dynamic data in `raw_data/RTS_CtrlsModified_RE.dyr`.

## Production Cost Modeling Data

The system is enhanced using load profiles and thermal costs from the [RTS dataset](https://github.com/GridMod/RTS-GMLC). This is done the Sienna platform, particularly [PowerSystems.jl](github.com/NREL-Sienna/PowerSystems.jl) and [PowerSimulations.jl](https://github.com/NREL-Sienna/PowerSimulations.jl).