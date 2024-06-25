#!/bin/bash

# no SBATCH options for now

module purge

#FILES= no .zip file informed
LOGDIR=/home/filagile2024/LOGS/
#JVMARGS= no JVMARGS informed

#$JARFILE= no .jar file informed
#$ARGS=  ...
#$declare -A VARIABLE_ARG=  ...

for file in $FILES
do
  #if grep -q "" $file; then

    echo "Processing $file file..."
    name="$(basename -- $file)"

    srun -n1 -N1 java $JVMARGS -jar $JARFILE1 $file $ARGS1 > $LOGDIR/${name%%.*}1.$option.out &

  #fi
done

wait
zip -jr $SLURM_JOB_NAME-$SLURM_JOB_ID.zip $LOGDIR