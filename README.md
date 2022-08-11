![GitHub Badge Blue](https://user-images.githubusercontent.com/25454503/157903512-a9be0f7b-9255-4f88-9b00-9d50539dd901.svg)

# Pluralith Ansible Module

A dedicated Ansible module to run Pluralith

`Pluralith is currently in Alpha`

&nbsp;

## 📕 Get Started

Copy the below snippet as a starting point to run Pluralith with your Terraform + Ansible setup.
- Task 1 initializes Terraform and Pluralith
- Task 2 runs Pluralith and generates a diagram.

```yml
- name: Generate Pluralith Diagram
  hosts: localhost
  vars:
    variable_dict:
      var_1: "VALUE"
      var_2: "VALUE"
  tasks:
    - name: Init Terraform and Pluralith
      pluralith:
        command: "init" # See all available commands at https://docs.pluralith.com/docs/category/cli-commands
        api_key: "YOUR API KEY HERE"
        project_id: "YOUR PROJECT ID HERE" # Sign up and create a project at https://app.pluralith.com
        project_path: "YOUR PROJECT PATH HERE"
        init_tf: true
        tf_backend_config:
          region: “us-west-1"
          bucket: "test"
          key: "ansible_test"
          profile: "qa_env"
      register: command_result
    - name: Run Pluralith
      pluralith:
        command: "run" # See all available commands at https://docs.pluralith.com/docs/category/cli-commands
        project_path: "YOUR PROJECT PATH HERE"
        tf_vars: "{{ variable_dict }}"
      register: command_result
```
