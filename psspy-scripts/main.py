"""
Main script to run PSS/E dynamic simulations
This is the entry point for running simulations
"""

from loguru import logger
from helpers import run_case_simulation

# Setup logging
logger.add("simulation.log", rotation="10 MB", level="INFO")


def main():
    """Main function to run simulations"""
    
    # Available cases (based on your case_data folder structure)
    available_cases = ["case_NRE", "case_RE"]
    
    # Available contingencies
    contingencies = [
        {
            "type": "line_fault",
            "description": "Line trip contingency (5-7)"
        },
        {
            "type": "gen_change", 
            "description": "Generator 2 power change (187.3 MW → 217 MW)"
        }
    ]
    
    # Configuration parameters
    channel_option = "All"          # or other options
    runtime = 20                    # simulation time in seconds
    
    logger.info("Starting PSS/E Dynamic Simulation Suite")
    
    # Run simulations for all contingencies and all cases
    for contingency in contingencies:
        logger.info(f"\n{'='*60}")
        logger.info(f"Running {contingency['description']}")
        logger.info(f"Contingency Type: {contingency['type']}")
        logger.info(f"{'='*60}")
        
        for case in available_cases:
            logger.info(f"Processing case: {case}")
            run_case_simulation(
                case_folder=case, 
                disturbance_type=contingency["type"], 
                channel_option=channel_option, 
                runtime=runtime
            )
        
        logger.info(f"Completed all cases for {contingency['description']}")
    
    logger.info("ALL SIMULATIONS COMPLETED!")

if __name__ == "__main__":
    main()