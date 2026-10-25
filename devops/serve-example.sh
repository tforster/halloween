#!/usr/bin/env bash
####################################################################################################################################
# serve.sh: Serve the app locally in development mode with debugging support.
#
# Usage:    devops/serve.sh [--refresh-oracle] [--stop]
#
# Options:
#   --refresh-oracle    Remove Oracle volume to force fresh database initialization and data import
#   --stop              Stop the currently running stack
#
####################################################################################################################################

# Exit immediately if a command exits with a non-zero status
set -o errexit
# Treat unset variables as an error when substituting
set -o nounset
# Fails entire pipeline if any command fails
set -euo pipefail
trap 'echo "Exit status $? at line $LINENO from: $BASH_COMMAND"' ERR

# Include the parseArgs function
source ./devops/includes/parseArgs.sh

###
# @description One-time initialisation including composer install and copying db snapshot files
# @returns {void}
###
function init() {
  echo "Initializing the stack with database import from folder: $db_folder"
  # Down the stack if it is already running and remove any named volumes
  docker compose -f devops/docker/docker-compose.yml down -v

  # Copy files from S3 to the local dev filesystem workspaces/cpe.web/sql/Database_Snapshot/{db_folder}
  devops/s32rds.sh --copy --environment dev --folder $db_folder

  # Up the web container only
  docker compose -f devops/docker/docker-compose.yml up web -d

  # Use the web instance to run composer install
  docker exec cpe-web-1 /bin/bash -c "cd /var/www/html && composer install"

  # Import the data. This will up the Oracle container
  importData
}

###
# @description Imports the data from workspaces/cpe.web/sql/Database_Snapshot/dev
# @returns {void}
###
function importData() {
  echo "Importing data into Oracle from folder: $db_folder"
  # Down the stack if it is already running
  # docker compose -f devops/docker/docker-compose.yml down
  # Remove any previous Oracle data
  docker volume rm cpe_oracle_data || echo "Volume cpe_oracle_data not found (this is OK if first run)"
  # Up the Oracle container
  docker compose -f devops/docker/docker-compose.yml up oracle -d

  # Wait for the Oracle container to be ready
  while ! docker exec cpe-oracle-1 sqlplus -s "sys/password@//localhost/xepdb1 as sysdba" <<<"SELECT 1 FROM dual;" >/dev/null 2>&1; do
    echo "Waiting for Oracle readiness..."
    sleep 5
  done

  # # Additional wait to ensure all services are fully registered
  # echo "Waiting for Oracle services to be fully registered..."
  # sleep 10

  # Verify that LOCAL_DUMP_DIR directory object exists
  echo "Verifying LOCAL_DUMP_DIR directory object..."
  while ! docker exec cpe-oracle-1 bash -c 'echo "SELECT directory_name FROM dba_directories WHERE directory_name = '\''LOCAL_DUMP_DIR'\'';" | sqlplus -s "sys/password@//localhost/xepdb1 as sysdba"' | grep -q "LOCAL_DUMP_DIR"; do
    echo "Waiting for LOCAL_DUMP_DIR directory object to be created..."
    sleep 5
  done
  echo "LOCAL_DUMP_DIR directory object verified!"

  # Grant 755 so that the Oracle Data Pump can write the log file to the directory
  docker exec -u root cpe-oracle-1 chown -R oracle:oinstall /opt/oracle/admin/XE/dpdump/
  docker exec -u root cpe-oracle-1 chmod 755 /opt/oracle/admin/XE/dpdump/

  # Create the parameter file with proper permissions
  #   docker exec -u root cpe-oracle-1 bash -c "cat > /tmp/importDev_with_userid.par << 'EOF'
  # USERID=\"sys/password@//localhost/xepdb1 as sysdba\"
  # DUMPFILE=expdp_agtwebdv_20250702_%U.dmp
  # DIRECTORY=LOCAL_DUMP_DIR
  # SCHEMAS=INTEGRATION_CPE
  # LOGFILE=importDev.log
  # CONTENT=ALL
  # TABLE_EXISTS_ACTION=REPLACE
  # TRANSFORM=oid:n
  # EOF"

  # Ensure the parameter file is owned by oracle and readable
  docker exec -u root cpe-oracle-1 chown -R oracle:oinstall /opt/oracle/admin/XE/dpdump
  docker exec -u root cpe-oracle-1 chmod 755 /opt/oracle/admin/XE/dpdump
  docker exec -u root cpe-oracle-1 chmod 777 /tmp

  echo "Running Oracle Data Pump import..."
  if docker exec cpe-oracle-1 impdp parfile=/tmp/importDev.par; then

    echo "✅ Data import completed successfully!"
  else
    echo "⚠️ Data import completed with some errors (this is often normal for large imports)"
  fi

  # Verify the import worked by checking table count
  echo "Verifying import..."
  TABLE_COUNT=$(docker exec cpe-oracle-1 bash -c "echo 'SELECT COUNT(*) FROM user_tables;' | sqlplus -s INTEGRATION_CPE/password@//localhost/xepdb1" 2>/dev/null | grep -o '[0-9]\+' || echo "0")
  echo "📊 Imported ${TABLE_COUNT} tables into INTEGRATION_CPE schema"

  echo "Data import complete! Starting remaining services..."
  docker compose -f devops/docker/docker-compose.yml up -d
  exit 0
}

# Usage docstring that is parsed by the parseArgs function. Edit with care.
USAGE="

Usage: serve.sh --environment = [ dev | stage | prod ] [--with-aws]

Options:
  --environment=dev     The environment environment variable to set when starting the container
  --init                Initialize the stack (databases, etc.) - only needed on first run
  --db-folder=2025-09-09           The folder in workspaces/cpe.web/sql/Database_Snapshot to use for the database import (e.g., 20250702)
  --stop                Stop the currently running stack
  --refresh-oracle      Remove Oracle volume to force database re-initialization and data import
  --verbose             Enable verbose output and show detailed error messages
  --help                Help
"

# Parse the command line arguments
parseArgs "$USAGE" "$@"

if [[ "${environment:-dev}" != "dev" ]]; then
  echo "This script only works with dev. Stage and prod are handled by GitHub Actions and AWS."
  exit 1
else
  if [[ "$stop" == "true" ]]; then
    echo "Stopping the currently running stack."
    docker compose -f devops/docker/docker-compose.yml down
    exit 0
  fi

  if [[ "$init" == "true" ]]; then
    if [[ "${db_folder}" == false ]]; then
      echo "Please specify a database folder with --db-folder"
      exit 1
    fi
    # Init will start the stack
    init
  else
    # Start the stack
    docker compose -f devops/docker/docker-compose.yml up
  fi

  if [[ "$refresh_oracle" == "true" ]]; then
    importData
  fi
fi
