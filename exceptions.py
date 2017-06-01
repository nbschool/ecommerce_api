"""
Custom exceptions to handle particular cases of our e-commerce API
"""


class InsufficientAvailabilityException(Exception):

    def __init__(self, item, requested_quantity):
        super(Exception, self).__init__(
            "Item availability {}, requested {}".format(
                item.availability,
                requested_quantity))

        self.item = item
        self.requested_quantity = requested_quantity


class WrongQuantity(Exception):
    pass


class SearchAttributeMismatch(Exception):
    """Raised when a model tries to call its ``search`` method but no
    fields to lookup are set, either as class attributes or at call time.
    """
    pass
