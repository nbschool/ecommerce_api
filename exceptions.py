
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
