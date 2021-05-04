from . import kubespray_validators

# Validators to be run in every start of a command run
context_validators = [kubespray_validators.validate]
