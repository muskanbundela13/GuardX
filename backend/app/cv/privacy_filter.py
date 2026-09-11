class PrivacyFilter:

    def apply(self, frame, bounding_boxes=None):
        """
        Current GuardX privacy layer.

        GuardX does not perform face recognition or identity tracking.
        Original evidence is preserved for authorized investigation.
        """

        return frame