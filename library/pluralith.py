#!/usr/bin/python

# Copyright: (c) 2022, Pluralith Core Team <dan@pluralith.com>
from __future__ import absolute_import, division, print_function
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

DOCUMENTATION = r"""
---
module: pluralith
version_added: "0.0.1"
short_description: An Ansible module to run Pluralith
description: This is my longer description explaining my test module.

options:
    command:
        description: Select the Pluralith CLI command you would like to run.
        required: true
        type: str
    api_key:
        description: Pluralith API key (found in the Pluralith dashboard).
        required: false
        type: str
    project_id:
        description: Pluralith project ID (found in the Pluralith dashboard).
        required: false
        type: str
    project_path:
        description: Path to the target Terraform project.
        required: true
        type: str
    tf_vars:
        description: A group of key-values to override template variables or those in variables files.
        required: false
        type: dict
    tf_var_files:
        description: The path to a variables file for Terraform to fill into the TF configurations. This can accept a list of paths to multiple variables files.
        required: false
        type: list
        elements: path
    tf_backend_config:
        description: A group of key-values to provide at init stage to the -backend-config parameter.
        required: false
        type: dict
    tf_backend_config_files:
        description: The path to a configuration file to provide at init state to the -backend-config parameter. This can accept a list of paths to multiple configuration files.
        required: false
        type: list
        elements: path

author:
    - Daniel Putzer (@DanThePutzer)
"""

EXAMPLES = r"""
# Initialize a Pluralith project
- name: Init Terraform and Pluralith
  my_namespace.my_collection.pluralith:
    command: "init" # See all available commands at https://docs.pluralith.com/docs/category/cli-commands
    api_key: "YOUR API KEY HERE"
    project_id: "YOUR PROJECT ID HERE" # Sign up and create a project at https://app.pluralith.com
    project_path: "YOUR PROJECT PATH HERE"
    init_tf: true
    tf_backend_config:
        region: "VALUE"
        bucket: "VALUE"
        key: "VALUE"
        profile: "VALUE"

# Run Pluralith and generate a diagram (both terraform and pluralith need to be initialized beforehand)
- name: Run Pluralith
  my_namespace.my_collection.pluralith:
    command: "run" # See all available commands at https://docs.pluralith.com/docs/category/cli-commands
    project_path: "YOUR PROJECT PATH HERE"
    tf_vars: "{{ variable_dict }}"
"""

RETURN = r"""
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: Pluralith module start message.
    type: str
    returned: always
message:
    description: Pluralith module complete message.
    type: str
    returned: always
command:
    description: Pluralith command that has been run
    type: str
    returned: always
state:
    description: Returns various outputs
    pluralith_output:
        description: Raw Pluralith CLI output for the command that has been run
        type: str
        returned: on success
    terraform_output:
        description: Raw Terraform output for the init command
        type: str
        returned: on success
"""

def run_pluralith():
    # Define available arguments/parameters a user can pass to the module
    module_args = dict(
        command=dict(type="str", required=True),
        api_key=dict(type="str", required=False),
        project_id=dict(type="str", required=False),
        project_path=dict(type="str", required=True),
        tf_vars=dict(type="dict", required=False, default={}),
        tf_var_files=dict(type="list", required=False, elements="path", default=[]),
        init_tf=dict(type="bool", required=False, default=False),
        tf_backend_config=dict(type="dict", required=False, default={}),
        tf_backend_config_files=dict(type="list", required=False, elements="path", default=[]),
    )

    # Construct result object
    result = dict(changed=False, state=dict(), original_message="", message="")

    # Initialize Ansible module
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # Extract argument values
    command = module.params.get("command")
    api_key = module.params.get("api_key")
    project_id = module.params.get("project_id")
    project_path = module.params.get("project_path")
    tf_vars = module.params.get('tf_vars')
    tf_var_files = module.params.get('tf_var_files')
    init_tf = module.params.get('init_tf')
    tf_backend_config = module.params.get('tf_backend_config')
    tf_backend_config_files = module.params.get('tf_backend_config_files')

    # Get binary paths
    pluralith_path = [module.get_bin_path("pluralith", required=True)][0]
    terraform_path = [module.get_bin_path("terraform", required=True)][0]

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    # if module.check_mode:
    #     module.exit_json(**result)

    # Manipulate or modify the state as needed
    result["original_message"] = "starting pluralith " + module.params["command"]
    result["message"] = "pluralith " + module.params["command"] + " completed"
    result["command"] = module.params["command"]

    # Initialize Terraform if applicable
    if (init_tf):
        # Construct Terraform init command
        executable = [terraform_path, "init", "-no-color"]
        executable += [f'-backend-config="{key}={val}"' for key, val in tf_backend_config.items()] # Construct backend config flags
        executable += [f'-backend-config={var_file}' for var_file in tf_backend_config_files] # Construct backend config file flags
        
        # Run Terraform init command
        rc, out, err = module.run_command(executable, cwd=project_path)
        if rc == 0: # success, no changes
            result["state"]["terraform_output"] = out
        elif rc == 1: # failure
            result["state"]["terraform_output"] = out
            module.fail_json(msg='terraform init failed\r\nSTDOUT: {1}\r\n\r\nSTDERR: {2}'.format(out, err))
        elif rc == 2: # success, with changes
            result["state"]["terraform_output"] = out

    # Construct Pluralith command
    executable = [pluralith_path, command]

    # Handle Pluralith init
    if command == "init":
        executable += [f'--api-key={api_key}']
        executable += [f'--project-id={project_id}']

    # Handle Pluralith graphing commands
    if command != "init":
        executable += [f'--var="{key}={val}"' for key, val in tf_vars.items()] # Construct variable flags
        executable += [f'--var-file={var_file}' for var_file in tf_var_files] # Construct variable file flags

    # Run Pluralith command
    rc, out, err = module.run_command(executable, cwd=project_path)
    if rc == 0: # success, no changes
        result["state"]["pluralith_output"] = out
    elif rc == 1: # failure
        result["state"]["pluralith_output"] = out
        module.fail_json(msg='pluralith {1} failed\r\nSTDOUT: {1}\r\n\r\nSTDERR: {2}'.format(command, out, err))
    elif rc == 2: # success, with changes
        result["state"]["outpluralith_output"] = out
    
    module.exit_json(**result)

def main():
    run_pluralith()

if __name__ == "__main__":
    main()
