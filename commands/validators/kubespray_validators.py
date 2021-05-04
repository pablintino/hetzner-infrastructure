from interfaces.ansible.kubespray_manager import KubesprayPatcher


def validate(run_context):
    kubespray_content = run_context.kubespray_config.package_manager.get_content(reusable=True)
    KubesprayPatcher(kubespray_content, run_context.kubespray_config.patches).validate_patches()
