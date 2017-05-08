
class InsufficientAvailabilityException(Exception):

    def __init__(self, item, requested_quantity):
        super(Exception, self).__init__(
            "Item availability {}, requested {}".format(
                item.availability,
                requested_quantity))

        self.item = item
        self.requested_quantity = requested_quantity


class ItemAlreadyUserFavoritesException(Exception):
    def __init__(self, item, user):
        super(Exception, self).__init__(
            "User {} had already item {} in favorites".format(user, item))
