#!/bin/bash
# environment variables for CPCReady projects
export CPCREADY_PROJECT=$($CPCREADY_DIR/opt/yq_cpc e '.project' $CPCREADY_PROJECT_CONFIG)
export CPCREADY_AUTHOR=$($CPCREADY_DIR/opt/yq_cpc e '.author' $CPCREADY_PROJECT_CONFIG)
export CPCREADY_CPCMODEL=$($CPCREADY_DIR/opt/yq_cpc e '.cpc_model' $CPCREADY_PROJECT_CONFIG)
export CPCREADY_DRIVE_A=$($CPCREADY_DIR/opt/yq_cpc e '.drive_a' $CPCREADY_PROJECT_CONFIG)
export CPCREADY_DRIVE_B=$($CPCREADY_DIR/opt/yq_cpc e '.drive_b' $CPCREADY_PROJECT_CONFIG)
export CPCREADY_DRIVE_SELECT=$($CPCREADY_DIR/opt/yq_cpc e '.drive_select' $CPCREADY_PROJECT_CONFIG)
export CPCREADY_STORAGE_SELECT=$($CPCREADY_DIR/opt/yq_cpc e '.storage_select' $CPCREADY_PROJECT_CONFIG)