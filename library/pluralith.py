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
    binary_path:
        description: Path to the current Pluralith binary.
        required: false
        type: str
    project_path:
        description: Path to the target Terraform project.
        required: true
        type: str
    terraform_vars:
        description: A group of key-values to override template variables or those in variables files.
        required: false
        type: dict
    terraform_var_files:
        description: The path to a variables file for Terraform to fill into the TF configurations. This can accept a list of paths to multiple variables files.
        required: false
        type: list
        elements: path
        aliases: [ 'variables_file' ]

# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - my_namespace.my_collection.my_doc_fragment_name

author:
    - Daniel Putzer (@DanThePutzer)
"""

EXAMPLES = r"""
# Initialize a Pluralith project
- name: Initialize a Pluralith project
  my_namespace.my_collection.pluralith:
    command: "init"
    project_path: "~/Code/Pluralith/test-architecture/aws/datalake/application"

# Run Pluralith and generate a diagram
- name: Generate a Pluralith diagram
  my_namespace.my_collection.pluralith:
    command: "run" # See all available commands here https://docs.pluralith.com/docs/category/cli-commands
    project_path: "~/Code/Pluralith/test-architecture/aws/datalake/application"
    terraform_vars: "{{ variable_dict }}"
"""

RETURN = r"""
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
"""

def run_pluralith():
    # Define available arguments/parameters a user can pass to the module
    module_args = dict(
        command=dict(type="str", required=True),
        binary_path=dict(type="str", required=False),
        project_path=dict(type="str", required=True),
        terraform_vars=dict(type="dict", required=False, default={}),
        terraform_var_files=dict(aliases=["variables_file"], type="list", elements="path", default=[]),
    )

    # Construct result object
    result = dict(changed=False, state=dict(), original_message="", message="")

    # Initialize Ansible module
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # Extract argument values
    command = module.params.get("command")
    project_path = module.params.get("project_path")
    terraform_vars = module.params.get('terraform_vars')
    terraform_var_files = module.params.get('terraform_var_files')

    if module.params.get("binary_path") is not None:
        bin_path = module.params.get("binary_path")
    else:
        bin_path = [module.get_bin_path("pluralith", required=True)][0]

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    # if module.check_mode:
    #     module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    result["original_message"] = "starting pluralith " + module.params["command"]
    result["message"] = "pluralith " + module.params["command"] + " completed"
    result["command"] = module.params["command"]
    result["state"] = {
        "bin_path": bin_path,
        "project_path": project_path,
        "terraform_vars": terraform_vars,
        "terraform_var_files": terraform_var_files,
    }

    executable = [bin_path, command]
    executable += [f'--var="{key}={val}"' for key, val in terraform_vars.items()] # Construct variable flags
    executable += [f'--var={var_file}' for var_file in terraform_var_files] # Construct variable file flags
    result["state"]["executable"] = executable

    rc, out, err = module.run_command(executable, cwd=project_path)
    if rc == 0: # success, no changes
        result["state"]["output"] = out
    elif rc == 1: # failure
        result["state"]["output"] = out
        module.fail_json(msg='pluralith {1} failed\r\nSTDOUT: {1}\r\n\r\nSTDERR: {2}'.format(command, out, err))
    elif rc == 2: # success, with changes
        result["state"]["output"] = out
    

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    # if module.params["name"] == "fail me":
    #     module.fail_json(msg="You requested this to fail", **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_pluralith()


if __name__ == "__main__":
    main()
