README - Run pipeline.py

Purpose
-------
This file contains minimal, exact instructions to run the `pipeline.py` script in the `data_pipeline` folder.

How to run
----------
1. Activate your conda env (if you created one):

   conda activate mlops

2. Run pipeline specifying the start date (pipeline will start at 00:00:00 of that date):

   cd data_pipeline
    python pipeline.py --start-date "2025-10-17"

3. Run pipeline for a specific hour

If you want the pipeline to start from a specific hour on a date (for example 08:00 on 2025-10-17), you can provide the start date-time string or a millisecond timestamp.

   cd data_pipeline
   python pipeline.py --start-date "2025-10-17 08:00:00"

Examples
```
# start from midnight of a day
python pipeline.py --start-date "2025-10-17"

# start from 08:00 on that day
python pipeline.py --start-date "2025-10-17 08:00:00"

