"""
Critical Days Functions

This module provides functions to identify critical days/hours in power system data
based on various criteria such as thermal generation, load demand, and net load.

Each function returns a tuple of (index, timestamp, value) for the critical hour.
"""

using Dates

"""
# Example usage of critical days functions

# Assuming you have vectors of data:
# tstamp, p_thermal, p_load, p_wind, p_solar

# Find individual critical days
min_thermal_ix, min_thermal_ts, min_thermal_val = find_min_thermal_output(tstamp, p_thermal)
min_load_ix, min_load_ts, min_load_val = find_min_load_demand(tstamp, p_load)
max_load_ix, max_load_ts, max_load_val = find_max_load_demand(tstamp, p_load)
max_thermal_ix, max_thermal_ts, max_thermal_val = find_max_thermal_output(tstamp, p_thermal)
max_net_load_ix, max_net_load_ts, max_net_load_val = find_max_net_load(tstamp, p_load, p_wind, p_solar)
min_net_load_ix, min_net_load_ts, min_net_load_val = find_min_net_load(tstamp, p_load, p_wind, p_solar)

# Or find all at once
critical_days = find_all_critical_days(tstamp, p_thermal, p_load, p_wind, p_solar)
print_critical_days_summary(critical_days)

# Access specific critical day
println("Min thermal occurs at: ", critical_days["min_thermal"].timestamp)
println("Max net load value: ", critical_days["max_net_load"].value, " MW")
"""

"""
    find_min_thermal_output(tstamp::Vector{DateTime}, p_thermal::Vector{Float64}; exclude_zero=true)

Find the hour with minimum thermal output.

# Arguments
- `tstamp::Vector{DateTime}`: Vector of timestamps
- `p_thermal::Vector{Float64}`: Vector of thermal power generation values
- `exclude_zero`: If true, excludes hours with zero thermal output (default: true)

# Returns
- Tuple of (index, timestamp, thermal_value) for the hour with minimum thermal output
"""
function find_min_thermal_output(tstamp::Vector{DateTime}, p_thermal::Vector{Float64}; exclude_zero=true)
    @assert length(tstamp) == length(p_thermal) "Length of tstamp and p_thermal must be equal"
    if exclude_zero
        # Sort indices by thermal power
        sorted_ixs = sortperm(p_thermal)
        p_thermal_sorted = p_thermal[sorted_ixs]
        
        # Find first index with positive thermal output
        first_positive_ix = findfirst(x -> x > 0.0, p_thermal_sorted)
        
        if isnothing(first_positive_ix)
            error("No positive thermal output found in data")
        end
        
        # Get the actual index in original array
        min_thermal_ix = sorted_ixs[first_positive_ix]
    else
        min_thermal_ix = argmin(p_thermal)
    end
    
    return (min_thermal_ix, tstamp[min_thermal_ix], p_thermal[min_thermal_ix])
end


"""
    find_min_load_demand(tstamp::Vector{DateTime}, p_load::Vector{Float64})

Find the hour with minimum load demand.

# Arguments
- `tstamp::Vector{DateTime}`: Vector of timestamps
- `p_load::Vector{Float64}`: Vector of load demand values

# Returns
- Tuple of (index, timestamp, load_value) for the hour with minimum load demand
"""
function find_min_load_demand(tstamp::Vector{DateTime}, p_load::Vector{Float64})
    @assert length(tstamp) == length(p_load) "Length of tstamp and p_load must be equal"
    min_load_ix = argmin(p_load)
    return (min_load_ix, tstamp[min_load_ix], p_load[min_load_ix])
end


"""
    find_max_load_demand(tstamp::Vector{DateTime}, p_load::Vector{Float64})

Find the hour with maximum load demand.

# Arguments
- `tstamp::Vector{DateTime}`: Vector of timestamps
- `p_load::Vector{Float64}`: Vector of load demand values

# Returns
- Tuple of (index, timestamp, load_value) for the hour with maximum load demand
"""
function find_max_load_demand(tstamp::Vector{DateTime}, p_load::Vector{Float64})
    @assert length(tstamp) == length(p_load) "Length of tstamp and p_load must be equal"
    max_load_ix = argmax(p_load)
    return (max_load_ix, tstamp[max_load_ix], p_load[max_load_ix])
end


"""
    find_max_thermal_output(tstamp::Vector{DateTime}, p_thermal::Vector{Float64})

Find the hour with maximum thermal output.

# Arguments
- `tstamp::Vector{DateTime}`: Vector of timestamps
- `p_thermal::Vector{Float64}`: Vector of thermal power generation values

# Returns
- Tuple of (index, timestamp, thermal_value) for the hour with maximum thermal output
"""
function find_max_thermal_output(tstamp::Vector{DateTime}, p_thermal::Vector{Float64})
    @assert length(tstamp) == length(p_thermal) "Length of tstamp and p_thermal must be equal"
    max_thermal_ix = argmax(p_thermal)
    return (max_thermal_ix, tstamp[max_thermal_ix], p_thermal[max_thermal_ix])
end


"""
    find_max_net_load(tstamp::Vector{DateTime}, p_load::Vector{Float64}, p_wind::Vector{Float64}, p_solar::Vector{Float64})

Find the hour with maximum net load (load - wind - solar).

# Arguments
- `tstamp::Vector{DateTime}`: Vector of timestamps
- `p_load::Vector{Float64}`: Vector of load demand values
- `p_wind::Vector{Float64}`: Vector of wind generation values
- `p_solar::Vector{Float64}`: Vector of solar generation values

# Returns
- Tuple of (index, timestamp, net_load_value) for the hour with maximum net load
"""
function find_max_net_load(tstamp::Vector{DateTime}, p_load::Vector{Float64}, p_wind::Vector{Float64}, p_solar::Vector{Float64})
    @assert length(tstamp) == length(p_load) == length(p_wind) == length(p_solar) "All vectors must have equal length"
    p_net_load = p_load .- p_wind .- p_solar
    max_net_load_ix = argmax(p_net_load)
    return (max_net_load_ix, tstamp[max_net_load_ix], p_net_load[max_net_load_ix])
end


"""
    find_min_net_load(tstamp::Vector{DateTime}, p_load::Vector{Float64}, p_wind::Vector{Float64}, p_solar::Vector{Float64})

Find the hour with minimum net load (load - wind - solar).

# Arguments
- `tstamp::Vector{DateTime}`: Vector of timestamps
- `p_load::Vector{Float64}`: Vector of load demand values
- `p_wind::Vector{Float64}`: Vector of wind generation values
- `p_solar::Vector{Float64}`: Vector of solar generation values

# Returns
- Tuple of (index, timestamp, net_load_value) for the hour with minimum net load
"""
function find_min_net_load(tstamp::Vector{DateTime}, p_load::Vector{Float64}, p_wind::Vector{Float64}, p_solar::Vector{Float64})
    @assert length(tstamp) == length(p_load) == length(p_wind) == length(p_solar) "All vectors must have equal length"
    p_net_load = p_load .- p_wind .- p_solar
    min_net_load_ix = argmin(p_net_load)
    return (min_net_load_ix, tstamp[min_net_load_ix], p_net_load[min_net_load_ix])
end


"""
    find_all_critical_days(tstamp::Vector{DateTime}, p_thermal::Vector{Float64}, p_load::Vector{Float64}, p_wind::Vector{Float64}, p_solar::Vector{Float64})

Find all critical days at once and return as a dictionary.

# Arguments
- `tstamp::Vector{DateTime}`: Vector of timestamps
- `p_thermal::Vector{Float64}`: Vector of thermal power generation values
- `p_load::Vector{Float64}`: Vector of load demand values
- `p_wind::Vector{Float64}`: Vector of wind generation values
- `p_solar::Vector{Float64}`: Vector of solar generation values

# Returns
- Dictionary with keys for each critical day type and values as named tuples (index, timestamp, value)
"""
function find_all_critical_days(tstamp::Vector{DateTime}, p_thermal::Vector{Float64}, p_load::Vector{Float64}, p_wind::Vector{Float64}, p_solar::Vector{Float64})
    @assert length(tstamp) == length(p_thermal) == length(p_load) == length(p_wind) == length(p_solar) "All vectors must have equal length"
    
    critical_days = Dict()
    
    # Min thermal output (excluding zero)
    ix, ts, val = find_min_thermal_output(tstamp, p_thermal; exclude_zero=true)
    critical_days["min_thermal"] = (index=ix, timestamp=ts, value=val)
    
    # Min load demand
    ix, ts, val = find_min_load_demand(tstamp, p_load)
    critical_days["min_load"] = (index=ix, timestamp=ts, value=val)
    
    # Max load demand
    ix, ts, val = find_max_load_demand(tstamp, p_load)
    critical_days["max_load"] = (index=ix, timestamp=ts, value=val)
    
    # Max thermal output
    ix, ts, val = find_max_thermal_output(tstamp, p_thermal)
    critical_days["max_thermal"] = (index=ix, timestamp=ts, value=val)
    
    # Max net load
    ix, ts, val = find_max_net_load(tstamp, p_load, p_wind, p_solar)
    critical_days["max_net_load"] = (index=ix, timestamp=ts, value=val)
    
    # Min net load
    ix, ts, val = find_min_net_load(tstamp, p_load, p_wind, p_solar)
    critical_days["min_net_load"] = (index=ix, timestamp=ts, value=val)
    
    return critical_days
end


"""
    print_critical_days_summary(critical_days_dict)

Print a formatted summary of critical days.

# Arguments
- `critical_days_dict`: Dictionary returned by find_all_critical_days()
"""
function print_critical_days_summary(critical_days_dict)
    println("\n" * "="^70)
    println("CRITICAL DAYS SUMMARY")
    println("="^70)
    
    for (key, data) in sort(collect(critical_days_dict))
        println("\n$(uppercase(replace(key, "_" => " "))):")
        println("  Index:     $(data.index)")
        println("  Timestamp: $(data.timestamp)")
        println("  Value:     $(round(data.value, digits=2)) MW")
    end
    
    println("\n" * "="^70)
end


# Example usage:

