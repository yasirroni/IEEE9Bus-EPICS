using Pkg
Pkg.activate(".")
Pkg.instantiate()

using PowerSimulationsDynamics
using PowerSystems
using Logging
using PowerFlows
using Sundials
using PlotlyJS
using PowerNetworkMatrices
using SparseArrays
using PowerSystemCaseBuilder
const PSY = PowerSystems
const PSID = PowerSimulationsDynamics
const PF = PowerFlows

######################
### Data Exploring ###
######################

raw_path = "raw_data/Escenario_Modified_MaxGen/RTS_NEW_ESC2.raw"
dyr_path = "raw_data/Escenario_Modified_MaxGen/RTS_NEW_ESC2.dyr"
sys = System(raw_path, dyr_path)

# Show data names
show_components(Source, sys)
show_components(ThermalStandard, sys)
show_components(Line, sys)

inf_bus = get_component(Source, sys, "generator-101-1")
static_gen = get_component(ThermalStandard, sys, "generator-102-1")
dyn_gen = get_dynamic_injector(static_gen)

########################
### Simulation Setup ###
########################

#### BranchTrip ####
time_span = (0.0, 30.0)
perturbation_trip = BranchTrip(1.0, Line, "BUS 1-BUS 2-i_2")

sim = Simulation(
    ResidualModel, # Type of formulation: Residual for using Sundials with IDA
    sys, # System
    mktempdir(), # Output directory
    time_span,
    perturbation_trip;
    console_level = Logging.Debug
)

show_states_initial_value(sim)