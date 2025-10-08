"""
PSS/E Simulation Functions
Contains all the utility functions for running dynamic simulations
"""

from __future__ import with_statement
from contextlib import contextmanager
import sys
import io
import re
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from loguru import logger

# Configure Plotly to use kaleido for static image export
pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 1000
pio.kaleido.scope.default_height = 600

# PSS/E imports
# sys.path.append("C:/Program Files/PTI/PSSE35/35.3/PSSBIN")
# sys.path.append("C:/Program Files/PTI/PSSE35/35.3/PSSPY39")

# import psse3503 # noqa
# import psspy    # type: ignore # noqa
# import redirect # type: ignore # noqa
# import dyntools # type: ignore # noqa
# from psspy import _i # type: ignore  # noqa: E402
# from psspy import _f # type: ignore  # noqa: E402

sys.path.append("C:/Program Files/PTI/PSSE36/36.1/PSSBIN")
sys.path.append("C:/Program Files/PTI/PSSE36/36.1/PSSPY311")

import psse3601  # type: ignore
import psspy     # type: ignore
import redirect  # type: ignore
import dyntools  # type: ignore
from psspy import _i # type: ignore  # noqa: E402
from psspy import _f # type: ignore  # noqa: E402

# Initialize PSS/E
redirect.psse2py()
psspy.psseinit()


@contextmanager
def silence(file_object=None):
    """
    Used to silence some of PSSE output without automatically silencing all output.
    Discard stdout (i.e. write to null device) or optionally write to given file-like object.
    """
    if file_object is None:
        file_object = open(os.devnull, 'w')

    old_stdout = sys.stdout
    try:
        sys.stdout = file_object
        yield
    finally:
        sys.stdout = old_stdout


def convert_raw_to_sav(case_folder, raw_file):
    """Convert .raw file to .sav file if .sav doesn't exist"""
    base_path = f"case_data/{case_folder}"
    raw_path = f"{base_path}/{raw_file}"
    sav_file = raw_file.replace('.raw', '.sav')
    sav_path = f"{base_path}/{sav_file}"
    
    logger.info(f"Converting {raw_file} to {sav_file}...")
    
    try:
        # Initialize PSS/E if not already done
        _ = psspy.psseinit(200000)
        
        # Load the .raw file
        _ = psspy.read(0, raw_path)
        
        # Save as .sav file
        _ = psspy.save(sav_path)
        
        logger.success(f"Successfully converted {raw_file} to {sav_file}")
        return sav_file
        
    except Exception as e:
        logger.error(f"Error converting {raw_file} to .sav: {str(e)}")
        return None


def create_output_folder(contingency_name, case_folder):
    """Create output folder for the contingency and case if it doesn't exist"""
    output_path = f"results/{contingency_name}/{case_folder}"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        logger.info(f"Created output folder: {output_path}")
    return output_path


def get_contingency_name(case_folder, disturbance_type):
    """Get the contingency name based on case and disturbance type"""
    if disturbance_type == "line_fault":
        if case_folder == "case_SAVNW":
            return "line_fault_154-3008"
        elif case_folder == "case_NRE":
            return "line_trip_5-7"
        elif case_folder == "case_RE":
            return "line_trip_5-7"
    elif disturbance_type == "bus_fault":
        return f"bus_fault_{disturbance_type}"
    elif disturbance_type == "gen_change":
        return "gen2_power_change_187-217MW"
    
    return "unknown_contingency"


def get_case_files(case_folder):
    """Get the appropriate files for the selected case"""
    base_path = f"case_data/{case_folder}"
    
    # Find .sav or .raw file
    sav_file = None
    raw_file = None
    dyr_file = None
    
    for file in os.listdir(base_path):
        if file.endswith('.sav'):
            sav_file = file
        elif file.endswith('.raw'):
            raw_file = file
        elif file.endswith('.dyr'):
            dyr_file = file
    
    # If no .sav file but .raw file exists, convert it
    if sav_file is None and raw_file is not None:
        sav_file = convert_raw_to_sav(case_folder, raw_file)
        # If conversion failed, use the raw file directly
        if sav_file is None:
            sav_file = raw_file
    
    return sav_file, dyr_file


def sort_results(d, e, z):
    """Sort simulation results by channel type"""
    POWR = []
    POWR_index = 1
    FREQ = []
    FREQ_index = 1
    VOLT = []
    VOLT_index = 1 
    SPEED = []
    SPEED_index = 1
    
    # Sort by channel type
    for channel in range(1, len(e)):
        channel_keys = re.split(' |\[|\]', e[channel])
        if channel_keys[0] == 'POWR':
            if len(POWR) == 0:
                POWR = pd.DataFrame(z[channel], columns=[f'GEN_BUS{channel_keys[1]}'], index=z['time'])
            else:
                POWR.insert(POWR_index, f'GEN_BUS{channel_keys[1]}', z[channel], allow_duplicates=True)
                POWR_index = POWR_index + 1
        elif channel_keys[0] == 'FREQ':
            if len(FREQ) == 0:
                # Convert frequency deviation to absolute frequency by adding 1.0
                freq_data = np.array(z[channel]) + 1.0
                FREQ = pd.DataFrame(freq_data, columns=[f'BUS{channel_keys[1]}'], index=z['time'])
            else:            
                # Convert frequency deviation to absolute frequency by adding 1.0
                freq_data = np.array(z[channel]) + 1.0
                FREQ.insert(FREQ_index, f'BUS{channel_keys[1]}', freq_data, allow_duplicates=True)
                FREQ_index = FREQ_index + 1    
        elif channel_keys[0] == 'VOLT':
            if len(VOLT) == 0:
                VOLT = pd.DataFrame(z[channel], columns=[f'BUS{channel_keys[1]}'], index=z['time'])
            else:    
                VOLT.insert(VOLT_index, f'BUS{channel_keys[1]}', z[channel], allow_duplicates=True)
                VOLT_index = VOLT_index + 1
        elif channel_keys[0] == 'SPD':
            if len(SPEED) == 0:
                # Convert speed deviation to absolute speed by adding 1.0
                speed_data = np.array(z[channel]) + 1.0
                SPEED = pd.DataFrame(speed_data, columns=[f'GEN_BUS{channel_keys[1]}'], index=z['time'])
            else:    
                # Convert speed deviation to absolute speed by adding 1.0
                speed_data = np.array(z[channel]) + 1.0
                SPEED.insert(SPEED_index, f'GEN_BUS{channel_keys[1]}', speed_data, allow_duplicates=True)
                SPEED_index = SPEED_index + 1

    # Sort DataFrames by Column (only if they contain data)
    if isinstance(POWR, pd.DataFrame):
        POWR = POWR.sort_index(axis=1)
    if isinstance(FREQ, pd.DataFrame):
        FREQ = FREQ.sort_index(axis=1)
    if isinstance(VOLT, pd.DataFrame):
        VOLT = VOLT.sort_index(axis=1)
    if isinstance(SPEED, pd.DataFrame):
        SPEED = SPEED.sort_index(axis=1)
    else:
        SPEED = pd.DataFrame()

    return POWR, FREQ, VOLT, SPEED


def create_plotly_config_figure(data, title, ylabel, colors, label_prefix, left_limit, right_limit, custom_yticks=None):
    """Create a Plotly figure with common formatting"""
    fig = go.Figure()
    
    for i, col in enumerate(data.columns):
        color = colors[i % len(colors)]
        
        # Extract the actual bus/gen number from column name
        if 'GEN_BUS' in col:
            display_name = f"PSSE: {col}"  # Shows as "PSSE: GEN_BUS1"
        elif 'BUS' in col:
            display_name = f"PSSE: {col}"  # Shows as "PSSE: BUS1"
        else:
            display_name = f"{label_prefix}{col}"
            
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data[col],
            mode='lines',
            name=display_name,
            line=dict(color=color, width=2)
        ))
    
    # Update layout
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=16)),
        xaxis=dict(
            title='Time (s)',
            range=[left_limit, right_limit],
            tickvals=[0, 5, 10, 15, 20],
            gridcolor='rgba(128, 128, 128, 0.3)',
            showgrid=True
        ),
        yaxis=dict(
            title=ylabel,
            gridcolor='rgba(128, 128, 128, 0.3)',
            showgrid=True
        ),
        legend=dict(
            x=1.02,
            y=1,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='rgba(0, 0, 0, 0.3)',
            borderwidth=1
        ),
        plot_bgcolor='white',
        width=1000,
        height=600,
        margin=dict(r=150)
    )
    
    # Set custom y-axis ticks if provided
    if custom_yticks:
        fig.update_yaxes(tickvals=custom_yticks)
    
    return fig


def plot_results(contingency_name, case_folder, plot_file, POWR, FREQ, VOLT, SPEED, excel_file, left_limit, right_limit):
    """Generate plots and save data for simulation results using Plotly"""
    output_path = f"results/{contingency_name}/{case_folder}"
    
    png_POWR = f"{output_path}/POWR_{plot_file}"
    png_FREQ = f"{output_path}/FREQ_{plot_file}"
    png_VOLT = f"{output_path}/VOLT_{plot_file}"
    png_SPEED = f"{output_path}/SPEED_{plot_file}"

    # Create CSV file names
    csv_base = excel_file.replace('.xlsx', '')
    csv_POWR = f"{output_path}/{csv_base}_POWR.csv"     # Plot power
    csv_FREQ = f"{output_path}/{csv_base}_FREQ.csv"     # Plot frequency
    csv_VOLT = f"{output_path}/{csv_base}_VOLT.csv"     # Plot bus voltage
    csv_SPEED = f"{output_path}/{csv_base}_SPEED.csv"   # Plot speed

    # Define color schemes
    default_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22']
    bus_colors = ['blue', 'red', 'green', 'purple', 'orange', 'cyan', 'brown', 'lightgreen', 'pink']
    gen_colors = ['blue', 'green', 'red']

    # Plot POWR
    if not POWR.empty:
        fig = create_plotly_config_figure(
            POWR, 
            'Generator Power after Line 5-7 Trip', 
            'MW', 
            gen_colors, 
            'PSSE:GEN', 
            left_limit, 
            right_limit
        )
        fig.write_image(png_POWR, format='png', engine='kaleido')
        logger.info(f"Power plot saved: {png_POWR}")
    
    # Plot FREQ
    if not FREQ.empty:
        fig = create_plotly_config_figure(
            FREQ, 
            'Bus Frequency after Line 5-7 Trip', 
            'Frequency (p.u.)', 
            default_colors, 
            'PSSE: BUS', 
            left_limit, 
            right_limit
        )
        fig.write_image(png_FREQ, format='png', engine='kaleido')
        logger.info(f"Frequency plot saved: {png_FREQ}")
    
    # Plot VOLT
    if not VOLT.empty:
        fig = create_plotly_config_figure(
            VOLT, 
            'Bus Voltage Magnitude after Line 5-7 Trip', 
            'Voltage magnitude (p.u.)', 
            bus_colors, 
            'PSSE: BUS', 
            left_limit, 
            right_limit
        )
        fig.write_image(png_VOLT, format='png', engine='kaleido')
        logger.info(f"Voltage plot saved: {png_VOLT}")
    
    # Plot SPEED only if data exists
    if not SPEED.empty:
        fig = create_plotly_config_figure(
            SPEED, 
            'Generator Speed after Line 5-7 Trip', 
            'Speed (p.u.)', 
            gen_colors, 
            'PSSE: GEN', 
            left_limit, 
            right_limit
        )
        
        # Auto-scale y-axis for speed data instead of fixed ticks
        # This eliminates the hard-coded yticks problem
        fig.update_yaxes(autorange=True)
        
        fig.write_image(png_SPEED, format='png', engine='kaleido')
        logger.info(f"Speed plot saved: {png_SPEED}")
    else:
        logger.warning("No speed data available to plot")

    # Save Data to separate CSV files with proper headers
    if not POWR.empty:
        # Reset index to make TIME a column, then rename it
        powr_csv = POWR.reset_index()
        powr_csv.rename(columns={'index': 'TIME'}, inplace=True)
        powr_csv.to_csv(csv_POWR, index=False)
        logger.info(f"Power CSV file saved: {csv_POWR}")
    
    if not FREQ.empty:
        # Reset index to make TIME a column, then rename it
        freq_csv = FREQ.reset_index()
        freq_csv.rename(columns={'index': 'TIME'}, inplace=True)
        freq_csv.to_csv(csv_FREQ, index=False)
        logger.info(f"Frequency CSV file saved: {csv_FREQ}")
    
    if not VOLT.empty:
        # Reset index to make TIME a column, then rename it
        volt_csv = VOLT.reset_index()
        volt_csv.rename(columns={'index': 'TIME'}, inplace=True)
        volt_csv.to_csv(csv_VOLT, index=False)
        logger.info(f"Voltage CSV file saved: {csv_VOLT}")
    
    if not SPEED.empty:
        # Reset index to make TIME a column, then rename it
        speed_csv = SPEED.reset_index()
        speed_csv.rename(columns={'index': 'TIME'}, inplace=True)
        speed_csv.to_csv(csv_SPEED, index=False)
        logger.info(f"Speed CSV file saved: {csv_SPEED}")


def run_psse_simulation(contingency_name, case_folder, sav_file, dyr_file, out_file, disturbance_type, channel_option, runtime):
    """Run the actual PSS/E dynamic simulation"""
    base_path = f"case_data/{case_folder}"
    sav = f"{base_path}/{sav_file}"
    out = f"results/{contingency_name}/{case_folder}/{out_file}"
    
    ierr = [1] * 30  # check and record for error codes
    output = io.StringIO()
    
    with silence(output):    
        # Initialize PSS/E
        ierr[0] = psspy.psseinit(200000) 
        ierr[1] = psspy.case(sav)  # load case information (.sav file)
        
        # Power flow solution
        ierr[3] = psspy.fnsl([0, 0, 0, 1, 1, 0, 99, 0]) 
        ierr[4] = psspy.cong(0)
        
        # Convert loads to constant impedance
        ierr[5] = psspy.conl(1, 1, 1, [0, 0], [0.0, 100.0, 0.0, 100.0])
        ierr[6] = psspy.conl(1, 1, 2, [0, 0], [0.0, 100.0, 0.0, 100.0])
        ierr[7] = psspy.conl(1, 1, 3, [0, 0], [0.0, 100.0, 0.0, 100.0])
        ierr[8] = psspy.ordr(1)
        ierr[9] = psspy.fact()
        ierr[10] = psspy.tysl(0)
        
        # Load dynamics data
        if dyr_file is not None:
            dyre = f"{base_path}/{dyr_file}"
            ierr[11] = psspy.dyre_new([1, 1, 1, 1], dyre, "", "", "")
            
        # Setup channels
        ierr[12] = psspy.delete_all_plot_channels()
        
        if channel_option == 'All':
            ierr[12] = psspy.chsb(0, 1, [-1, -1, -1, 1, 2, 0])   # Machine electrical power
            ierr[13] = psspy.chsb(0, 1, [-1, -1, -1, 1, 12, 0])  # Bus Frequency Deviations
            ierr[14] = psspy.chsb(0, 1, [-1, -1, -1, 1, 13, 0])  # Bus Voltage and angle
            ierr[15] = psspy.chsb(0, 1, [-1, -1, -1, 1, 7, 0])   # Machine speed
            
        # Start simulation
        ierr[21] = psspy.strt_2([0, 1], out)
        ierr[22] = psspy.run(0, 1.0, 1, 1, 1)  # Run for 1 second steady state
        
        # Apply disturbance
        if disturbance_type == "line_fault":
            if case_folder == "case_SAVNW":
                ierr[23] = psspy.dist_branch_fault(154, 3008, r"""1""", 1, 230.0, [0.0, -0.2E+10])
            elif case_folder == "case_NRE":
                ierr[23] = psspy.dist_branch_trip(5, 7, r"""1""")
            elif case_folder == "case_RE":
                ierr[23] = psspy.dist_branch_trip(5, 7, r"""1""")

            ierr[24] = psspy.change_channel_out_file(out)
            ierr[25] = psspy.run(0, 1.17, 1, 1, 1)  # run for 10 cycles
            ierr[26] = psspy.dist_clear_fault(1)  # clears fault
            
        elif disturbance_type == "gen_change":
            # Apply generator power change at t=1s
            # Find generator 2 bus number (you'll need to identify this from your case)
            gen_bus = None
            if case_folder == "case_NRE":
                gen_bus = 2  # Replace with actual bus number for generator 2
            elif case_folder == "case_RE":
                gen_bus = 2  # Replace with actual bus number for generator 2
            if gen_bus:
                ierr[23] = psspy.change_channel_out_file(out)
                # Change generator power from 187.3 MW to 217 MW
                # Only change PG (first parameter), all others use defaults (_f)
                ierr[24] = psspy.machine_chng_2(gen_bus, r"""1""", [_i,_i,_i,_i,_i,_i], 
                                               [217.0,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])
                logger.debug(f"Changed generator at bus {gen_bus} from 187.3 MW to 217.0 MW")
            else:
                logger.error(f"Generator bus not defined for case {case_folder}")
        
            
        # Continue simulation
        ierr[27] = psspy.change_channel_out_file(out)
        ierr[28] = psspy.run(0, runtime, 1, 1, 1)
        ierr[29] = psspy.delete_all_plot_channels()
        
    # Check for errors
    run_output = output.getvalue()
    current_error = 0
    if "Network not converged" in run_output:
        logger.error('Network not converged') 
        current_error = 1
    elif "NaN" in run_output:
        logger.error("NaN, network is no good")
        current_error = 1
    if current_error == 0 and "INITIAL CONDITIONS CHECK O.K." in run_output:
        logger.success("Network converged. No errors and initial conditions were good.")
     
    # Gather the data
    data = dyntools.CHNF(out)
    d, e, z = data.get_data()
    
    return d, e, z


def run_case_simulation(case_folder, disturbance_type="line_fault", channel_option="All", runtime=20):
    """Run simulation for a specific case folder"""
    logger.info(f"Running simulation for case: {case_folder}")
    
    # Get contingency name
    contingency_name = get_contingency_name(case_folder, disturbance_type)
    logger.info(f"Contingency: {contingency_name}")
    
    # Create output folder for this contingency and case (swapped order)
    create_output_folder(contingency_name, case_folder)
    
    # Get case files
    sav_file, dyr_file = get_case_files(case_folder)
    
    if sav_file is None:
        logger.error(f"No .sav or .raw file found in {case_folder}")
        return
    
    logger.info(f"Using files: {sav_file}, {dyr_file}")
    
    # Set simulation parameters
    left_limit = 0
    right_limit = runtime
    
    # Generate file names
    case_name = f"{case_folder}_{disturbance_type}_{channel_option}_{runtime}s"
    plot_file = f"{case_name}.png"
    excel_file = f"{case_name}.xlsx"
    out_file = f"{case_name}.outx"
    
    try:
        # Run simulation
        import time
        t0 = time.time()
        d, e, z = run_psse_simulation(contingency_name, case_folder, sav_file, dyr_file, out_file, disturbance_type, channel_option, runtime)
        
        # Process results
        POWR, FREQ, VOLT, SPEED = sort_results(d, e, z)
        
        # Create plots and save data (swapped parameter order)
        plot_results(contingency_name, case_folder, plot_file, POWR, FREQ, VOLT, SPEED, excel_file, left_limit, right_limit)
        
        t1 = time.time()
        logger.success(f"Simulation completed in {t1-t0:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Error running simulation for {case_folder}: {str(e)}")