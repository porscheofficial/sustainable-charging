#!/bin/bash
#SBATCH --account=demelo   # Set account of De Melo’s chair
#SBATCH --job-name=varima_training       # Job name
#SBATCH --mail-user=nick.bessin@student.hpi.de # Address that should receive notifications
#SBATCH --mail-type=END     # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --partition=magic
#SBATCH --time=03:30:00           # Time limit hrs:min:sec
#SBATCH --mem=32G
#SBTACH -c 2
#SBATCH --output=output_%j.log     # Standard output log
#SBATCH --error=error_%j.log      # Standard error log

eval "$(conda shell.bash hook)"
conda activate aip-porsche

export PYTHONPATH="/hpi/fs00/home/nick.bessin/hpi-porsche-challenge"
export LD_LIBRARY_PATH="/hpi/fs00/home/nick.bessin/miniconda3/envs/aip-porsche/lib"

cd /hpi/fs00/home/nick.bessin/hpi-porsche-challenge/experiments

echo "Running VARIMA model"

python varima_cluster.py