using PRAS
using PowerSystems
using SiennaPRASInterface

const SPI = SiennaPRASInterface
const PSY = PowerSystems

sys = System("saved_systems/ieee9_sienna_with_renewable.json")
show_components(ACBus, sys, [:area])
pras_sys = SPI.generate_pras_system(sys, Area)
sf = assess(sys,Area,SequentialMonteCarlo(samples=100,seed=1),Shortfall())
neue = EUE(sf[1])

# Attempt to make a system with 1 NEUE, add demand response, add additional thermal or storage,
# First split generators in 3.

function split_unit_into_N_units!(sys, plant_name, N = 3)
    plant = get_component(ThermalStandard, sys, plant_name)
    for i in 1:N
        new_gen = ThermalStandard(;
            name = "$(plant.name)_$i",
            available = plant.available,
            status = plant.status,
            bus = plant.bus,
            active_power = plant.active_power / N,
            reactive_power = plant.reactive_power / N,
            rating = plant.rating / N,
            active_power_limits = (min = plant.active_power_limits.min / N, max = plant.active_power_limits.max / N),
            reactive_power_limits = (min = plant.reactive_power_limits.min / N, max = plant.reactive_power_limits.max / N),
            ramp_limits = (up = plant.ramp_limits.up / N, down = plant.ramp_limits.down / N),
            operation_cost = plant.operation_cost,
            base_power = plant.base_power,
            time_limits = plant.time_limits,
            must_run = plant.must_run,
            prime_mover_type = plant.prime_mover_type,
            fuel = plant.fuel,
        )
        add_component!(sys, new_gen)
    end
    set_available!(plant, false)
    return
end

#split_unit_into_N_units!(sys, "generator-2-1", 2)
split_unit_into_N_units!(sys, "generator-3-1", 3)

pras_sys = SPI.generate_pras_system(sys, Area)
sf = assess(sys,Area,SequentialMonteCarlo(samples=100,seed=1),Shortfall())
neue = EUE(sf[1])