from abc import ABCMeta, abstractmethod

from interfaces.ansible.kubespray_manager import KubesprayPatcher


class Validator(metaclass=ABCMeta):
    def __init__(self, context):
        self.context = context

    @abstractmethod
    def validate(self):
        """Run the specific validator implementation"""


class KubesprayPatchesValidator(Validator):

    def __init__(self, context):
        super().__init__(context)

    def validate(self):
        kubespray_content = self.context.kubespray_config.package_manager.get_content(reusable=True)
        KubesprayPatcher(kubespray_content, self.context.kubespray_config.patches).validate_patches()
