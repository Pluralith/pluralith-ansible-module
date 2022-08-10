#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: pluralith

short_description: An Ansible module to run Pluralith

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "0.0.1"

description: This is my longer description explaining my test module.

options:
    command:
        description: Select the Pluralith CLI command you would like to run
        required: true
        type: str
    # name:
    #     description: This is the message to send to the test module.
    #     required: true
    #     type: str
    # new:
    #     description:
    #         - Control to demo if the result of this module is changed or not.
    #         - Parameter description can be a list as well.
    #     required: false
    #     type: bool
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

# Run Pluralith and generate a diagram
- name: Generate a Pluralith diagram
  my_namespace.my_collection.pluralith:
    command: "run"
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

from ansible.module_utils.basic import AnsibleModule


def run_pluralith():
    # Define available arguments/parameters a user can pass to the module
    module_args = dict(
        command=dict(type="str", required=True),
        binary_path=dict(type="str", required=False),
        project_path=dict(type="str", required=True),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(changed=False, state=dict(), original_message="", message="")

    # Initialize Ansible module
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # Extract argument values
    command = module.params.get("command")
    project_path = module.params.get("project_path")

    if module.params.get("binary_path") is not None:
        binary_path = module.params.get("binary_path")
    else:
        bin_path = [module.get_bin_path("pluralith", required=True)][0]

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    result["original_message"] = module.params["command"]
    result["message"] = "goodbye"

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    if module.params["command"] == "init":
        result["state"] = {
            "init": True,
            "bin_path": bin_path,
            "project_path": project_path,
        }

    if module.params["command"] == "run":
        result["state"] = {
            "run": True,
            "bin_path": bin_path,
            "project_path": project_path,
        }

    executable = [bin_path, command]
    rc, out, err = module.run_command(executable, cwd=project_path)

    if rc == 0:
        # no changes
        result["output"] = out
        # return plan_path, False, out, err, plan_command if state == 'planned' else command
    elif rc == 1:
        # failure to plan
        result["output"] = out
        module.fail_json(msg='pluralith {1} failed\r\nSTDOUT: {1}\r\n\r\nSTDERR: {2}'.format(command, out, err))
    elif rc == 2:
        # changes, but successful
        result["output"] = out
        # return plan_path, True, out, err, plan_command if state == 'planned' else command
    

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
