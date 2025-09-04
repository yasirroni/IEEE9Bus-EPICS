using PowerSystems
using PowerSystemCaseBuilder

sys = build_system(PSISystems, "RTS_GMLC_DA_sys_noForecast"; force_build = true)
set_units_base_system!(sys, "NATURAL_UNITS")

show_components(ThermalStandard, sys, [:active_power_limits])

th_names = sort(get_name.(get_components(ThermalStandard, sys)))
for name in th_names
    gen = get_component(ThermalStandard, sys, name)
    println("Name: ", name, ", Rating: ", get_rating(gen))
end

th_total = sum(get_rating.(get_components(ThermalStandard, sys)))

re_names = sort(get_name.(get_components(RenewableDispatch, sys)))
for name in re_names
    gen = get_component(RenewableDispatch, sys, name)
    println("Name: ", name, ", Active Power Limits: ", get_rating(gen))
end

re_total = sum(get_max_active_power.(get_components(ThermalStandard, sys)))

total_load = sum(get_max_active_power.(get_components(PowerLoad, sys)))
