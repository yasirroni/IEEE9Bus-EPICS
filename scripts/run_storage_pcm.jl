using PowerSystems
using PowerSystemCaseBuilder
using PowerSimulations
using StorageSystemsSimulations
using Dates
using HiGHS
using PlotlyJS

sys = System("saved_systems/ieee9_sienna_with_storage.json")
transform_single_time_series!(sys, Hour(72), Hour(24))
p_flow_load = sum(get_max_active_power.(get_components(StandardLoad, sys))) 
th_max_power = sum(get_max_active_power.(get_components(ThermalStandard, sys)))

solver = optimizer_with_attributes(HiGHS.Optimizer)
template = ProblemTemplate(CopperPlatePowerModel)
set_device_model!(template, StandardLoad, StaticPowerLoad)
set_device_model!(template, ThermalStandard, ThermalDispatchNoMin)
set_device_model!(template, RenewableDispatch, RenewableFullDispatch)
set_device_model!(template, EnergyReservoirStorage, StorageDispatchWithReserves)
#set_device_model!(template, ThermalStandard, ThermalBasicUnitCommitment)

models = SimulationModels(;
    decision_models = [
        DecisionModel(template, sys; optimizer = solver, name = "UC"),
    ],
)

feedforward = Dict()
sequence = SimulationSequence(;
    models = models,
    ini_cond_chronology = InterProblemChronology(),
    feedforwards = feedforward,
)

sim = Simulation(;
    name = "ieee9-test",
    steps = 360,
    models = models,
    sequence = sequence,
    simulation_folder = mktempdir(),
    #initial_time = DateTime("2020-07-01T00:00:00"),
)

build!(sim)
execute!(sim; enable_progress_bar = true)
results = SimulationResults(sim);
uc_results = get_decision_problem_results(results, "UC")
p_th = read_realized_variable(uc_results, "ActivePowerVariable__ThermalStandard")
p_load = read_realized_parameter(uc_results, "ActivePowerTimeSeriesParameter__StandardLoad")
p_re = read_realized_variable(uc_results, "ActivePowerVariable__RenewableDispatch")
p_bat_out = read_realized_variable(uc_results, "ActivePowerOutVariable__EnergyReservoirStorage")
p_bat_in = read_realized_variable(uc_results, "ActivePowerInVariable__EnergyReservoirStorage")
p_bat = p_bat_out[!, "Storage_Bus_1"] .- p_bat_in[!, "Storage_Bus_1"]
soc = read_realized_variable(uc_results, "EnergyVariable__EnergyReservoirStorage")[!, "Storage_Bus_1"]
cost_th = read_realized_expression(uc_results, "ProductionCostExpression__ThermalStandard")
total_cost = sum(cost_th[!, "generator-3-1"]) + sum(cost_th[!, "generator-2-1"])

tstamp = p_th[!, 1]
#p_gen1 = p_th[!, "generator-1-1"]
p_gen2 = p_th[!, "generator-2-1"]
p_gen3 = p_th[!, "generator-3-1"]
p_gen_pv = p_re[!, "PV_Bus_1"]
p_gen_wind = p_re[!, "Wind_Bus_1"]
p_load5 = -p_load[!, "load51"]
p_load6 = -p_load[!, "load61"]
p_load8 = -p_load[!, "load81"]
total_p_load = p_load5 + p_load6 + p_load8

plot([
    scatter(
        x = tstamp,
        y = p_gen_pv,
        mode = "lines",
        name = "PV Gen",
        line = attr(color = "gold"),
    ),
    scatter(
        x = tstamp,
        y = p_gen_wind,
        mode = "lines",
        name = "Wind Gen",
        line = attr(color = "green"),
    ),
    scatter(
        x = tstamp,
        y = p_gen2,
        mode = "lines",
        name = "CT Gen",
        line = attr(color = "blue"),
    ),
    scatter(
        x = tstamp,
        y = p_gen3,
        mode = "lines",
        name = "CC Gen",
        line = attr(color = "red"),
    ),
    scatter(
        x = tstamp,
        y = p_bat,
        mode = "lines",
        name = "Battery Gen",
        line = attr(color = "purple"),
    ),
    scatter(
        x = tstamp,
        y = total_p_load,
        mode = "lines",
        name = "Total Load",
        line = attr(color = "black", dash = "dot"),
    )
], Layout(
        yaxis_title="Active Power [MW]",
        title = "Gas, Storage, PV and Wind case: Total Cost $(round(total_cost, digits=1))",
    ),
)

plot([
    scatter(
        x = tstamp,
        y = soc,
        mode = "lines",
        name = "Storage SoC",
        line = attr(color = "red"),
    ),
], Layout(
        yaxis_title="Energy [MWh]",
        title = "Gas, Storage, PV and Wind case: Total Cost $(round(total_cost, digits=1))",
    ),
)
