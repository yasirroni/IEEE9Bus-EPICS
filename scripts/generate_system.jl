using PowerSystems
using PowerSystemCaseBuilder

sys = System("raw_data/ieee9_v32.raw")
rts_sys = build_system(PSISystems, "modified_RTS_GMLC_DA_sys_noForecast"; force_build = true)

function update_operation_cost!(sys, rts_sys)
    gen_names = ["generator-1-1", "generator-2-1", "generator-3-1"]
    rts_gen_names = ["101_STEAM_4", "213_CT_1", "321_CC_1"]
    for (ix, gen_name) in enumerate(gen_names)
        gen = get_component(ThermalStandard, sys, gen_name)
        rts_gen = get_component(ThermalStandard, rts_sys, rts_gen_names[ix])
        mid_slope = rts_gen.operation_cost.variable.value_curve.function_data.y_coords[2]
        fuel_cost = rts_gen.operation_cost.variable.fuel_cost
        new_op_cost = ThermalGenerationCost(
            variable = CostCurve(
                value_curve = LinearCurve(mid_slope * fuel_cost),
                power_units = rts_gen.operation_cost.variable.power_units,
                vom_cost = rts_gen.operation_cost.variable.vom_cost,
            ),
            fixed = rts_gen.operation_cost.fixed,
            start_up = rts_gen.operation_cost.start_up,
            shut_down = rts_gen.operation_cost.shut_down,
        )
        set_operation_cost!(gen, new_op_cost)
    end
end

function add_load_time_series!(sys, rts_sys)
    load_names = ["load51", "load61", "load81"]
    rts_load_names = ["Alder", "Bacon", "Caesar"]
    for (ix, load_name) in enumerate(load_names)
        load = get_component(StandardLoad, sys, load_name)
        rts_load = get_component(PowerLoad, rts_sys, rts_load_names[ix])
        ts_array = get_time_series_array(SingleTimeSeries, rts_load, "max_active_power"; ignore_scaling_factors = true)
        add_time_series!(sys, load, SingleTimeSeries(; name = "max_active_power", data = ts_array, scaling_factor_multiplier = get_max_active_power))
    end
end

set_units_base_system!(sys, "NATURAL_UNITS")
add_load_time_series!(sys, rts_sys)
update_operation_cost!(sys, rts_sys)
to_json(sys, "saved_systems/ieee9_sienna.json"; force=true)