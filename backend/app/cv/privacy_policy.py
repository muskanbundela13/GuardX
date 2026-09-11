from privacy_config import (
    FACE_RECOGNITION_ENABLED,
    IDENTITY_TRACKING_ENABLED,
    TEMPORARY_TRACKING_IDS,
    ORIGINAL_EVIDENCE_ALLOWED,
    INVESTIGATION_REQUIRES_AUTHORIZATION,
    AUDIT_EVIDENCE_ACCESS
)


class PrivacyPolicy:

    def is_face_recognition_allowed(self):
        return FACE_RECOGNITION_ENABLED

    def is_identity_tracking_allowed(self):
        return IDENTITY_TRACKING_ENABLED

    def use_temporary_tracking_ids(self):
        return TEMPORARY_TRACKING_IDS

    def can_store_original_evidence(self):
        return ORIGINAL_EVIDENCE_ALLOWED

    def can_access_original_evidence(self, authorized):
        if not INVESTIGATION_REQUIRES_AUTHORIZATION:
            return True

        return authorized

    def should_audit_evidence_access(self):
        return AUDIT_EVIDENCE_ACCESS

    def validate(self):
        if FACE_RECOGNITION_ENABLED:
            return False

        if IDENTITY_TRACKING_ENABLED:
            return False

        if not TEMPORARY_TRACKING_IDS:
            return False

        if not ORIGINAL_EVIDENCE_ALLOWED:
            return False

        return True