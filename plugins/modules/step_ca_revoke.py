#!/usr/bin/python

# Copyright: (c) 2021, Max Hösel <ansible@maxhoesel.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: step_ca_revoke
author: Max Hösel (@maxhoesel)
short_description: Revoke a Certificate
version_added: '0.3.0'
description: Revoke a Certificate
notes:
  - Check mode is supported.
options:
  cert:
    description: The path to the cert that should be revoked. Can be let empty if I(serial_number) is defined.
    type: path
  key:
    description: The path to the key corresponding to the cert that should be revoked. Can be let empty if I(serial_number) is defined.
    type: path
  reason:
    description: The string representing the reason for which the cert is being revoked.
    type: str
  reason_code:
    description: >
      The reasonCode specifies the reason for revocation - chose from a list of common revocation reasons.
      If unset, the default is Unspecified. See https://smallstep.com/docs/step-cli/reference/ca/revoke for more details
    type: int
  serial_number:
    description: >
      The serial number of the certificate that should be revoked.
      Can be left blank when using I(cert) and I(key) params for revocation over mTLS.
    type: int
  token:
    description: The one-time token used to authenticate with the CA in order to revoke the certificate.
    type: str
    ##no_log

extends_documentation_fragment:
  - maxhoesel.smallstep.step_cli
  - maxhoesel.smallstep.connection
"""

EXAMPLES = r"""
# See https://smallstep.com/docs/step-cli/reference/ca/revoke for more examples

- name: Revoke a local certificate
  maxhoesel.smallstep.step_ca_revoke:
    cert: internal.crt
    key: internal.key
    ca_url: https://ca.smallstep.com:9000

- name: Revoke a certificate via serial number
  maxhoesel.smallstep.step_ca_revoke:
    serial_number: 308893286343609293989051180431574390766
    ca_url: https://ca.smallstep.com:9000
    token: "{{ ca_token }}"
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils.step_cli_wrapper import CLIWrapper
from ..module_utils import connection


def run_module():
    module_args = dict(
        cert=dict(type="path"),
        key=dict(type="path"),
        reason=dict(type="str"),
        reason_code=dict(type="int"),
        serial_number=dict(type="int"),
        token=dict(type="str", no_log=True),
        step_cli_executable=dict(type="path", default="step-cli"),
    )
    result = dict(changed=False, stdout="", stderr="", msg="")
    module = AnsibleModule(argument_spec={**connection.args, **module_args}, supports_check_mode=True)

    connection.check_argspec(module, result)

    cli = CLIWrapper(module, result, module.params["step_cli_executable"])

    # Positional Parameters
    params = ["ca", "revoke"]
    if module.params["serial_number"]:
        params.append([module.params["serial_number"]])
    # Regular args
    args = ["cert", "key", "reason", "reason_code",
            "token"]
    # All parameters can be converted to a mapping by just appending -- and replacing the underscores
    args = {arg: f"--{arg.replace('_', '-')}" for arg in args}
    # This step-cli argument uses camelCase for some reason
    args["reason_code"] = "--reasonCode"

    result["stdout"], result["stderr"] = cli.run_command(params, {**args, **connection.param_spec})[1:3]
    result["changed"] = True
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
